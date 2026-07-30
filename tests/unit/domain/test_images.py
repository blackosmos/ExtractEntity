from collections.abc import Callable
from dataclasses import FrozenInstanceError
from math import inf, nan

import pytest

from extract_entity.domain import (
    AlphaMatte,
    BinaryMask,
    ExtractionResult,
    ImageDocument,
    ProbabilityMask,
    RgbaImage,
    Trimap,
    TrimapValue,
)

FloatContract = Callable[[int, int, tuple[float, ...]], object]


def test_image_uses_rgb_row_major_coordinates() -> None:
    image = ImageDocument(2, 1, bytes((1, 2, 3, 4, 5, 6)))

    assert image.size == (2, 1)
    assert image.pixel_at(0, 0) == (1, 2, 3)
    assert image.pixel_at(1, 0) == (4, 5, 6)


@pytest.mark.parametrize("width,height", [(0, 1), (1, 0), (-1, 1)])
def test_dimensions_must_be_positive(width: int, height: int) -> None:
    with pytest.raises(ValueError, match="positive"):
        ImageDocument(width, height, b"")


@pytest.mark.parametrize("width,height", [(True, 1), (1, 1.0)])
def test_dimensions_require_exact_integer_dtype(width: object, height: object) -> None:
    with pytest.raises(TypeError, match="int dtype"):
        ImageDocument(width, height, b"")  # type: ignore[arg-type]


def test_image_rejects_wrong_shape_and_dtype() -> None:
    with pytest.raises(ValueError, match="expected 6"):
        ImageDocument(2, 1, bytes((1, 2, 3)))
    with pytest.raises(TypeError, match="bytes dtype"):
        ImageDocument(1, 1, (1, 2, 3))  # type: ignore[arg-type]


def test_image_is_immutable_and_checks_coordinates() -> None:
    image = ImageDocument(1, 1, bytes((1, 2, 3)))
    with pytest.raises(FrozenInstanceError):
        image.width = 2  # type: ignore[misc]
    with pytest.raises(IndexError, match="outside"):
        image.pixel_at(1, 0)
    with pytest.raises(TypeError, match="int dtype"):
        image.pixel_at(True, 0)  # type: ignore[arg-type]


def test_rgba_image_uses_packed_row_major_straight_alpha_pixels() -> None:
    image = RgbaImage(2, 1, bytes((1, 2, 3, 4, 5, 6, 7, 8)))
    assert image.size == (2, 1)
    assert image.pixel_at(0, 0) == (1, 2, 3, 4)
    assert image.pixel_at(1, 0) == (5, 6, 7, 8)


def test_rgba_image_strictly_validates_dimensions_storage_and_coordinates() -> None:
    with pytest.raises(ValueError, match="positive"):
        RgbaImage(0, 1, b"")
    with pytest.raises(TypeError, match="int dtype"):
        RgbaImage(True, 1, b"")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="bytes dtype"):
        RgbaImage(1, 1, (1, 2, 3, 4))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="expected 4"):
        RgbaImage(1, 1, b"\x00\x00\x00")

    image = RgbaImage(1, 1, b"\x01\x02\x03\x04")
    with pytest.raises(FrozenInstanceError):
        image.pixels = b""  # type: ignore[misc]
    with pytest.raises(IndexError, match="outside"):
        image.pixel_at(1, 0)
    with pytest.raises(TypeError, match="int dtype"):
        image.pixel_at(0.0, 0)  # type: ignore[arg-type]


@pytest.mark.parametrize("contract", [ProbabilityMask, AlphaMatte])
def test_float_contract_accepts_boundary_values(contract: FloatContract) -> None:
    value = contract(2, 1, (0.0, 1.0))
    assert value.width == 2  # type: ignore[attr-defined]


@pytest.mark.parametrize("contract", [ProbabilityMask, AlphaMatte])
@pytest.mark.parametrize("value", [nan, inf, -inf])
def test_float_contract_rejects_non_finite_values(contract: FloatContract, value: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        contract(1, 1, (value,))


@pytest.mark.parametrize("contract", [ProbabilityMask, AlphaMatte])
@pytest.mark.parametrize("value", [-0.01, 1.01])
def test_float_contract_rejects_out_of_range_values(contract: FloatContract, value: float) -> None:
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        contract(1, 1, (value,))


@pytest.mark.parametrize("contract", [ProbabilityMask, AlphaMatte])
def test_float_contract_rejects_wrong_shape_and_dtype(contract: FloatContract) -> None:
    with pytest.raises(ValueError, match="expected 2"):
        contract(2, 1, (0.0,))
    with pytest.raises(TypeError, match="float dtype"):
        contract(1, 1, (1,))
    with pytest.raises(TypeError, match=r"tuple\[float"):
        contract(1, 1, [1.0])  # type: ignore[arg-type]


def test_binary_mask_accepts_only_bytes_zero_and_one() -> None:
    assert BinaryMask(2, 1, b"\x00\x01").values == b"\x00\x01"
    with pytest.raises(ValueError, match="0 or 1"):
        BinaryMask(1, 1, b"\x02")
    with pytest.raises(TypeError, match="bytes dtype"):
        BinaryMask(1, 1, (True,))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="expected 2"):
        BinaryMask(2, 1, b"\x00")


def test_trimap_accepts_exactly_three_canonical_values() -> None:
    values = bytes((TrimapValue.BACKGROUND, TrimapValue.UNKNOWN, TrimapValue.FOREGROUND))
    assert Trimap(3, 1, values).values == b"\x00\x80\xff"
    with pytest.raises(ValueError, match="0, 128 or 255"):
        Trimap(1, 1, b"\x7f")
    with pytest.raises(TypeError, match="bytes dtype"):
        Trimap(1, 1, (TrimapValue.UNKNOWN,))  # type: ignore[arg-type]


def test_extraction_result_requires_spatial_alignment() -> None:
    image = ImageDocument(2, 1, bytes(6))
    alpha = AlphaMatte(2, 1, (0.0, 1.0))

    result = ExtractionResult(image, alpha, ("review edge",))

    assert result.image is image
    assert result.alpha is alpha
    assert result.warnings == ("review edge",)

    with pytest.raises(ValueError, match="size does not match"):
        ExtractionResult(image, AlphaMatte(1, 1, (1.0,)))


def test_extraction_result_rejects_wrong_types() -> None:
    image = ImageDocument(1, 1, bytes(3))
    alpha = AlphaMatte(1, 1, (1.0,))
    with pytest.raises(TypeError, match="ImageDocument"):
        ExtractionResult(object(), alpha)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="AlphaMatte"):
        ExtractionResult(image, object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="tuple of strings"):
        ExtractionResult(image, alpha, ["warning"])  # type: ignore[arg-type]
