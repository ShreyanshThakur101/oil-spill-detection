# PERSON 2 — Detection Module (Stage 1: SAR Oil-Slick Segmentation)

Read `docs/ARCHITECTURE.md` in full before starting, especially §2 (AI/ML justification), §5.2 (your interface contract), and §9 (dependency table). You own the entire `backend/app/ml/` folder — nobody else edits files in there.

---

## Your role in one sentence
You take a Sentinel-1 SAR image and produce a geographic polygon of the detected oil slick plus its shape features, exposed to the rest of the system through exactly one function: `detect_slick()`.

---

## Prerequisites before you can fully finish (but you can start most of this immediately)

- `backend/app/utils/geo.py` **stub** must exist on `main` (Person 1, Day 1) — you can write and test your own logic against it once Person 1 fills in the real geometry functions (Day 2), but you can start dataset/training work immediately without waiting.
- Person 1 will tell you the exact demo case SAR scene (date/bbox) by end of Day 1 — sanity-check your trained model against that specific scene as early as possible, don't wait until the end.

---

## STEP 1 — Clone and branch

```bash
git clone <repository-url>
cd oil-spill-detection
git checkout -b person2/ml-setup
```

Only edit files under `backend/app/ml/`, `backend/tests/test_detection.py`, `backend/scripts/download_training_data.py`, `backend/data/models/README.md`, `backend/data/raw/README.md` (add your own section, don't touch Person 3's), and `backend/requirements.txt` (append only, under the "Person 2 (ML) additions" marker).

## STEP 2 — Set up your environment and dependencies

Add to `backend/requirements.txt` under the Person 2 section:
```
torch>=2.1
torchvision
segmentation-models-pytorch
rasterio
opencv-python
Pillow
numpy
```
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

## STEP 3 — Download the training dataset

**`backend/scripts/download_training_data.py`**
```python
"""
Downloads the Kaggle "Oil Spill Detection" dataset into backend/data/raw/kaggle_oil_spill/.
Requires a Kaggle API token (~/.kaggle/kaggle.json) — see Kaggle account settings.
Run manually: python backend/scripts/download_training_data.py
"""
import subprocess
from pathlib import Path

TARGET_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "kaggle_oil_spill"

def main():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "kaggle", "datasets", "download",
        "-d", "<exact-kaggle-dataset-slug-you-find-when-searching-'oil-spill-detection'>",
        "-p", str(TARGET_DIR), "--unzip"
    ], check=True)
    print(f"Downloaded to {TARGET_DIR}")

if __name__ == "__main__":
    main()
```
**Action item before writing this for real:** search Kaggle for the exact current dataset slug (the briefing doc references "the Kaggle Sentinel-1 oil spill dataset" but you must confirm the exact dataset name/slug and check it actually contains paired images + segmentation masks, not just classification labels — if it only has classification labels, flag this to the team immediately since it changes the training approach). Update `backend/data/raw/README.md` with the exact dataset name, the manual download URL as a fallback, and the expected folder layout after unzip (e.g. `images/`, `masks/`).

## STEP 4 — `ml/dataset.py`

```python
"""
PyTorch Dataset wrapper for the oil-spill segmentation training data.
"""
import os
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
import cv2
import numpy as np
import torch

class OilSpillDataset(Dataset):
    """
    Input (constructor):
        images_dir: str — folder of input images (SAR patches, grayscale or 3-channel)
        masks_dir: str  — folder of binary segmentation masks, same filenames as images
        image_size: int — resize target (e.g. 256), model expects square input
    __getitem__ output:
        (image_tensor, mask_tensor) — image_tensor shape (3, H, W) float32 normalized 0-1,
        mask_tensor shape (1, H, W) float32 with values 0.0 or 1.0
    """
    def __init__(self, images_dir: str, masks_dir: str, image_size: int = 256):
        self.images_dir = Path(images_dir)
        self.masks_dir = Path(masks_dir)
        self.image_size = image_size
        self.filenames = sorted(os.listdir(self.images_dir))

    def __len__(self) -> int:
        return len(self.filenames)

    def __getitem__(self, idx: int):
        fname = self.filenames[idx]
        img = cv2.imread(str(self.images_dir / fname))
        img = cv2.resize(img, (self.image_size, self.image_size))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

        mask = cv2.imread(str(self.masks_dir / fname), cv2.IMREAD_GRAYSCALE)
        mask = cv2.resize(mask, (self.image_size, self.image_size))
        mask = (mask > 127).astype(np.float32)

        img_t = torch.from_numpy(img).permute(2, 0, 1)          # (3,H,W)
        mask_t = torch.from_numpy(mask).unsqueeze(0)             # (1,H,W)
        return img_t, mask_t


def get_dataloaders(data_dir: str, batch_size: int = 8, val_split: float = 0.15):
    """
    Input: data_dir containing images/ and masks/ subfolders; batch_size; val_split fraction.
    Output: (train_loader, val_loader) — torch DataLoader objects.
    Purpose: build train/val split and wrap in DataLoaders for train.py.
    """
    full_dataset = OilSpillDataset(f"{data_dir}/images", f"{data_dir}/masks")
    val_size = int(len(full_dataset) * val_split)
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = torch.utils.data.random_split(full_dataset, [train_size, val_size])
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader
```

**Edge cases to handle:** filenames that exist in `images/` but not `masks/` (skip with a warning, don't crash); corrupt/unreadable image files (`cv2.imread` returns `None` — check for this and skip); empty dataset directory (raise a clear error in `get_dataloaders`, don't silently produce an empty loader).

## STEP 5 — `ml/model_utils.py`

```python
"""
Model construction and checkpoint I/O helpers.
"""
import segmentation_models_pytorch as smp
import torch

def build_model():
    """
    Output: a segmentation_models_pytorch Unet with a resnet34 encoder,
    pretrained on ImageNet, 3 input channels, 1 output channel (binary mask logits).
    """
    return smp.Unet(encoder_name="resnet34", encoder_weights="imagenet",
                     in_channels=3, classes=1, activation=None)

def save_checkpoint(model, path: str):
    """Input: trained model, output path. Saves model.state_dict() to path."""
    torch.save(model.state_dict(), path)

def load_checkpoint(model, path: str, device: str = "cpu"):
    """Input: model instance (from build_model()), checkpoint path, device.
       Output: model with weights loaded, in eval() mode."""
    model.load_state_dict(torch.load(path, map_location=device))
    model.eval()
    return model
```

## STEP 6 — `ml/train.py`

```python
"""
Training script. Run manually: python -m app.ml.train
"""
import torch
import torch.nn as nn
from .dataset import get_dataloaders
from .model_utils import build_model, save_checkpoint
from ..config import MODELS_DIR

def dice_loss(pred, target, eps=1e-6):
    pred = torch.sigmoid(pred)
    intersection = (pred * target).sum()
    return 1 - (2 * intersection + eps) / (pred.sum() + target.sum() + eps)

def train_model(data_dir: str, epochs: int = 20, batch_size: int = 8, lr: float = 1e-4):
    """
    Input: data_dir (images/ + masks/ subfolders), epochs, batch_size, lr.
    Output: none — saves best checkpoint to MODELS_DIR / "unet_resnet34.pth"
    Logic: standard train loop, combined BCE + Dice loss (Dice alone is unstable early;
    BCE alone under-weights the (usually small) positive/slick class), track val loss,
    save whenever val loss improves.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    train_loader, val_loader = get_dataloaders(data_dir, batch_size)
    model = build_model().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    bce = nn.BCEWithLogitsLoss()
    best_val_loss = float("inf")

    for epoch in range(epochs):
        model.train()
        for imgs, masks in train_loader:
            imgs, masks = imgs.to(device), masks.to(device)
            optimizer.zero_grad()
            preds = model(imgs)
            loss = bce(preds, masks) + dice_loss(preds, masks)
            loss.backward()
            optimizer.step()

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for imgs, masks in val_loader:
                imgs, masks = imgs.to(device), masks.to(device)
                preds = model(imgs)
                val_loss += (bce(preds, masks) + dice_loss(preds, masks)).item()
        val_loss /= max(len(val_loader), 1)
        print(f"Epoch {epoch+1}/{epochs} — val_loss={val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            save_checkpoint(model, str(MODELS_DIR / "unet_resnet34.pth"))

if __name__ == "__main__":
    train_model(data_dir="data/raw/kaggle_oil_spill")
```

Once training is done, upload the `.pth` file to a shared Google Drive link (it's too large for git) and put the link + file size + a SHA256 checksum in `backend/data/models/README.md` so Person 1 (and Person 3, for reproducing your environment) can download it.

## STEP 7 — `ml/shape_features.py`

```python
"""
Deterministic geometric feature extraction — NOT machine learning, plain shapely math.
"""
from ..utils.geo import polygon_area_km2, polygon_perimeter_km, polygon_elongation
from shapely.geometry import shape

def compute_shape_features(polygon_geojson: dict) -> dict:
    """
    Input: GeoJSON polygon (or multipolygon) of the detected slick.
    Output:
        {
          "area_km2": float,
          "perimeter_km": float,
          "elongation": float,
          "fragment_count": int,     # number of separate polygons if MultiPolygon, else 1
          "age_class": str           # "fresh" | "aging" | "old"
        }
    Logic (rule-based thresholds, tune against visual inspection of training examples):
        - fragment_count > 1 and elongation > 3.0  -> "old"
        - elongation > 1.8 (but fragment_count == 1) -> "aging"
        - otherwise -> "fresh"
    """
    geom = shape(polygon_geojson)
    fragment_count = len(geom.geoms) if geom.geom_type == "MultiPolygon" else 1
    area = polygon_area_km2(polygon_geojson)
    perimeter = polygon_perimeter_km(polygon_geojson)
    elongation = polygon_elongation(polygon_geojson)

    if fragment_count > 1 and elongation > 3.0:
        age_class = "old"
    elif elongation > 1.8:
        age_class = "aging"
    else:
        age_class = "fresh"

    return {"area_km2": area, "perimeter_km": perimeter, "elongation": elongation,
            "fragment_count": fragment_count, "age_class": age_class}
```
**Important:** the exact thresholds (3.0, 1.8) are placeholders — visually inspect 10-15 examples from your training set, compute their actual elongation values, and pick thresholds that roughly separate compact-vs-elongated shapes in your specific dataset. Document what you chose and why in a comment.

## STEP 8 — `ml/infer.py` (the function everyone else depends on — build this last, once training + shape_features work)

```python
"""
Public interface: detect_slick(). This is the ONLY function other modules should import from ml/.
"""
import numpy as np
import rasterio
import cv2
import torch
from pathlib import Path
from .model_utils import build_model, load_checkpoint
from .shape_features import compute_shape_features
from ..utils.geo import geojson_polygon_from_mask
from ..config import MODELS_DIR

_MODEL_CACHE = {}

def _get_model():
    if "model" not in _MODEL_CACHE:
        model = build_model()
        model = load_checkpoint(model, str(MODELS_DIR / "unet_resnet34.pth"))
        _MODEL_CACHE["model"] = model
    return _MODEL_CACHE["model"]

def detect_slick(image_path: str, model=None) -> dict:
    """
    See exact contract in ARCHITECTURE.md §5.2.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"SAR image not found: {image_path}")

    with rasterio.open(path) as src:
        img = src.read([1, 1, 1] if src.count == 1 else [1, 2, 3])  # force 3-channel
        img = np.transpose(img, (1, 2, 0)).astype(np.float32)
        img = (img - img.min()) / max(img.max() - img.min(), 1e-6)
        transform = src.transform
        crs = str(src.crs)

    orig_h, orig_w = img.shape[:2]
    resized = cv2.resize(img, (256, 256))
    tensor = torch.from_numpy(resized).permute(2, 0, 1).unsqueeze(0).float()

    m = model or _get_model()
    with torch.no_grad():
        logits = m(tensor)
        probs = torch.sigmoid(logits).squeeze().numpy()

    confidence = float(probs[probs > 0.5].mean()) if (probs > 0.5).any() else 0.0
    if confidence == 0.0:
        raise RuntimeError("No slick-like region detected above confidence threshold")

    mask_resized = (probs > 0.5).astype(np.uint8)
    mask_full = cv2.resize(mask_resized, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)

    polygon_geojson = geojson_polygon_from_mask(mask_full, transform, crs)
    shape_features = compute_shape_features(polygon_geojson)

    mask_path = str(path.parent / f"{path.stem}_mask.png")
    cv2.imwrite(mask_path, mask_full * 255)

    return {
        "polygon_geojson": polygon_geojson,
        "confidence": confidence,
        "shape_features": shape_features,
        "mask_path": mask_path,
    }
```

**This function cannot be finished until `utils/geo.py:geojson_polygon_from_mask()` is really implemented by Person 1 (not the stub).** Write and unit-test everything else in this file first (model loading, inference, thresholding) using a temporary local mock of `geojson_polygon_from_mask` if needed, then swap to the real import once Person 1 has pushed it.

## STEP 9 — Tests: `backend/tests/test_detection.py`

- `test_build_model_output_shape` — build model, run a random tensor through it, assert output shape is `(1, 1, 256, 256)`.
- `test_dataset_loading` — point `OilSpillDataset` at a tiny fixture folder (2-3 sample image/mask pairs you commit under `backend/tests/fixtures/`), assert `__len__` and `__getitem__` output shapes/dtypes are correct.
- `test_shape_features_compact_square` — feed `compute_shape_features` a known square polygon, assert `elongation` is close to 1.0 and `age_class == "fresh"`.
- `test_shape_features_elongated_thin` — feed a known long thin rectangle, assert `elongation` is high and `age_class` is `"aging"` or `"old"`.
- `test_detect_slick_missing_file` — assert `FileNotFoundError` is raised for a nonexistent path.
- `test_detect_slick_on_demo_case` — (once weights + real `geo.py` are ready) run `detect_slick()` on the actual demo case SAR scene, assert the return dict has all required keys and `confidence > 0`.

---

## STEP 10 — Git workflow for your branch

```bash
git add app/ml/ tests/test_detection.py scripts/download_training_data.py requirements.txt data/models/README.md data/raw/README.md
git commit -m "[ml] add dataset, model, training pipeline"
git push -u origin person2/ml-setup
```
Open a PR into `main` titled `[ml] detection module`, describing which parts of the §5.2 contract are implemented. Push incremental commits/PRs as each piece (dataset → training → shape features → infer) becomes testable rather than one giant PR at the end. Person 1 reviews and merges.

Before starting new work each day: `git checkout main && git pull origin main && git checkout person2/ml-setup && git rebase main` (or merge, whichever the team prefers — just stay current).

---

## Completion Checklist

- [ ] Repository cloned, branch created
- [ ] Kaggle dataset downloaded, `download_training_data.py` works and is documented
- [ ] `ml/dataset.py` implemented and tested
- [ ] `ml/model_utils.py` implemented
- [ ] `ml/train.py` run to completion, checkpoint saved, uploaded, linked in `data/models/README.md`
- [ ] `ml/shape_features.py` implemented, thresholds tuned against real data, documented
- [ ] `ml/infer.py` implemented, returns the exact §5.2 contract shape
- [ ] Verified `detect_slick()` works on the actual chosen demo case SAR scene
- [ ] `tests/test_detection.py` written and passing
- [ ] Code committed, branch pushed, PR(s) created and merged
- [ ] Person 1 notified that `ml/infer.py` is ready for orchestrator integration (STEP 13 in PERSON_1.md)
