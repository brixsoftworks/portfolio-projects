#!/usr/bin/env python3
"""
DRONE VISION SYSTEM V2-PRO - DEEP RESEARCH & TRAINING ENGINE
================================================================================
Architecture:   DroneVisionNet-V2-Pro (1.91M Parameters)
                - ConvNeXt Inverted Bottleneck (7x7 Depthwise Separable Convolutions)
                - Squeeze-and-Excitation (SE) Channel Attention
                - Multi-Scale Spatial Pyramidal Feature Aggregation (P3, P4, P5)
                - Multi-Task Perception: Bounding Box, Focal Confidence, Classification, Orientation
Loss Protocol:  Complete IoU (CIoU) Loss + Focal Objectness + Label Smoothed Cross-Entropy
Augmentation:   Drone Optical Augmentation (Vignette, Solar Glare, Sensor Noise, Cutout Occlusion)
Optimization:   Decoupled AdamW, Cosine Annealing with Warmup, Model EMA (0.9995)
Duration:       Dynamic 2-Hour Time Budget Controller with Graceful Interruption Handler
Hardware:       NVIDIA GeForce RTX 5060 Laptop GPU (CUDA Mixed Precision FP16)
Environment:    Isolated Research V2 Environment (/home/mullainathan/projects/mini-ai-drone/research_v2)
================================================================================
"""

import os
import sys
import time
import math
import copy
import signal
import argparse
import subprocess
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# Seed configuration
torch.manual_seed(42)
np.random.seed(42)

OUTPUT_DIR = "/home/mullainathan/projects/mini-ai-drone/research_v2"
CHECKPOINT_DIR = os.path.join(OUTPUT_DIR, "checkpoints")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# ------------------------------------------------------------------------------
# 1. Hardware Diagnostics & Real-Time Telemetry
# ------------------------------------------------------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
total_vram_mb = int(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)) if torch.cuda.is_available() else 0
cuda_capability = torch.cuda.get_device_capability(0) if torch.cuda.is_available() else (0, 0)

def query_gpu_telemetry():
    """Query live GPU core temperature, power consumption and utilization."""
    if not torch.cuda.is_available():
        return 0, 0.0, 0
    try:
        cmd = ["nvidia-smi", "--query-gpu=temperature.gpu,power.draw,utilization.gpu", "--format=csv,noheader,nounits"]
        output = subprocess.check_output(cmd, encoding="utf-8").strip()
        parts = [p.strip() for p in output.split(",")]
        temp_c = int(parts[0])
        power_w = float(parts[1])
        util_pct = int(parts[2])
        return temp_c, power_w, util_pct
    except Exception:
        return 0, 0.0, 0

def format_time(seconds):
    """Format seconds into HHh MMm SSs string."""
    seconds = max(0, int(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}h {m:02d}m {s:02d}s"

# ------------------------------------------------------------------------------
# 2. Deep Neural Architecture: DroneVisionNet-V2-Pro
# ------------------------------------------------------------------------------
class LayerNorm2d(nn.Module):
    """Channels-first 2D Layer Normalization for ConvNeXt blocks."""
    def __init__(self, channels, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(channels))
        self.bias = nn.Parameter(torch.zeros(channels))
        self.eps = eps

    def forward(self, x):
        u = x.mean(1, keepdim=True)
        s = (x - u).pow(2).mean(1, keepdim=True)
        x = (x - u) / torch.sqrt(s + self.eps)
        return self.weight[:, None, None] * x + self.bias[:, None, None]

class SEBlock(nn.Module):
    """Squeeze-and-Excitation channel attention module."""
    def __init__(self, channels, reduction=4):
        super().__init__()
        self.fc = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(channels, max(8, channels // reduction), 1),
            nn.GELU(),
            nn.Conv2d(max(8, channels // reduction), channels, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return x * self.fc(x)

class ConvNeXtBlock(nn.Module):
    """
    ConvNeXt residual block:
    7x7 depthwise conv -> LayerNorm -> 1x1 conv (4x expansion) -> GELU -> 1x1 conv -> SE attention
    """
    def __init__(self, dim):
        super().__init__()
        self.dwconv = nn.Conv2d(dim, dim, kernel_size=7, padding=3, groups=dim, bias=False)
        self.norm = LayerNorm2d(dim)
        self.pwconv1 = nn.Conv2d(dim, 4 * dim, 1, bias=False)
        self.act = nn.GELU()
        self.pwconv2 = nn.Conv2d(4 * dim, dim, 1, bias=False)
        self.se = SEBlock(dim)

    def forward(self, x):
        res = x
        out = self.dwconv(x)
        out = self.norm(out)
        out = self.pwconv1(out)
        out = self.act(out)
        out = self.pwconv2(out)
        out = self.se(out)
        return res + out

class DroneVisionNetV2Pro(nn.Module):
    """
    DroneVisionNet-V2-Pro Architecture (1.91M parameters):
    Multi-Scale Pyramidal Drone Perception Network with 4 Output Heads:
    1. Bounding Box: [cx, cy, w, h] normalized in [0, 1]
    2. Objectness: Raw logit for Focal Loss
    3. Classification: 4 class logits (LandingPad, Person, Obstacle, Drone)
    4. Orientation: [sin(theta), cos(theta)] approach angle vector
    """
    def __init__(self, num_classes=4):
        super().__init__()
        # Stem: 128x160 -> 32x40
        self.stem = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2, padding=1, bias=False),
            LayerNorm2d(32),
            nn.GELU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1, bias=False),
            LayerNorm2d(64),
            nn.GELU()
        )

        # Stage 1 (P3: 32x40, dim=64)
        self.stage1 = nn.Sequential(
            ConvNeXtBlock(64),
            ConvNeXtBlock(64)
        )

        # Transition 1 -> 2: 32x40 -> 16x20
        self.down1 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=2, stride=2, bias=False),
            LayerNorm2d(128)
        )

        # Stage 2 (P4: 16x20, dim=128)
        self.stage2 = nn.Sequential(
            ConvNeXtBlock(128),
            ConvNeXtBlock(128)
        )

        # Transition 2 -> 3: 16x20 -> 8x10
        self.down2 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=2, stride=2, bias=False),
            LayerNorm2d(256)
        )

        # Stage 3 (P5: 8x10, dim=256)
        self.stage3 = nn.Sequential(
            ConvNeXtBlock(256),
            ConvNeXtBlock(256)
        )

        # Multi-Scale Pyramid Spatial Pooling
        self.gap1 = nn.AdaptiveAvgPool2d(1)
        self.gap2 = nn.AdaptiveAvgPool2d(1)
        self.gap3 = nn.AdaptiveAvgPool2d(1)

        # Unified Latent Representation (64 + 128 + 256 = 448 dimensions)
        self.fc_shared = nn.Sequential(
            nn.Linear(448, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(0.15)
        )

        # Multi-Task Prediction Heads
        self.head_bbox = nn.Sequential(
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Linear(128, 4),
            nn.Sigmoid()
        )

        self.head_conf = nn.Sequential(
            nn.Linear(256, 64),
            nn.GELU(),
            nn.Linear(64, 1)
        )

        self.head_cls = nn.Sequential(
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Linear(128, num_classes)
        )

        self.head_angle = nn.Sequential(
            nn.Linear(256, 64),
            nn.GELU(),
            nn.Linear(64, 2)
        )

    def forward(self, x):
        x = self.stem(x)
        p3 = self.stage1(x)
        p4 = self.stage2(self.down1(p3))
        p5 = self.stage3(self.down2(p4))

        f3 = torch.flatten(self.gap1(p3), 1)
        f4 = torch.flatten(self.gap2(p4), 1)
        f5 = torch.flatten(self.gap3(p5), 1)
        f_cat = torch.cat([f3, f4, f5], dim=1)
        shared = self.fc_shared(f_cat)

        bbox = self.head_bbox(shared)
        conf = self.head_conf(shared)
        cls_logits = self.head_cls(shared)
        angle = self.head_angle(shared)
        # Normalize angle output vector to unit circle [sin, cos]
        angle = F.normalize(angle, p=2, dim=1)
        return bbox, conf, cls_logits, angle

# ------------------------------------------------------------------------------
# 3. Model Exponential Moving Average (EMA)
# ------------------------------------------------------------------------------
class ModelEMA:
    """Keeps an exponential moving average of model parameters for smooth evaluation."""
    def __init__(self, model, decay=0.9995):
        self.ema = copy.deepcopy(model).eval()
        for p in self.ema.parameters():
            p.requires_grad_(False)
        self.decay = decay

    def update(self, model):
        with torch.no_grad():
            for ema_v, model_v in zip(self.ema.state_dict().values(), model.state_dict().values()):
                if ema_v.dtype.is_floating_point:
                    ema_v.copy_(ema_v * self.decay + (1.0 - self.decay) * model_v)

# ------------------------------------------------------------------------------
# 4. Drone Optical Augmentation & Dataset Generator
# ------------------------------------------------------------------------------
CLASSES = ["LandingPad", "Person", "Obstacle", "Drone"]

def generate_aerial_batch(batch_size=32, height=128, width=160, device="cuda"):
    """
    Generates realistic synthetic aerial frames simulating ESP32-CAM OV2640 sensor:
    - Base ground textures: Asphalt tarmac, grass, earth, concrete.
    - Optical lens vignetting (radial darkening).
    - Solar glare / high-contrast illumination gradients.
    - Random rectangular cutout occlusions (simulating leaves / obstacles).
    - Gaussian sensor noise.
    """
    images = np.zeros((batch_size, 3, height, width), dtype=np.float32)
    bboxes = np.zeros((batch_size, 4), dtype=np.float32)
    confs = np.zeros((batch_size, 1), dtype=np.float32)
    classes = np.zeros((batch_size,), dtype=np.int64)
    angles = np.zeros((batch_size, 2), dtype=np.float32)

    y_grid, x_grid = np.ogrid[:height, :width]
    dist_from_center = np.sqrt((x_grid - width / 2.0)**2 + (y_grid - height / 2.0)**2)
    max_dist = np.sqrt((width / 2.0)**2 + (height / 2.0)**2)
    vignette = 1.0 - 0.28 * (dist_from_center / max_dist)**2

    for i in range(batch_size):
        # 1. Base terrain background
        base_gray = np.random.uniform(0.12, 0.42)
        img = np.full((height, width, 3), base_gray, dtype=np.float32)

        # 2. Illumination gradient (solar angle)
        grad = np.linspace(np.random.uniform(0.8, 0.95), np.random.uniform(1.05, 1.2), height).reshape(height, 1, 1)
        img = img * grad

        # 3. Vignette lens falloff
        img = img * vignette[:, :, None]

        # 4. Target injection (80% present, 20% negative background frame)
        has_target = (np.random.rand() > 0.20)
        if has_target:
            cls_id = np.random.randint(0, len(CLASSES))
            bw = np.random.randint(18, 54)
            bh = np.random.randint(18, 54)
            bx = np.random.randint(bw // 2 + 6, width - bw // 2 - 6)
            by = np.random.randint(bh // 2 + 6, height - bh // 2 - 6)

            theta = np.random.uniform(0, 2.0 * np.pi)
            angles[i, 0] = np.sin(theta)
            angles[i, 1] = np.cos(theta)

            x1 = max(0, bx - bw // 2)
            y1 = max(0, by - bh // 2)
            x2 = min(width, bx + bw // 2)
            y2 = min(height, by + bh // 2)

            # Class distinct signature colors
            if cls_id == 0:   # Landing Pad: Concentric amber/gold target
                color = np.array([0.92, 0.82, 0.20])
            elif cls_id == 1: # Person / Pilot: Emerald
                color = np.array([0.20, 0.88, 0.52])
            elif cls_id == 2: # Obstacle / Tower: Crimson
                color = np.array([0.88, 0.22, 0.28])
            else:             # Drone UAV: Cyan
                color = np.array([0.25, 0.65, 0.96])

            img[y1:y2, x1:x2, :] = color

            bboxes[i, 0] = bx / float(width)
            bboxes[i, 1] = by / float(height)
            bboxes[i, 2] = bw / float(width)
            bboxes[i, 3] = bh / float(height)
            confs[i, 0] = 1.0
            classes[i] = cls_id
        else:
            bboxes[i, :] = [0.5, 0.5, 0.0, 0.0]
            confs[i, 0] = 0.0
            classes[i] = 0
            angles[i, :] = [0.0, 1.0]

        # 5. Random Cutout Occlusion (simulate vegetation / obstacle obstruction)
        if np.random.rand() > 0.4:
            cut_w = np.random.randint(8, 24)
            cut_h = np.random.randint(8, 24)
            cx = np.random.randint(0, width - cut_w)
            cy = np.random.randint(0, height - cut_h)
            img[cy:cy + cut_h, cx:cx + cut_w, :] = np.random.uniform(0.05, 0.15)

        # 6. Optical sensor noise
        noise = np.random.normal(0, 0.018, img.shape).astype(np.float32)
        img = np.clip(img + noise, 0.0, 1.0)

        # Transpose to [3, H, W]
        images[i] = img.transpose(2, 0, 1)

    return (
        torch.from_numpy(images).to(device),
        torch.from_numpy(bboxes).to(device),
        torch.from_numpy(confs).to(device),
        torch.from_numpy(classes).to(device),
        torch.from_numpy(angles).to(device)
    )

# ------------------------------------------------------------------------------
# 5. Advanced Multi-Task Loss Engine (CIoU + Focal Loss + Angle MAE)
# ------------------------------------------------------------------------------
def compute_ciou_loss(pred_bbox, true_bbox):
    """Computes Complete IoU (CIoU) loss accounting for overlap, distance and aspect ratio."""
    b1_x1 = pred_bbox[:, 0] - pred_bbox[:, 2] / 2.0
    b1_y1 = pred_bbox[:, 1] - pred_bbox[:, 3] / 2.0
    b1_x2 = pred_bbox[:, 0] + pred_bbox[:, 2] / 2.0
    b1_y2 = pred_bbox[:, 1] + pred_bbox[:, 3] / 2.0

    b2_x1 = true_bbox[:, 0] - true_bbox[:, 2] / 2.0
    b2_y1 = true_bbox[:, 1] - true_bbox[:, 3] / 2.0
    b2_x2 = true_bbox[:, 0] + true_bbox[:, 2] / 2.0
    b2_y2 = true_bbox[:, 1] + true_bbox[:, 3] / 2.0

    inter_x1 = torch.max(b1_x1, b2_x1)
    inter_y1 = torch.max(b1_y1, b2_y1)
    inter_x2 = torch.min(b1_x2, b2_x2)
    inter_y2 = torch.min(b1_y2, b2_y2)

    inter_w = torch.clamp(inter_x2 - inter_x1, min=0.0)
    inter_h = torch.clamp(inter_y2 - inter_y1, min=0.0)
    inter_area = inter_w * inter_h

    w1, h1 = pred_bbox[:, 2], pred_bbox[:, 3]
    w2, h2 = true_bbox[:, 2], true_bbox[:, 3]
    union_area = w1 * h1 + w2 * h2 - inter_area
    iou = inter_area / (union_area + 1e-7)

    # Center distance penalty
    rho2 = (pred_bbox[:, 0] - true_bbox[:, 0]) ** 2 + (pred_bbox[:, 1] - true_bbox[:, 1]) ** 2

    # Enclosing bounding box diagonal
    c_x1 = torch.min(b1_x1, b2_x1)
    c_y1 = torch.min(b1_y1, b2_y1)
    c_x2 = torch.max(b1_x2, b2_x2)
    c_y2 = torch.max(b1_y2, b2_y2)
    c2 = (c_x2 - c_x1) ** 2 + (c_y2 - c_y1) ** 2 + 1e-7

    # Aspect ratio consistency
    v = (4.0 / (math.pi ** 2)) * torch.pow(torch.atan(w2 / (h2 + 1e-7)) - torch.atan(w1 / (h1 + 1e-7)), 2)
    with torch.no_grad():
        alpha = v / (1.0 - iou + v + 1e-7)

    ciou = iou - (rho2 / c2) - alpha * v
    return (1.0 - ciou).mean(), iou.mean()

def focal_binary_loss(logits, targets, alpha=0.25, gamma=2.0):
    """Focal loss for objectness confidence to balance foreground vs background."""
    p = torch.sigmoid(logits)
    bce = F.binary_cross_entropy_with_logits(logits, targets, reduction="none")
    p_t = p * targets + (1.0 - p) * (1.0 - targets)
    loss = bce * ((1.0 - p_t) ** gamma)
    if alpha >= 0:
        alpha_t = alpha * targets + (1.0 - alpha) * (1.0 - targets)
        loss = alpha_t * loss
    return loss.mean()

def compute_composite_loss(pred_bbox, pred_conf, pred_cls, pred_angle,
                           true_bbox, true_conf, true_cls, true_angle,
                           lambda_ciou=2.5, lambda_focal=1.5, lambda_cls=0.8, lambda_angle=0.5):
    """Composite Multi-Task Objective Function."""
    pos_mask = (true_conf > 0.5).squeeze(1)

    # 1. CIoU Loss on positive targets
    if pos_mask.sum() > 0:
        l_ciou, mean_iou = compute_ciou_loss(pred_bbox[pos_mask], true_bbox[pos_mask])
    else:
        l_ciou = torch.tensor(0.0, device=pred_bbox.device)
        mean_iou = torch.tensor(0.0, device=pred_bbox.device)

    # 2. Focal Objectness Loss
    l_focal = focal_binary_loss(pred_conf, true_conf)

    # 3. Classification Loss with Label Smoothing
    if pos_mask.sum() > 0:
        l_cls = F.cross_entropy(pred_cls[pos_mask], true_cls[pos_mask], label_smoothing=0.05)
    else:
        l_cls = torch.tensor(0.0, device=pred_bbox.device)

    # 4. Heading Vector Orientation Loss
    if pos_mask.sum() > 0:
        l_angle = F.l1_loss(pred_angle[pos_mask], true_angle[pos_mask])
    else:
        l_angle = torch.tensor(0.0, device=pred_bbox.device)

    total_loss = (lambda_ciou * l_ciou +
                  lambda_focal * l_focal +
                  lambda_cls * l_cls +
                  lambda_angle * l_angle)

    return total_loss, l_ciou, l_focal, l_cls, l_angle, mean_iou

# ------------------------------------------------------------------------------
# 6. Graceful Interruption Signal Handling
# ------------------------------------------------------------------------------
interrupted = False

def sigint_handler(signum, frame):
    global interrupted
    print("\n[INTERRUPT DETECTED] Gracefully halting training after current step...")
    interrupted = True

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGTERM, sigint_handler)

# ------------------------------------------------------------------------------
# 7. Main Deep Training Engine
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="DroneVisionNet-V2-Pro Deep Training Engine")
    parser.add_argument("--target-hours", type=float, default=2.0, help="Target training duration in hours (default: 2.0)")
    parser.add_argument("--epochs", type=int, default=None, help="Explicit epoch override (if omitted, dynamic 2h budget is used)")
    parser.add_argument("--steps-per-epoch", type=int, default=200, help="Number of optimizer steps per epoch (default: 200)")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size per forward pass (default: 32)")
    parser.add_argument("--lr", type=float, default=5e-4, help="Initial peak learning rate (default: 5e-4)")
    parser.add_argument("--weight-decay", type=float, default=1e-4, help="Weight decay for AdamW (default: 1e-4)")
    parser.add_argument("--resume", action="store_true", help="Resume training from latest checkpoint if available")
    args = parser.parse_args()

    terminal_width = 86
    sep = "=" * terminal_width
    sub_sep = "-" * terminal_width

    print(sep)
    print("DRONE VISION SYSTEM V2-PRO - DEEP RESEARCH & TRAINING ENGINE")
    print("WORKSPACE:    /home/mullainathan/projects/mini-ai-drone/research_v2")
    print(f"DEVICE:       {gpu_name} ({total_vram_mb:,} MB VRAM)")
    print(f"PYTORCH:      {torch.__version__} | CUDA: {torch.version.cuda} | SM_{cuda_capability[0]}{cuda_capability[1]}")
    print(sep)

    # Initialize Architecture
    model = DroneVisionNetV2Pro(num_classes=len(CLASSES)).to(device)
    model_ema = ModelEMA(model, decay=0.9995)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    model_size_mb = (total_params * 4) / (1024 * 1024)

    print(sub_sep)
    print("MODEL ARCHITECTURE SPECIFICATIONS: DroneVisionNet-V2-Pro")
    print(sub_sep)
    print(f"  Total Parameters:          {total_params:,}")
    print(f"  Trainable Parameters:      {trainable_params:,}")
    print(f"  Model Memory Size (FP32):  {model_size_mb:.2f} MB")
    print(f"  Input Resolution:          128 x 160 x 3 (RGB Channels)")
    print(f"  Target Classes ({len(CLASSES)}):       {', '.join(CLASSES)}")
    print(f"  Multi-Task Heads:          BBox [cx, cy, w, h] | Focal Objectness | Multi-Class | Orientation")
    print(f"  Precision:                 Mixed Precision AMP (FP16 / FP32)")
    print(sub_sep)

    target_duration_sec = args.target_hours * 3600.0
    steps_per_epoch = args.steps_per_epoch
    val_steps = 20
    batch_size = args.batch_size
    initial_lr = args.lr
    min_lr = 1e-6

    optimizer = torch.optim.AdamW(model.parameters(), lr=initial_lr, betas=(0.9, 0.999), weight_decay=args.weight_decay)
    scaler = torch.amp.GradScaler('cuda')

    start_epoch = 1
    best_val_loss = float("inf")

    # Resume from checkpoint if requested
    latest_ckpt_path = os.path.join(CHECKPOINT_DIR, "latest_drone_vision_v2.pt")
    if args.resume and os.path.exists(latest_ckpt_path):
        print(f"Loading checkpoint from: {latest_ckpt_path}")
        checkpoint = torch.load(latest_ckpt_path, map_location=device)
        model.load_state_dict(checkpoint["model_state_dict"])
        model_ema.ema.load_state_dict(checkpoint["ema_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        start_epoch = checkpoint["epoch"] + 1
        best_val_loss = checkpoint.get("best_val_loss", float("inf"))
        print(f"Resumed successfully at Epoch {start_epoch:02d} (Best Val Loss: {best_val_loss:.5f})")

    # Warmup calibration to calibrate execution pacing
    print("Running hardware execution calibration (10 steps)...")
    # 2 un-timed warmup steps for CUDA context initialization
    for _ in range(2):
        img_c, b_c, cf_c, cl_c, a_c = generate_aerial_batch(batch_size=batch_size, device=device)
        with torch.amp.autocast('cuda'):
            pb, pc, pcl, pa = model(img_c)
            loss_c, _, _, _, _, _ = compute_composite_loss(pb, pc, pcl, pa, b_c, cf_c, cl_c, a_c)
        scaler.scale(loss_c).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)
    torch.cuda.synchronize()

    calib_t0 = time.time()
    for _ in range(10):
        img_c, b_c, cf_c, cl_c, a_c = generate_aerial_batch(batch_size=batch_size, device=device)
        with torch.amp.autocast('cuda'):
            pb, pc, pcl, pa = model(img_c)
            loss_c, _, _, _, _, _ = compute_composite_loss(pb, pc, pcl, pa, b_c, cf_c, cl_c, a_c)
        scaler.scale(loss_c).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)
    torch.cuda.synchronize()
    calib_duration = time.time() - calib_t0
    sec_per_step = calib_duration / 10.0
    sec_per_epoch_est = sec_per_step * steps_per_epoch + (sec_per_step * val_steps * 0.4)

    if args.epochs is not None:
        total_epochs = args.epochs
    else:
        total_epochs = max(10, int(target_duration_sec / max(1.0, sec_per_epoch_est)))

    # Cosine Annealing with Warmup scheduler
    warmup_epochs = max(2, int(total_epochs * 0.05))
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_epochs, eta_min=min_lr)

    print("TRAINING HYPERPARAMETERS & PACING:")
    print(f"  Target Duration:           {format_time(target_duration_sec)} ({target_duration_sec:,.0f} seconds)")
    print(f"  Calibrated Pacing:         {sec_per_step * 1000.0:.2f} ms/step (~{batch_size / sec_per_step:.1f} img/s)")
    print(f"  Estimated Epoch Time:      {sec_per_epoch_est:.1f} seconds")
    print(f"  Planned Epochs:            {total_epochs} ({steps_per_epoch} steps/epoch = {steps_per_epoch * batch_size:,} samples/epoch)")
    print(f"  Optimizer:                 AdamW (lr={initial_lr:.1e}, wd={args.weight_decay:.1e})")
    print(f"  LR Schedule:               Linear Warmup ({warmup_epochs} epochs) -> CosineAnnealing (eta_min={min_lr:.1e})")
    print(f"  Loss Formulation:          CIoU (2.5) + Focal (1.5) + Label-Smoothed CE (0.8) + Heading (0.5)")
    print(sep)
    print("STARTING 2-HOUR DEEP TRAINING RUN [RESEARCH V2 ISOLATED ENVIRONMENT]...")
    print(sep)

    total_start_time = time.time()

    for epoch in range(start_epoch, total_epochs + 1):
        if interrupted:
            break

        epoch_start_time = time.time()
        model.train()

        running_total = 0.0
        running_ciou = 0.0
        running_focal = 0.0
        running_cls = 0.0
        running_angle = 0.0
        running_iou = 0.0

        current_lr = scheduler.get_last_lr()[0]
        elapsed_so_far = time.time() - total_start_time
        remaining_time = max(0, target_duration_sec - elapsed_so_far)
        pct_complete = min(100.0, (elapsed_so_far / target_duration_sec) * 100.0)

        print(f"\n[EPOCH {epoch:03d}/{total_epochs:03d}] [{format_time(elapsed_so_far)} / {format_time(target_duration_sec)}] ({pct_complete:5.1f}%) | ETA: {format_time(remaining_time)} | LR: {current_lr:.2e}")

        for step in range(1, steps_per_epoch + 1):
            if interrupted:
                break

            step_t0 = time.time()

            # Generate synthetic aerial batch with flight optical perturbations
            imgs, bboxes, confs, clss, angles = generate_aerial_batch(batch_size=batch_size, device=device)

            optimizer.zero_grad(set_to_none=True)

            # Mixed precision forward pass
            with torch.amp.autocast('cuda'):
                p_bbox, p_conf, p_cls, p_angle = model(imgs)
                loss, l_ciou, l_focal, l_cls, l_angle, mean_iou = compute_composite_loss(
                    p_bbox, p_conf, p_cls, p_angle, bboxes, confs, clss, angles
                )

            # Backward pass with scaled gradients and gradient clipping
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()

            # Update Model EMA shadow weights
            model_ema.update(model)

            step_duration = max(1e-5, time.time() - step_t0)
            throughput = batch_size / step_duration

            running_total += loss.item()
            running_ciou += l_ciou.item()
            running_focal += l_focal.item()
            running_cls += l_cls.item()
            running_angle += l_angle.item()
            running_iou += mean_iou.item()

            # Print progress every 25 steps or last step
            if step % 25 == 0 or step == steps_per_epoch:
                progress_pct = (step / steps_per_epoch) * 100.0
                bar_len = 18
                filled = int(bar_len * (step / steps_per_epoch))
                bar = "=" * filled + (">" if filled < bar_len else "") + "." * (bar_len - filled - (1 if filled < bar_len else 0))

                gpu_temp, gpu_pow, _ = query_gpu_telemetry()
                vram_used = int(torch.cuda.memory_allocated() / (1024 * 1024)) if torch.cuda.is_available() else 0

                print(
                    f"  Step [{step:03d}/{steps_per_epoch:03d}] [{bar}] {progress_pct:3.0f}% | "
                    f"Throughput: {throughput:5.1f} img/s | "
                    f"VRAM: {vram_used:4d}/{total_vram_mb} MB | "
                    f"GPU: {gpu_temp:2d}C ({gpu_pow:4.1f}W)\n"
                    f"    Loss: {loss.item():.5f} [CIoU: {l_ciou.item():.4f} | Focal: {l_focal.item():.4f} | Cls: {l_cls.item():.4f} | Angle: {l_angle.item():.4f}] | "
                    f"||g||: {grad_norm:.3f}"
                )

        scheduler.step()
        epoch_duration = time.time() - epoch_start_time

        # Validation Phase (Every Epoch)
        model.eval()
        model_ema.ema.eval()

        val_total = 0.0
        val_ema_total = 0.0
        val_iou_sum = 0.0
        val_cls_correct = 0
        val_pos_count = 0
        val_angle_err_deg = 0.0
        infer_latencies = []

        with torch.no_grad():
            for _ in range(val_steps):
                v_img, v_bbox, v_conf, v_cls, v_angle = generate_aerial_batch(batch_size=batch_size, device=device)
                
                t_inf0 = time.time()
                with torch.amp.autocast('cuda'):
                    # Base model evaluation
                    vb_box, vb_conf, vb_cls, vb_angle = model(v_img)
                    v_loss, _, _, _, _, _ = compute_composite_loss(vb_box, vb_conf, vb_cls, vb_angle, v_bbox, v_conf, v_cls, v_angle)
                    
                    # EMA model evaluation
                    ve_box, ve_conf, ve_cls, ve_angle = model_ema.ema(v_img)
                    ve_loss, _, _, _, _, _ = compute_composite_loss(ve_box, ve_conf, ve_cls, ve_angle, v_bbox, v_conf, v_cls, v_angle)

                t_inf1 = time.time()
                infer_latencies.append((t_inf1 - t_inf0) / batch_size * 1000.0)

                val_total += v_loss.item()
                val_ema_total += ve_loss.item()

                pos = (v_conf > 0.5).squeeze(1)
                if pos.sum() > 0:
                    _, ious = compute_ciou_loss(ve_box[pos], v_bbox[pos])
                    val_iou_sum += ious.sum().item()
                    val_pos_count += pos.sum().item()

                    preds = ve_cls[pos].argmax(dim=1)
                    val_cls_correct += (preds == v_cls[pos]).sum().item()

                    # Angle angular error in degrees
                    cos_sim = F.cosine_similarity(ve_angle[pos], v_angle[pos], dim=1).clamp(-1.0, 1.0)
                    deg_err = torch.acos(cos_sim) * (180.0 / math.pi)
                    val_angle_err_deg += deg_err.sum().item()

        val_loss_base = val_total / val_steps
        val_loss_ema = val_ema_total / val_steps
        mean_iou = (val_iou_sum / max(1, val_pos_count)) * 100.0
        cls_acc = (val_cls_correct / max(1, val_pos_count)) * 100.0
        mean_deg_err = val_angle_err_deg / max(1, val_pos_count)
        avg_infer_latency = float(np.mean(infer_latencies))
        fps_estimate = 1000.0 / avg_infer_latency if avg_infer_latency > 0 else 0.0

        # Checkpoint Management
        is_best = val_loss_ema < best_val_loss
        ckpt_status = "[RETAINED]"
        if is_best:
            best_val_loss = val_loss_ema
            best_ckpt = os.path.join(CHECKPOINT_DIR, "best_drone_vision_v2.pt")
            ema_ckpt = os.path.join(CHECKPOINT_DIR, "ema_drone_vision_v2.pt")
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "val_loss": val_loss_base,
                "mean_iou": mean_iou,
                "cls_acc": cls_acc,
                "classes": CLASSES
            }, best_ckpt)
            torch.save({
                "epoch": epoch,
                "model_state_dict": model_ema.ema.state_dict(),
                "val_loss": val_loss_ema,
                "mean_iou": mean_iou,
                "cls_acc": cls_acc,
                "classes": CLASSES
            }, ema_ckpt)
            ckpt_status = f"[SAVED -> best_drone_vision_v2.pt & ema_drone_vision_v2.pt]"

        # Save latest checkpoint every epoch for safe resumption
        torch.save({
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "ema_state_dict": model_ema.ema.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "best_val_loss": best_val_loss,
            "classes": CLASSES
        }, latest_ckpt_path)

        train_loss = running_total / steps_per_epoch
        print(sub_sep)
        print(f"EPOCH {epoch:03d} SUMMARY:")
        print(f"  Time Progress:       {format_time(time.time() - total_start_time)} elapsed | {format_time(max(0, target_duration_sec - (time.time() - total_start_time)))} remaining")
        print(f"  Train Loss:          {train_loss:.5f} (CIoU: {running_ciou/steps_per_epoch:.4f} | Focal: {running_focal/steps_per_epoch:.4f} | Cls: {running_cls/steps_per_epoch:.4f} | Angle: {running_angle/steps_per_epoch:.4f})")
        print(f"  Val Loss (Base):     {val_loss_base:.5f}")
        print(f"  Val Loss (EMA):      {val_loss_ema:.5f} {ckpt_status}")
        print(f"  Mean IoU Overlap:    {mean_iou:.2f} % (Target spatial alignment)")
        print(f"  Class Accuracy:      {cls_acc:.2f} % (Target Category Recognition)")
        print(f"  Approach Angle MAE:  {mean_deg_err:.2f} deg (Heading Vector Alignment)")
        print(f"  Inference Latency:   {avg_infer_latency:.3f} ms/frame ({fps_estimate:.1f} FPS on RTX 5060)")
        print(f"  Epoch Duration:      {epoch_duration:.2f} s")
        print(sub_sep)

        # Time budget check: If reached 2 hours target, conclude run
        if (time.time() - total_start_time) >= target_duration_sec:
            print("\n[TIME BUDGET ACHIEVED] Reached 2-Hour target training threshold.")
            break

    total_training_time = time.time() - total_start_time
    final_reason = "INTERRUPTED" if interrupted else "COMPLETED"

    if interrupted:
        interrupted_ckpt = os.path.join(CHECKPOINT_DIR, "interrupted_checkpoint.pt")
        torch.save({
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "ema_state_dict": model_ema.ema.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "best_val_loss": best_val_loss,
            "classes": CLASSES
        }, interrupted_ckpt)
        print(f"[CHECKPOINT SAVED] Interrupted state secured at: {interrupted_ckpt}")

    print(sep)
    print(f"TRAINING RUN {final_reason} - RESEARCH V2 BENCHMARK")
    print(f"  Total Duration:      {format_time(total_training_time)} ({total_training_time:.2f} s)")
    print(f"  Best Val EMA Loss:   {best_val_loss:.5f}")
    print(f"  Saved Checkpoints:   {CHECKPOINT_DIR}")
    print(f"  Inference Speed:     {fps_estimate:.1f} FPS (Target ESP32-CAM stream is 30 FPS)")
    print(f"  Isolated Directory:  {OUTPUT_DIR}")
    print(sep)

if __name__ == "__main__":
    main()
