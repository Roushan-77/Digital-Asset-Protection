from pathlib import Path

import cv2
import imagehash
from PIL import Image


def generate_perceptual_hash(image_path: str | Path) -> str:
    path = Path(image_path)

    # OpenCV validates that the file is readable as an image before hashing.
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError("Unsupported or corrupted image.")

    with Image.open(path) as pil_image:
        return str(imagehash.phash(pil_image.convert("RGB")))


def compare_hashes(hash_a: str, hash_b: str) -> int:
    return imagehash.hex_to_hash(hash_a) - imagehash.hex_to_hash(hash_b)
