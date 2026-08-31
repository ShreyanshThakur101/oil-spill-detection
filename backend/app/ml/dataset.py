"""
PyTorch Dataset wrapper for the oil-spill segmentation training data.
"""
import os
from pathlib import Path

import cv2
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset


class OilSpillDataset(Dataset):
    """
    Dataset of SAR image patches paired with binary segmentation masks.

    images_dir: folder of input images (SAR patches, grayscale or 3-channel)
    masks_dir:  folder of binary segmentation masks, same filenames as images
    image_size: resize target (e.g. 256), model expects square input

    __getitem__ returns (image_tensor, mask_tensor):
        image_tensor shape (3, H, W) float32 normalized 0-1
        mask_tensor  shape (1, H, W) float32 with values 0.0 or 1.0
    """

    def __init__(self, images_dir: str, masks_dir: str, image_size: int = 256):
        self.images_dir = Path(images_dir)
        self.masks_dir = Path(masks_dir)
        self.image_size = image_size
        self.filenames = self._collect_filenames()

    def _collect_filenames(self) -> list:
        """Only keep filenames present in both images and masks dirs; skip corrupt/missing."""
        names = []
        if not self.images_dir.is_dir() or not self.masks_dir.is_dir():
            raise ValueError(f"Dataset directories must exist: {self.images_dir}, {self.masks_dir}")
        for fname in sorted(os.listdir(self.images_dir)):
            if not (self.images_dir / fname).is_file():
                continue
            if not (self.masks_dir / fname).is_file():
                print(f"WARNING: {fname} has no corresponding mask in {self.masks_dir}; skipping")
                continue
            names.append(fname)
        return names

    def __len__(self) -> int:
        return len(self.filenames)

    def __getitem__(self, idx: int):
        if idx < 0 or idx >= len(self.filenames):
            raise IndexError("Index out of range")

        fname = self.filenames[idx]

        img = cv2.imread(str(self.images_dir / fname))
        if img is None:
            print(f"WARNING: could not read image {self.images_dir / fname}; returning all-black")
            img = np.zeros((self.image_size, self.image_size, 3), dtype=np.uint8)
        img = cv2.resize(img, (self.image_size, self.image_size))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

        mask = cv2.imread(str(self.masks_dir / fname), cv2.IMREAD_GRAYSCALE)
        if mask is None:
            print(f"WARNING: could not read mask {self.masks_dir / fname}; returning all-zero")
            mask = np.zeros((self.image_size, self.image_size), dtype=np.uint8)
        mask = cv2.resize(mask, (self.image_size, self.image_size))
        mask = (mask > 127).astype(np.float32)

        img_t = torch.from_numpy(img).permute(2, 0, 1)          # (3,H,W)
        mask_t = torch.from_numpy(mask).unsqueeze(0)            # (1,H,W)
        return img_t, mask_t


def get_dataloaders(data_dir: str, batch_size: int = 8, val_split: float = 0.15):
    """
    Build train/val split and wrap in DataLoader objects.

    data_dir:  contains images/ and masks/ subfolders
    batch_size: batch size
    val_split: fraction of data held out for validation
    Returns:   (train_loader, val_loader)
    """
    data_path = Path(data_dir)
    images_dir = data_path / "images"
    masks_dir = data_path / "masks"
    if not images_dir.is_dir() or not masks_dir.is_dir():
        raise ValueError(
            f"Expected data_dir with 'images/' and 'masks/' subfolders, got {data_dir}"
        )

    full_dataset = OilSpillDataset(str(images_dir), str(masks_dir))
    if len(full_dataset) == 0:
        raise ValueError("No valid image/mask pairs found in dataset directory")

    val_size = int(len(full_dataset) * val_split)
    val_size = max(1, val_size)
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = torch.utils.data.random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader
