"""Pure in-memory composition at the 8-bit straight-alpha export boundary."""

from math import floor

from extract_entity.domain import AlphaMatte, ImageDocument, RgbaImage


def _alpha_to_u8(value: float) -> int:
    """Quantize normalized alpha with round-half-up rather than bankers rounding."""

    return floor(value * 255.0 + 0.5)


def compose_straight_alpha_rgba(image: ImageDocument, alpha: AlphaMatte) -> RgbaImage:
    """Interleave original RGB bytes and aligned alpha without premultiplication."""

    if type(image) is not ImageDocument:
        raise TypeError("image must be an ImageDocument")
    if type(alpha) is not AlphaMatte:
        raise TypeError("alpha must be an AlphaMatte")
    if image.size != (alpha.width, alpha.height):
        raise ValueError("alpha matte size does not match image size")

    rgba = bytearray(image.width * image.height * 4)
    for index, alpha_value in enumerate(alpha.values):
        rgb_offset = index * 3
        rgba_offset = index * 4
        rgba[rgba_offset : rgba_offset + 3] = image.pixels[rgb_offset : rgb_offset + 3]
        rgba[rgba_offset + 3] = _alpha_to_u8(alpha_value)
    return RgbaImage(width=image.width, height=image.height, pixels=bytes(rgba))
