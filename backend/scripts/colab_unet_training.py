"""
Colab-Ready Standalone Training Script for SAGAR-DRISHTI SAR Oil Spill U-Net.
Designed to run directly in Google Colab with free T4 GPU.

Usage in Colab:
    !pip install -q segmentation-models-pytorch rasterio opencv-python
    !python colab_unet_training.py --data-dir /content/dataset --epochs 20 --save-dir /content/drive/MyDrive/sagar_drishti_models
"""
import argparse
import os
from pathlib import Path
import cv2
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import segmentation_models_pytorch as smp


class OilSpillDataset(Dataset):
    def __init__(self, images_dir: str, masks_dir: str, image_size: int = 256):
        self.images_dir = Path(images_dir)
        self.masks_dir = Path(masks_dir)
        self.image_size = image_size
        self.filenames = sorted([
            f for f in os.listdir(self.images_dir)
            if (self.masks_dir / f).is_file() and f.endswith(('.png', '.jpg', '.tif'))
        ])

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        fname = self.filenames[idx]
        img = cv2.imread(str(self.images_dir / fname))
        if img is None:
            img = np.zeros((self.image_size, self.image_size, 3), dtype=np.uint8)
        img = cv2.resize(img, (self.image_size, self.image_size))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

        mask = cv2.imread(str(self.masks_dir / fname), cv2.IMREAD_GRAYSCALE)
        if mask is None:
            mask = np.zeros((self.image_size, self.image_size), dtype=np.uint8)
        mask = cv2.resize(mask, (self.image_size, self.image_size))
        mask = (mask > 127).astype(np.float32)

        img_t = torch.from_numpy(img).permute(2, 0, 1)
        mask_t = torch.from_numpy(mask).unsqueeze(0)
        return img_t, mask_t


def dice_loss(pred, target, eps=1e-6):
    pred = torch.sigmoid(pred).contiguous().view(pred.size(0), -1)
    target = target.contiguous().view(target.size(0), -1)
    intersection = (pred * target).sum(dim=1)
    return 1 - (2 * intersection + eps) / (pred.sum(dim=1) + target.sum(dim=1) + eps)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, help="Path containing images/ and masks/")
    parser.add_argument("--save-dir", default="./models", help="Directory to save .pth weights")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=1e-4)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[*] Training on device: {device}")

    data_path = Path(args.data_dir)
    full_ds = OilSpillDataset(str(data_path / "images"), str(data_path / "masks"))
    print(f"[*] Loaded {len(full_ds)} valid paired samples.")

    val_size = max(1, int(len(full_ds) * 0.15))
    train_ds, val_ds = torch.utils.data.random_split(full_ds, [len(full_ds) - val_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False)

    model = smp.Unet(
        encoder_name="resnet34",
        encoder_weights="imagenet",
        in_channels=3,
        classes=1,
        activation=None
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    bce = nn.BCEWithLogitsLoss()
    save_path = Path(args.save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    out_file = save_path / "unet_resnet34_oilspill.pth"

    best_val = float("inf")
    for epoch in range(args.epochs):
        model.train()
        t_loss = 0.0
        for imgs, masks in train_loader:
            imgs, masks = imgs.to(device), masks.to(device)
            optimizer.zero_grad()
            preds = model(imgs)
            loss = bce(preds, masks) + dice_loss(preds, masks).mean()
            loss.backward()
            optimizer.step()
            t_loss += loss.item()
        t_loss /= len(train_loader)

        model.eval()
        v_loss = 0.0
        with torch.no_grad():
            for imgs, masks in val_loader:
                imgs, masks = imgs.to(device), masks.to(device)
                preds = model(imgs)
                v_loss += (bce(preds, masks) + dice_loss(preds, masks).mean()).item()
        v_loss /= len(val_loader)

        print(f"Epoch {epoch+1:02d}/{args.epochs:02d} | Train Loss: {t_loss:.4f} | Val Loss: {v_loss:.4f}")
        if v_loss < best_val:
            best_val = v_loss
            torch.save(model.state_dict(), str(out_file))
            print(f"  --> Saved new best checkpoint to {out_file}")

    print(f"\n[✓] Training Complete. Best Val Loss: {best_val:.4f}")
    print(f"[✓] Weights saved to: {out_file}")


if __name__ == "__main__":
    main()
