"""
Public interface: detect_slick().

This is the ONLY function other modules should import from ml/.
"""
from pathlib import Path

import cv2
import numpy as np
import rasterio
import torch

from ..config import MODELS_DIR
from ..utils.geo import geojson_polygon_from_mask
from .model_utils import CHECKPOINT_NAME, build_model, load_checkpoint
from .shape_features import compute_shape_features

_MODEL_CACHE = {}
_CONFIDENCE_THRESHOLD = 0.5


def _get_model():
    """Load (or return cached) default model with trained weights."""
    if "model" not in _MODEL_CACHE:
        weights_path = MODELS_DIR / CHECKPOINT_NAME
        if not weights_path.exists():
            raise FileNotFoundError(
                f"Trained weights not found at {weights_path}. "
                "Run training (python -m app.ml.train) or download from the "
                "link in backend/data/models/README.md."
            )
        model = build_model()
        model = load_checkpoint(model, str(weights_path))
        _MODEL_CACHE["model"] = model
    return _MODEL_CACHE["model"]


def detect_slick(image_path: str, model=None) -> dict:
    """
    Detect an oil slick in a Sentinel-1 GeoTIFF (or preprocessed PNG).

    See exact contract in ARCHITECTURE.md §5.2.

    Returns:
        {
          "polygon_geojson": dict,
          "confidence": float,          # mean softmax prob inside predicted mask
          "shape_features": { ... },
          "mask_path": str
        }

    Raises:
        FileNotFoundError if image_path does not exist
        RuntimeError if no slick-like region is detected above threshold
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"SAR image not found: {image_path}")

    with rasterio.open(path) as src:
        if src.count == 1:
            img = src.read(1)
            img = np.stack([img, img, img], axis=-1)
        else:
            img = src.read([1, 2, 3])
            img = np.transpose(img, (1, 2, 0)).astype(np.float32)
        transform = src.transform
        crs = str(src.crs)

    img = img.astype(np.float32)
    mn, mx = img.min(), img.max()
    img = (img - mn) / max(mx - mn, 1e-6)

    orig_h, orig_w = img.shape[:2]
    resized = cv2.resize(img, (256, 256))
    tensor = torch.from_numpy(resized).permute(2, 0, 1).unsqueeze(0).float()

    m = model or _get_model()
    with torch.no_grad():
        logits = m(tensor)
        probs = torch.sigmoid(logits).squeeze().numpy()

    positive = probs > _CONFIDENCE_THRESHOLD
    if not positive.any():
        raise RuntimeError("No slick-like region detected above confidence threshold")

    confidence = float(probs[positive].mean())

    mask_resized = positive.astype(np.uint8)
    mask_full = cv2.resize(
        mask_resized, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST
    ).astype(np.uint8)

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
