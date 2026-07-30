"""Canonical, model-independent image and mask value objects.

Coordinates are written as ``(x, y)``. Storage is flat row-major ``[y, x]``;
RGB adds three interleaved channels in ``RGBRGB...`` order. Width and height
always mean the dimensions after EXIF orientation correction.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from math import isfinite


def _validate_dimensions(width: int, height: int) -> None:
    if type(width) is not int or type(height) is not int:
        raise TypeError("width and height must have int dtype")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")


def _validate_bytes(values: bytes, *, length: int, name: str) -> None:
    if type(values) is not bytes:
        raise TypeError(f"{name} must have bytes dtype")
    if len(values) != length:
        raise ValueError(f"{name} length {len(values)} does not match expected {length}")


def _validate_float_values(values: tuple[float, ...], *, length: int, name: str) -> None:
    if type(values) is not tuple:
        raise TypeError(f"{name} must have tuple[float, ...] dtype")
    if len(values) != length:
        raise ValueError(f"{name} length {len(values)} does not match expected {length}")
    for value in values:
        if type(value) is not float:
            raise TypeError(f"{name} values must have float dtype")
        if not isfinite(value):
            raise ValueError(f"{name} values must be finite")
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} values must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class ImageDocument:
    """Normalized RGB image with interleaved unsigned 8-bit channel storage."""

    width: int
    height: int
    pixels: bytes

    def __post_init__(self) -> None:
        _validate_dimensions(self.width, self.height)
        _validate_bytes(self.pixels, length=self.width * self.height * 3, name="RGB pixels")

    @property
    def size(self) -> tuple[int, int]:
        """Return ``(width, height)`` after EXIF orientation correction."""

        return self.width, self.height

    def pixel_at(self, x: int, y: int) -> tuple[int, int, int]:
        """Return the RGB pixel at a coordinate expressed as ``(x, y)``."""

        if type(x) is not int or type(y) is not int:
            raise TypeError("pixel coordinates must have int dtype")
        if not 0 <= x < self.width or not 0 <= y < self.height:
            raise IndexError("pixel coordinate is outside the image")
        offset = (y * self.width + x) * 3
        return self.pixels[offset], self.pixels[offset + 1], self.pixels[offset + 2]


@dataclass(frozen=True, slots=True)
class RgbaImage:
    """Packed unsigned 8-bit straight-alpha pixels in ``RGBARGBA...`` order."""

    width: int
    height: int
    pixels: bytes

    def __post_init__(self) -> None:
        _validate_dimensions(self.width, self.height)
        _validate_bytes(self.pixels, length=self.width * self.height * 4, name="RGBA pixels")

    @property
    def size(self) -> tuple[int, int]:
        """Return the packed image size as ``(width, height)``."""

        return self.width, self.height

    def pixel_at(self, x: int, y: int) -> tuple[int, int, int, int]:
        """Return one straight-alpha RGBA pixel at an ``(x, y)`` coordinate."""

        if type(x) is not int or type(y) is not int:
            raise TypeError("pixel coordinates must have int dtype")
        if not 0 <= x < self.width or not 0 <= y < self.height:
            raise IndexError("pixel coordinate is outside the image")
        offset = (y * self.width + x) * 4
        return (
            self.pixels[offset],
            self.pixels[offset + 1],
            self.pixels[offset + 2],
            self.pixels[offset + 3],
        )


@dataclass(frozen=True, slots=True)
class ProbabilityMask:
    """Float foreground probabilities in row-major ``[y, x]`` order."""

    width: int
    height: int
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        _validate_dimensions(self.width, self.height)
        _validate_float_values(
            self.values,
            length=self.width * self.height,
            name="probability mask",
        )


@dataclass(frozen=True, slots=True)
class BinaryMask:
    """Binary foreground mask encoded as bytes containing only 0 and 1."""

    width: int
    height: int
    values: bytes

    def __post_init__(self) -> None:
        _validate_dimensions(self.width, self.height)
        _validate_bytes(self.values, length=self.width * self.height, name="binary mask")
        if any(value not in (0, 1) for value in self.values):
            raise ValueError("binary mask values must be 0 or 1")


class TrimapValue(IntEnum):
    """The only valid trimap categories and their canonical uint8 values."""

    BACKGROUND = 0
    UNKNOWN = 128
    FOREGROUND = 255


@dataclass(frozen=True, slots=True)
class Trimap:
    """Trimap encoded as bytes containing only 0, 128 and 255."""

    width: int
    height: int
    values: bytes

    def __post_init__(self) -> None:
        _validate_dimensions(self.width, self.height)
        _validate_bytes(self.values, length=self.width * self.height, name="trimap")
        allowed_values = {value.value for value in TrimapValue}
        if any(value not in allowed_values for value in self.values):
            raise ValueError("trimap values must be 0, 128 or 255")


@dataclass(frozen=True, slots=True)
class AlphaMatte:
    """Continuous float opacity values in row-major ``[y, x]`` order."""

    width: int
    height: int
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        _validate_dimensions(self.width, self.height)
        _validate_float_values(self.values, length=self.width * self.height, name="alpha matte")


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    """Minimum successful extraction result before RGBA composition."""

    image: ImageDocument
    alpha: AlphaMatte
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if type(self.image) is not ImageDocument:
            raise TypeError("result image must be an ImageDocument")
        if type(self.alpha) is not AlphaMatte:
            raise TypeError("result alpha must be an AlphaMatte")
        if self.image.size != (self.alpha.width, self.alpha.height):
            raise ValueError("result alpha size does not match image size")
        if type(self.warnings) is not tuple or any(
            type(warning) is not str for warning in self.warnings
        ):
            raise TypeError("result warnings must be a tuple of strings")
