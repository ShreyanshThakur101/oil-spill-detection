"""
Downloads the Kaggle oil-spill segmentation dataset into backend/data/raw/kaggle_oil_spill/.

Dataset: "Deep-SAR Oil Spill Segmentation (Refined)"
    https://www.kaggle.com/datasets/bakhtiyar2222/deep-sar-oil-spill-segmentation-refined

This dataset was selected (over alternatives) because it provides PAIRED grayscale
SAR images and BINARY SEGMENTATION MASKS (oil = white/1, background = black/0),
which is exactly the supervision our U-Net requires. Several other "oil spill"
Kaggle datasets (e.g. the CSIRO-based 'sentinel-1-sar-oil-spill-detection-dataset')
are binary CLASSIFICATION datasets with NO segmentation masks — those would change
the training approach and are not suitable here.

Requires a Kaggle API token (~/.kaggle/kaggle.json) — see Kaggle account settings.
Run manually: python backend/scripts/download_training_data.py
"""
import shutil
import subprocess
import zipfile
from pathlib import Path

DATASET_SLUG = "bakhtiyar2222/deep-sar-oil-spill-segmentation-refined"

TARGET_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "kaggle_oil_spill"
DOWNLOAD_DIR = TARGET_DIR / "_download"


def _unzip_to_layout() -> None:
    """Move the downloaded images/masks into the images/ and masks/ subfolders expected by ml/dataset.py."""
    images_src = DOWNLOAD_DIR / "images"
    masks_src = DOWNLOAD_DIR / "masks"

    # Some versions nest the images under images/images
    if not images_src.is_dir() and (DOWNLOAD_DIR / "images" / "images").is_dir():
        images_src = DOWNLOAD_DIR / "images" / "images"

    for name, src in (("images", images_src), ("masks", masks_src)):
        if not src.is_dir():
            raise RuntimeError(f"Expected '{name}' folder in download layout, not found in {DOWNLOAD_DIR}")
        dst = TARGET_DIR / name
        dst.mkdir(parents=True, exist_ok=True)
        for f in src.iterdir():
            if f.is_file():
                shutil.copy2(f, dst / f.name)
    print(f"Organized images and masks into {TARGET_DIR}")


def main():
    if shutil.which("kaggle") is None:
        raise RuntimeError(
            "The 'kaggle' CLI is not installed. Install it with 'pip install kaggle' "
            "and configure your API token at ~/.kaggle/kaggle.json first."
        )

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "kaggle",
            "datasets",
            "download",
            "-d",
            DATASET_SLUG,
            "-p",
            str(DOWNLOAD_DIR),
            "--unzip",
        ],
        check=True,
    )
    print(f"Downloaded dataset raw files to {DOWNLOAD_DIR}")

    _unzip_to_layout()

    # Clean up the intermediate download folder
    shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)
    print(f"Done. Training data ready at {TARGET_DIR} (images/ + masks/)")


if __name__ == "__main__":
    main()
