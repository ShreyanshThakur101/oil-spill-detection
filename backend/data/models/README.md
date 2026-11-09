# Guidelines for Model Artifacts and Checkpoints

This directory is intended for trained machine learning model checkpoints (`*.pth`, `*.pt`, `*.onnx`).

## Guidelines
- Do NOT commit binary weights directly to Git. Model checkpoints must be stored in external persistent storage or downloaded via verified links with SHA256 checksums.
- Canonical target model checkpoint: `unet_resnet34_oilspill.pth` (U-Net with ResNet-34 encoder trained on Sentinel-1 SAR imagery).

## Status
- **Target Architecture**: U-Net with ResNet-34 backbone (`segmentation-models-pytorch`).
- **Target File**: `backend/data/models/unet_resnet34_oilspill.pth`.
- **Checkpoint Status**: Pending training via Google Colab / GPU worker.
