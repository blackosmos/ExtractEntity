from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from PIL import Image

from extract_entity.infrastructure import ImageDecodeError, decode_image


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _save_oriented_jpeg(path: Path, orientation: int) -> None:
    image = Image.new("RGB", (3, 2))
    colors = (
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
    )
    for index, color in enumerate(colors):
        image.putpixel((index % 3, index // 3), color)
    exif = Image.Exif()
    exif[274] = orientation
    image.save(path, format="JPEG", quality=100, subsampling=0, exif=exif)


@pytest.mark.parametrize(
    ("orientation", "expected_size"),
    [(1, (3, 2)), (3, (3, 2)), (6, (2, 3)), (8, (2, 3))],
)
def test_decode_applies_exif_without_modifying_source(
    tmp_path: Path, orientation: int, expected_size: tuple[int, int]
) -> None:
    path = tmp_path / f"orientation-{orientation}.jpg"
    _save_oriented_jpeg(path, orientation)
    before = _digest(path)

    document = decode_image(path)

    assert document.size == expected_size
    assert _digest(path) == before


@pytest.mark.parametrize(("mode", "suffix"), [("RGB", ".png"), ("RGBA", ".png"), ("L", ".webp")])
def test_decode_normalizes_supported_modes_to_rgb(tmp_path: Path, mode: str, suffix: str) -> None:
    path = tmp_path / f"input{suffix}"
    color: int | tuple[int, ...] = (
        96 if mode == "L" else ((10, 20, 30, 40) if mode == "RGBA" else (10, 20, 30))
    )
    Image.new(mode, (2, 1), color).save(path)

    document = decode_image(path)

    assert document.size == (2, 1)
    assert len(document.pixels) == 6


def test_decode_reports_missing_and_corrupt_files(tmp_path: Path) -> None:
    corrupt = tmp_path / "corrupt.png"
    corrupt.write_bytes(b"not an image")

    with pytest.raises(ImageDecodeError, match="could not decode image"):
        decode_image(corrupt)
    with pytest.raises(ImageDecodeError, match="could not decode image"):
        decode_image(tmp_path / "missing.png")


def test_decode_rejects_unsupported_decodable_format(tmp_path: Path) -> None:
    path = tmp_path / "input.bmp"
    Image.new("RGB", (1, 1), (1, 2, 3)).save(path)

    with pytest.raises(ImageDecodeError, match="unsupported image format"):
        decode_image(path)
