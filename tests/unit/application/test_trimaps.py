import math

import pytest

from extract_entity.application import TrimapThresholds, probability_mask_to_trimap
from extract_entity.domain import ProbabilityMask, TrimapValue


def test_probability_mask_to_trimap_maps_boundaries_and_preserves_non_square_size() -> None:
    mask = ProbabilityMask(
        width=3,
        height=2,
        values=(0.0, 0.2, 0.5, 0.8, 1.0, 0.21),
    )

    trimap = probability_mask_to_trimap(mask, TrimapThresholds(background=0.2, foreground=0.8))

    assert (trimap.width, trimap.height) == (3, 2)
    assert trimap.values == bytes(
        (
            TrimapValue.BACKGROUND,
            TrimapValue.BACKGROUND,
            TrimapValue.UNKNOWN,
            TrimapValue.FOREGROUND,
            TrimapValue.FOREGROUND,
            TrimapValue.UNKNOWN,
        )
    )


@pytest.mark.parametrize("field", ["background", "foreground"])
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_thresholds_reject_non_finite_values(field: str, value: float) -> None:
    values = {"background": 0.2, "foreground": 0.8, field: value}
    with pytest.raises(ValueError, match="finite"):
        TrimapThresholds(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("background", "foreground", "message"),
    [
        (-0.1, 0.8, r"\[0, 1\]"),
        (0.2, 1.1, r"\[0, 1\]"),
        (0.5, 0.5, "less than"),
        (0.8, 0.2, "less than"),
    ],
)
def test_thresholds_reject_invalid_ranges(
    background: float, foreground: float, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        TrimapThresholds(background=background, foreground=foreground)


@pytest.mark.parametrize("value", [0, True, "0.1", None])
def test_thresholds_reject_non_float_types(value: object) -> None:
    with pytest.raises(TypeError, match="float dtype"):
        TrimapThresholds(background=value, foreground=0.9)  # type: ignore[arg-type]


def test_conversion_rejects_wrong_input_types() -> None:
    mask = ProbabilityMask(width=1, height=1, values=(0.5,))
    with pytest.raises(TypeError, match="ProbabilityMask"):
        probability_mask_to_trimap(object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="TrimapThresholds"):
        probability_mask_to_trimap(mask, object())  # type: ignore[arg-type]
