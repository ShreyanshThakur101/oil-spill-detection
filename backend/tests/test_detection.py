"""
Unit tests for the detection module (Person 2): ml/dataset.py, ml/model_utils.py,
ml/shape_features.py, ml/infer.py.
"""
import numpy as np
import pytest
import torch

from app.ml.dataset import OilSpillDataset, get_dataloaders
from app.ml.infer import detect_slick
from app.ml.model_utils import build_model, load_checkpoint, save_checkpoint
from app.ml.shape_features import compute_shape_features


# --------------------------------------------------------------------------- #
# Model construction
# --------------------------------------------------------------------------- #
def test_build_model_output_shape():
    model = build_model()
    x = torch.randn(1, 3, 256, 256)
    with torch.no_grad():
        out = model(x)
    assert out.shape == (1, 1, 256, 256)


def test_checkpoint_roundtrip(tmp_path):
    model = build_model()
    path = str(tmp_path / "ckpt.pth")
    save_checkpoint(model, path)
    loaded = build_model()
    loaded = load_checkpoint(loaded, path)
    model.eval()  # match eval mode so batchnorm normalizes identically
    with torch.no_grad():
        x = torch.randn(1, 3, 256, 256)
        assert torch.allclose(model(x), loaded(x), atol=1e-6)


# --------------------------------------------------------------------------- #
# Dataset loading
# --------------------------------------------------------------------------- #
def _make_fixture_images(tmp_path, n=3, image_size=64):
    """Create tiny paired image/mask folders as a fixture."""
    images_dir = tmp_path / "images"
    masks_dir = tmp_path / "masks"
    images_dir.mkdir()
    masks_dir.mkdir()
    for i in range(n):
        img = np.random.randint(0, 255, (image_size, image_size, 3), dtype=np.uint8)
        mask = np.zeros((image_size, image_size), dtype=np.uint8)
        mask[10:20, 10:20] = 255
        import cv2
        cv2.imwrite(str(images_dir / f"img_{i:03d}.png"), img)
        cv2.imwrite(str(masks_dir / f"img_{i:03d}.png"), mask)
    return images_dir, masks_dir


def test_dataset_loading(tmp_path):
    images_dir, masks_dir = _make_fixture_images(tmp_path)
    ds = OilSpillDataset(str(images_dir), str(masks_dir), image_size=64)
    assert len(ds) == 3
    img, mask = ds[0]
    assert img.shape == (3, 64, 64)
    assert img.dtype == torch.float32
    assert mask.shape == (1, 64, 64)
    assert mask.dtype == torch.float32
    assert set(np.unique(mask.numpy())).issubset({0.0, 1.0})


def test_dataset_skips_missing_mask(tmp_path):
    images_dir = tmp_path / "images"
    masks_dir = tmp_path / "masks"
    images_dir.mkdir()
    masks_dir.mkdir()
    import cv2
    cv2.imwrite(str(images_dir / "a.png"), np.zeros((16, 16, 3), dtype=np.uint8))
    cv2.imwrite(str(images_dir / "b.png"), np.zeros((16, 16, 3), dtype=np.uint8))
    cv2.imwrite(str(masks_dir / "a.png"), np.zeros((16, 16), dtype=np.uint8))
    # 'b' has no mask -> should be skipped with a warning
    ds = OilSpillDataset(str(images_dir), str(masks_dir), image_size=16)
    assert len(ds) == 1


def test_get_dataloaders_empty_dir_raises(tmp_path):
    images_dir = tmp_path / "images"
    masks_dir = tmp_path / "masks"
    images_dir.mkdir()
    masks_dir.mkdir()
    with pytest.raises(ValueError):
        get_dataloaders(str(tmp_path), batch_size=2)


# --------------------------------------------------------------------------- #
# Shape features
# --------------------------------------------------------------------------- #
def _square_geojson_around(lon, lat, size_deg):
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [lon, lat],
                [lon + size_deg, lat],
                [lon + size_deg, lat + size_deg],
                [lon, lat + size_deg],
                [lon, lat],
            ]
        ],
    }


def test_shape_features_compact_square():
    sq = _square_geojson_around(75.0, 10.0, 0.05)
    feats = compute_shape_features(sq)
    assert "area_km2" in feats
    assert "perimeter_km" in feats
    assert "elongation" in feats
    assert "fragment_count" in feats
    assert 1.0 <= feats["elongation"] < 1.15
    assert feats["fragment_count"] == 1
    assert feats["age_class"] == "fresh"


def test_shape_features_elongated_thin():
    # A long thin rectangle -> high elongation -> "aging"
    rect = {
        "type": "Polygon",
        "coordinates": [
            [
                [75.0, 10.0],
                [75.5, 10.0],
                [75.5, 10.03],
                [75.0, 10.03],
                [75.0, 10.0],
            ]
        ],
    }
    feats = compute_shape_features(rect)
    assert feats["elongation"] > 5.0
    assert feats["fragment_count"] == 1
    assert feats["age_class"] == "aging"


# --------------------------------------------------------------------------- #
# Inference
# --------------------------------------------------------------------------- #
def test_detect_slick_missing_file():
    with pytest.raises(FileNotFoundError):
        detect_slick("does/not/exist.tif")
