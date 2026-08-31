"""
Training script for the SAR oil-spill segmentation U-Net.

Run manually:  python -m app.ml.train --data-dir <path>
or with defaults targeting backend/data/raw/kaggle_oil_spill.
"""
import argparse

import torch
import torch.nn as nn

from ..config import MODELS_DIR
from .dataset import get_dataloaders
from .model_utils import CHECKPOINT_NAME, build_model, save_checkpoint


def dice_loss(pred, target, eps=1e-6):
    """Dice loss computed on sigmoid-activated predictions."""
    pred = torch.sigmoid(pred)
    # Flatten for element-wise reduction
    pred = pred.contiguous().view(pred.size(0), -1)
    target = target.contiguous().view(target.size(0), -1)
    intersection = (pred * target).sum(dim=1)
    return 1 - (2 * intersection + eps) / (pred.sum(dim=1) + target.sum(dim=1) + eps)


def train_model(data_dir: str, epochs: int = 20, batch_size: int = 8, lr: float = 1e-4):
    """
    Train the U-Net with combined BCE + Dice loss.

    data_dir: folder containing images/ and masks/ subfolders
    epochs / batch_size / lr: training hyperparameters
    Saves the best checkpoint (by validation loss) to MODELS_DIR / CHECKPOINT_NAME.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    train_loader, val_loader = get_dataloaders(data_dir, batch_size)
    model = build_model().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    bce = nn.BCEWithLogitsLoss()

    best_val_loss = float("inf")

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for imgs, masks in train_loader:
            imgs, masks = imgs.to(device), masks.to(device)
            optimizer.zero_grad()
            preds = model(imgs)
            loss = bce(preds, masks) + dice_loss(preds, masks).mean()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        train_loss = total_loss / max(len(train_loader), 1)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for imgs, masks in val_loader:
                imgs, masks = imgs.to(device), masks.to(device)
                preds = model(imgs)
                val_loss += (bce(preds, masks) + dice_loss(preds, masks).mean()).item()
        val_loss /= max(len(val_loader), 1)
        print(f"Epoch {epoch+1}/{epochs} — train_loss={train_loss:.4f} val_loss={val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            out_path = MODELS_DIR / CHECKPOINT_NAME
            save_checkpoint(model, str(out_path))
            print(f"  saved checkpoint -> {out_path}")

    print(f"Training complete. Best val loss: {best_val_loss:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the oil-spill U-Net")
    parser.add_argument("--data-dir", default="data/raw/kaggle_oil_spill")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=1e-4)
    args = parser.parse_args()
    train_model(
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
    )
