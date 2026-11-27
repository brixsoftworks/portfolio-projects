"""
LESSON 2 & 3: Building & Training a Drone Vision Model from Scratch
-------------------------------------------------------------------
In this lesson, you will learn:
1. Model Architecture: Feature Extraction (Convolutions) + Regression Head (Linear).
2. The Loss Function: Mean Squared Error (MSE) - measuring the error between where
   the drone THINKS the target is vs where it ACTUALLY is.
3. The Optimizer (AdamW): How gradients update the weights via backpropagation.
4. Training Loop: Generating dynamic flight frames and training the model on your RTX 5060!
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import cv2
import time

print("=" * 65)
print("MODULE 2 & 3: ARCHITECTURE, LOSS FUNCTIONS, AND TRAINING LOOP")
print("=" * 65)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[+] Active GPU: {torch.cuda.get_device_name(0)}")

# ------------------------------------------------------------------
# CONCEPT 1: Designing the Architecture (DroneTrackNet)
# ------------------------------------------------------------------
# Our model will take: An image of size (3, 120, 160)
# Our model will output: [target_x, target_y, target_area, confidence]
# - target_x: normalized horizontal position [0.0 = left, 1.0 = right]
# - target_y: normalized vertical position [0.0 = top, 1.0 = bottom]
# - target_area: normalized bounding area [0.0 = tiny/far, 1.0 = fills frame]
# - confidence: probability that target is present [0.0 to 1.0]

class DroneTrackNet(nn.Module):
    def __init__(self):
        super(DroneTrackNet, self).__init__()
        
        # 1. Feature Extractor (Backbone)
        # Deep stack of Convolutions that learn from simple edges to full objects
        self.features = nn.Sequential(
            # Layer 1: 3 channels (RGB) -> 16 filters. Output: 60x80
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            # Layer 2: 16 -> 32 filters. Output: 30x40
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            # Layer 3: 32 -> 64 filters. Output: 15x20
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            # Layer 4: 64 -> 128 filters. Output: 7x10
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        
        # 2. Global Average Pooling: Flattens 128 feature maps of (7x10) into 128 single values
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        
        # 3. Prediction Head (Fully Connected Layers)
        # Translates high-level feature patterns into the 4 flight parameters
        self.regressor = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 4),
            nn.Sigmoid() # Squashes all 4 outputs strictly into [0.0, 1.0]
        )

    def forward(self, x):
        # x is [Batch, 3, 120, 160]
        x = self.features(x)
        x = self.gap(x)
        x = torch.flatten(x, 1) # Shape: [Batch, 128]
        output = self.regressor(x) # Shape: [Batch, 4] -> [x, y, area, conf]
        return output

model = DroneTrackNet().to(device)
total_params = sum(p.numel() for p in model.parameters())
print(f"[+] DroneTrackNet instantiated! Total parameters: {total_params:,}")
print("    (Lightweight enough to run at 300+ FPS on your RTX 5060!)")

# ------------------------------------------------------------------
# CONCEPT 2: Generating a Synthetic Drone Flight Dataset
# ------------------------------------------------------------------
# In real life, you would collect video from your ESP32-CAM.
# To teach the model right now, we create a dynamic batch generator that
# places targets at random positions (x, y) with random sizes and background noise.

def generate_drone_batch(batch_size=32, height=120, width=160):
    images = np.zeros((batch_size, height, width, 3), dtype=np.float32)
    labels = np.zeros((batch_size, 4), dtype=np.float32)
    
    for i in range(batch_size):
        # Random background brightness
        bg_val = np.random.uniform(0.05, 0.25)
        images[i, :, :] = bg_val
        
        # Random target position & radius
        r = np.random.randint(8, 24)
        cx = np.random.randint(r + 5, width - r - 5)
        cy = np.random.randint(r + 5, height - r - 5)
        
        # Target color (bright red/orange marker or person)
        color = (np.random.uniform(0.7, 1.0), np.random.uniform(0.6, 1.0), 0.1)
        cv2.circle(images[i], (cx, cy), r, color, -1)
        
        # Add random noise (motion blur / camera sensor noise)
        noise = np.random.normal(0, 0.03, images[i].shape)
        images[i] = np.clip(images[i] + noise, 0.0, 1.0)
        
        # Ground Truth Label: [norm_x, norm_y, norm_area, confidence]
        norm_x = cx / width
        norm_y = cy / height
        norm_area = (np.pi * (r ** 2)) / (width * height)
        conf = 1.0
        
        labels[i] = [norm_x, norm_y, norm_area, conf]
        
    # Convert to PyTorch [Batch, Channels, Height, Width]
    tensor_x = torch.from_numpy(images).permute(0, 3, 1, 2).to(device)
    tensor_y = torch.from_numpy(labels).to(device)
    return tensor_x, tensor_y

# ------------------------------------------------------------------
# CONCEPT 3: The Loss Function & Optimizer
# ------------------------------------------------------------------
# Loss Function (MSE): Measures (Predicted - Actual)^2
# If the target is at (0.80, 0.50) and model guesses (0.20, 0.50),
# the loss is large: (0.80 - 0.20)^2 = 0.36
criterion = nn.MSELoss()

# Optimizer (AdamW): Adjusts all 100k+ weights in the direction of the gradient
optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)

# ------------------------------------------------------------------
# CONCEPT 4: The Training Loop (Watch the Model Learn!)
# ------------------------------------------------------------------
print("\n" + "=" * 65)
print("STARTING TRAINING LOOP ON NVIDIA RTX 5060...")
print("=" * 65)

epochs = 15
batches_per_epoch = 20
batch_size = 32

start_time = time.time()
for epoch in range(1, epochs + 1):
    epoch_loss = 0.0
    for _ in range(batches_per_epoch):
        # 1. Get batch
        inputs, targets = generate_drone_batch(batch_size=batch_size)
        
        # 2. Zero gradients from previous step
        optimizer.zero_grad()
        
        # 3. Forward Pass: Make predictions
        predictions = model(inputs)
        
        # 4. Compute Loss
        loss = criterion(predictions, targets)
        
        # 5. Backward Pass (Backpropagation): Compute gradients via Chain Rule
        loss.backward()
        
        # 6. Optimizer Step: Update weights (W = W - lr * gradient)
        optimizer.step()
        
        epoch_loss += loss.item()
        
    avg_loss = epoch_loss / batches_per_epoch
    print(f"Epoch [{epoch:02d}/{epochs:02d}] ---> MSE Loss: {avg_loss:.6f}")

total_duration = time.time() - start_time
print(f"\n[+] Training complete in {total_duration:.2f} seconds on GPU!")

# Save the trained model weights
model_path = "/home/mullainathan/projects/mini-ai-drone/drone_track_net.pth"
torch.save(model.state_dict(), model_path)
print(f"[+] Model weights saved to: {model_path}")

# ------------------------------------------------------------------
# CONCEPT 5: Testing on an Unseen Test Frame
# ------------------------------------------------------------------
model.eval()
with torch.no_grad():
    test_img, true_label = generate_drone_batch(batch_size=1)
    predicted = model(test_img)[0].cpu().numpy()
    actual = true_label[0].cpu().numpy()
    
    print("\n" + "=" * 65)
    print("VERIFICATION: PREDICTION VS GROUND TRUTH")
    print("=" * 65)
    print(f"Actual Position    -> X: {actual[0]:.3f}, Y: {actual[1]:.3f}, Area: {actual[2]:.4f}")
    print(f"Predicted Position -> X: {predicted[0]:.3f}, Y: {predicted[1]:.3f}, Area: {predicted[2]:.4f}")
    error_x_px = abs(predicted[0] - actual[0]) * 160
    error_y_px = abs(predicted[1] - actual[1]) * 120
    print(f"Tracking Accuracy  -> Off by only ~{error_x_px:.1f} pixels horizontally, ~{error_y_px:.1f} pixels vertically!")
