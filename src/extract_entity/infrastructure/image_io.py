"""Local image decoding at the infrastructure boundary."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from extract_entity.domain import ImageDocument


class ImageDecodeError(ValueError):
    """A local file could not be decoded as a supported image."""


def decode_image(path: str | Path) -> ImageDocument:
    """Decode a JPEG, PNG, or WebP file, apply EXIF orientation, and return RGB pixels."""

    source = Path(path)
    try:
        with Image.open(source) as opened:
            if opened.format not in {"JPEG", "PNG", "WEBP"}:
                raise ImageDecodeError(
                    f"unsupported image format for {source}: {opened.format or 'unknown'}"
                )
            opened.load()
            normalized = ImageOps.exif_transpose(opened).convert("RGB")
            width, height = normalized.size
            pixels = normalized.tobytes()
    except ImageDecodeError:
        raise
    except (
        FileNotFoundError,
        IsADirectoryError,
        PermissionError,
        OSError,
        UnidentifiedImageError,
    ) as exc:
        raise ImageDecodeError(f"could not decode image {source}: {exc}") from exc

    return ImageDocument(width=width, height=height, pixels=pixels)
