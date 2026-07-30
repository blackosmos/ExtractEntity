from math import nextafter

import pytest

from extract_entity.application import compose_straight_alpha_rgba
from extract_entity.domain import AlphaMatte, ImageDocument


def test_composition_preserves_non_square_size_and_row_major_rgba_order() -> None:
    image = ImageDocument(
        width=3,
        height=2,
        pixels=bytes(
            (
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
            )
        ),
    )
    alpha = AlphaMatte(3, 2, (0.0, 1.0, 0.5, 0.25, 0.75, 2.5 / 255.0))

    result = compose_straight_alpha_rgba(image, alpha)

    assert result.size == image.size
    assert result.pixels == bytes(
        (
            1,
            2,
            3,
            0,
            4,
            5,
            6,
            255,
            7,
            8,
            9,
            128,
            10,
            11,
            12,
            64,
            13,
            14,
            15,
            191,
            16,
            17,
            18,
            3,
        )
    )


def test_composition_is_straight_alpha_and_never_premultiplies_rgb() -> None:
    image = ImageDocument(2, 1, bytes((250, 100, 50, 25, 200, 75)))
    result = compose_straight_alpha_rgba(image, AlphaMatte(2, 1, (0.0, 0.5)))
    assert result.pixel_at(0, 0) == (250, 100, 50, 0)
    assert result.pixel_at(1, 0) == (25, 200, 75, 128)


def test_alpha_quantization_is_round_half_up_on_and_around_half_boundary() -> None:
    midpoint = 2.5 / 255.0
    below = nextafter(midpoint, 0.0)
    above = nextafter(midpoint, 1.0)
    image = ImageDocument(3, 1, bytes(9))
    result = compose_straight_alpha_rgba(image, AlphaMatte(3, 1, (below, midpoint, above)))
    assert tuple(result.pixels[3::4]) == (2, 3, 3)


def test_composition_rejects_wrong_types_before_processing() -> None:
    image = ImageDocument(1, 1, bytes(3))
    alpha = AlphaMatte(1, 1, (1.0,))
    with pytest.raises(TypeError, match="ImageDocument"):
        compose_straight_alpha_rgba(object(), alpha)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="AlphaMatte"):
        compose_straight_alpha_rgba(image, object())  # type: ignore[arg-type]


def test_composition_rejects_spatial_mismatch_before_allocating_result() -> None:
    image = ImageDocument(2, 1, bytes(6))
    with pytest.raises(ValueError, match="size does not match"):
        compose_straight_alpha_rgba(image, AlphaMatte(1, 1, (1.0,)))
