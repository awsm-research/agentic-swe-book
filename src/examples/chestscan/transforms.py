# transforms.py — shared between training and serving
# Defining transforms here ensures training and inference use IDENTICAL preprocessing.
# Import this module in both train.py and backend/main.py.

from torchvision import transforms

IMAGE_SIZE = 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]


def get_train_transforms() -> transforms.Compose:
    """Augmentation pipeline for training.

    Applies random geometric and colour augmentations to improve generalisation.
    All operations are deterministic given a fixed torch seed — reproducible across runs.
    """
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE + 32, IMAGE_SIZE + 32)),
        transforms.RandomCrop(IMAGE_SIZE),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_val_transforms() -> transforms.Compose:
    """Deterministic transforms for validation, test, and inference.

    Never augment at evaluation time — augmentation introduces randomness
    that makes evaluation metrics irreproducible.
    """
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
