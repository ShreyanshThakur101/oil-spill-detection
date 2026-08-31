"""
Model construction and checkpoint I/O helpers.
"""
import segmentation_models_pytorch as smp
import torch

# Canonical filename of the trained weights, referenced by train.py and infer.py
# and documented in backend/data/models/README.md
CHECKPOINT_NAME = "unet_resnet34_oilspill.pth"


def build_model():
    """
    Build a segmentation_models_pytorch Unet with a ResNet34 encoder,
    pretrained on ImageNet, 3 input channels, 1 output channel (binary logits).
    """
    return smp.Unet(
        encoder_name="resnet34",
        encoder_weights="imagenet",
        in_channels=3,
        classes=1,
        activation=None,
    )


def save_checkpoint(model, path: str):
    """Save model.state_dict() to the given path."""
    torch.save(model.state_dict(), path)


def load_checkpoint(model, path: str, device: str = "cpu"):
    """Load weights into a model instance and return it in eval() mode."""
    model.load_state_dict(torch.load(path, map_location=device))
    model.eval()
    return model
