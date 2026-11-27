"""
LESSON 1: How Computers See Images & What a Convolution Actually Is
--------------------------------------------------------------------
In this lesson, you will learn:
1. What an image is to PyTorch: The [Batch, Channels, Height, Width] Tensor.
2. The Convolution operation: Why we don't use flat matrices for vision.
3. How a 3x3 filter slides across an image to extract features (edges, corners).
4. Running our first Convolution on your NVIDIA RTX 5060 GPU!
"""

import torch
import torch.nn as nn
import numpy as np
import cv2

print("=" * 60)
print("MODULE 1: TENSORS & CONVOLUTIONS FROM SCRATCH")
print("=" * 60)

# Check GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[+] Device detected: {device} ({torch.cuda.get_device_name(0)})")

# -------------------------------------------------------------
# CONCEPT 1: An Image is Just a 3D Grid of Numbers
# -------------------------------------------------------------
# OpenCV loads images as: Height x Width x Channels (BGR, 0 to 255)
# PyTorch expects images as: [Batch_Size, Channels, Height, Width] (NCHW)
#
# Let's create a synthetic camera frame: 120 height, 160 width, 3 channels (RGB)
# with a mock target (like a person or drone gate) in the middle.

frame = np.zeros((120, 160, 3), dtype=np.uint8)

# Draw a simulated obstacle / drone target (white circle & rectangle)
cv2.circle(frame, (80, 60), 20, (255, 255, 255), -1)      # Target center
cv2.rectangle(frame, (10, 10), (40, 100), (180, 180, 180), -1) # Obstacle on left

cv2.imwrite("/home/mullainathan/projects/mini-ai-drone/lesson1_synthetic_input.png", frame)
print("[+] Saved synthetic camera frame to 'lesson1_synthetic_input.png'")

# -------------------------------------------------------------
# CONCEPT 2: Normalization
# -------------------------------------------------------------
# Raw pixels are integers from 0 to 255.
# Neural networks hate large, unnormalized inputs because weights explode!
# We normalize pixel values to [0.0, 1.0] or [-1.0, 1.0].

normalized_frame = frame.astype(np.float32) / 255.0

# Convert NumPy (H, W, C) -> PyTorch (C, H, W) -> Add Batch Dimension (1, C, H, W)
tensor_img = torch.from_numpy(normalized_frame).permute(2, 0, 1).unsqueeze(0).to(device)

print(f"[+] Input Tensor Shape: {tensor_img.shape}  [Batch=1, Channels=3, H=120, W=160]")
print(f"[+] Pixel value range: Min = {tensor_img.min():.2f}, Max = {tensor_img.max():.2f}")

# -------------------------------------------------------------
# CONCEPT 3: What is a Convolution (Conv2d)?
# -------------------------------------------------------------
# Instead of connecting every pixel to a neuron (which would require millions of weights),
# a Convolution slides a tiny 3x3 window (kernel) across the image.
#
# At each step, it multiplies the 3x3 window with the 3x3 pixel patch and adds them:
# Output = (Kernel * Pixels) + Bias
#
# Let's create:
# - Input Channels = 3 (RGB)
# - Output Channels = 8 (The layer will learn 8 different feature detectors: vertical edges,
#   horizontal edges, diagonals, color contrasts, etc.)
# - Kernel Size = 3x3
# - Stride = 1 (Slide 1 pixel at a time)
# - Padding = 1 (Keeps the output image height/width identical to input)

conv1 = nn.Conv2d(in_channels=3, out_channels=8, kernel_size=3, stride=1, padding=1).to(device)
relu = nn.ReLU() # Activation function: zeroes out negative values (creates non-linearity)

# Pass the image through the convolution on the GPU
feature_maps = relu(conv1(tensor_img))

print(f"[+] Output Feature Maps Shape: {feature_maps.shape}  [Batch=1, Features=8, H=120, W=160]")
print(f"[+] Number of learnable parameters in this layer: {sum(p.numel() for p in conv1.parameters())}")
print("    Formula: (3 input channels * 3 * 3 kernel * 8 filters) + 8 biases = 224 weights!")

# -------------------------------------------------------------
# CONCEPT 4: Downsampling with Max Pooling
# -------------------------------------------------------------
# A drone cannot afford to process high resolutions in deep layers.
# MaxPool2d(kernel_size=2, stride=2) takes the largest number in every 2x2 block.
# This halves the height and width (120x160 -> 60x80) while keeping the strongest signals.

pool = nn.MaxPool2d(kernel_size=2, stride=2)
pooled_features = pool(feature_maps)
print(f"[+] After MaxPool2d Shape: {pooled_features.shape}  [Batch=1, Features=8, H=60, W=80]")

print("\n[SUCCESS] Lesson 1 concepts verified on NVIDIA GPU!")
