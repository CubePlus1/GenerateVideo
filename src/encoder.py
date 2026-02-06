"""Image encoding utilities for video generation."""
import base64
from pathlib import Path

from src.config import MAX_IMAGE_SIZE, VALID_IMAGE_FORMATS
from src.errors import InvalidImageError


def encode_image_to_base64(image_path: Path) -> str:
    """
    Encode an image file to base64 string.

    Args:
        image_path: Path to the image file to encode.

    Returns:
        Base64-encoded string representation of the image.

    Raises:
        InvalidImageError: If file doesn't exist, has invalid format, or exceeds size limit.
    """
    # Validate file exists
    if not image_path.exists():
        raise InvalidImageError(f"Image file not found: {image_path}")

    # Validate file extension
    file_extension = image_path.suffix.lower()
    if file_extension not in VALID_IMAGE_FORMATS:
        supported = ", ".join(VALID_IMAGE_FORMATS)
        raise InvalidImageError(
            f"Invalid image format: {file_extension}. Supported: {supported}"
        )

    # Validate file size
    file_size = image_path.stat().st_size
    if file_size > MAX_IMAGE_SIZE:
        size_mb = file_size / (1024 * 1024)
        max_mb = MAX_IMAGE_SIZE / (1024 * 1024)
        raise InvalidImageError(
            f"Image file too large: {size_mb:.2f}MB. Maximum: {max_mb:.0f}MB"
        )

    # Read binary content and encode to base64
    with image_path.open('rb') as image_file:
        image_data = image_file.read()

    # Encode and return as UTF-8 string
    encoded = base64.b64encode(image_data)
    return encoded.decode('utf-8')
