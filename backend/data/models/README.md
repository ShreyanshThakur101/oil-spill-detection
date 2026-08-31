# Model Artifacts Directory

This directory holds trained machine learning weights and model checkpoints (e.g., `.pth` files).

## Guidelines
* **Do NOT commit model weight binaries (`*.pth`, `*.pt`, `*.onnx`, etc.) to Git.**
* Model artifacts will be generated via `backend/app/ml/train.py` or downloaded from designated hosted storage (e.g., Google Drive link with SHA256 checksum).

---

## Person 2 (ML / Detection) Models
* **Architecture:** U-Net with ResNet34 encoder (`segmentation-models-pytorch`)
* **Target weight file:** `backend/data/models/unet_resnet34_oilspill.pth`
* **Training command:**
  ```bash
  python -m app.ml.train --data-dir backend/data/raw/kaggle_oil_spill --epochs 20
  ```
* **Hosted Link / Checksum:** TBD by Person 2 — once training completes, upload the `.pth`
  to Google Drive and record the share link + file size + SHA256 checksum here so teammates
  can reproduce it without retraining.

  - Google Drive link: `TBD`
  - File size: `TBD`
  - SHA256: `TBD`
