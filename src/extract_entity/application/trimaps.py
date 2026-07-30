"""Deterministic M0 conversion from probabilities to trimap categories."""

from dataclasses import dataclass
from math import isfinite

from extract_entity.domain import ProbabilityMask, Trimap, TrimapValue


@dataclass(frozen=True, slots=True)
class TrimapThresholds:
    """Validated inclusive boundary thresholds for the M0 trimap baseline."""

    background: float = 0.1
    foreground: float = 0.9

    def __post_init__(self) -> None:
        if type(self.background) is not float or type(self.foreground) is not float:
            raise TypeError("trimap thresholds must have float dtype")
        if not isfinite(self.background) or not isfinite(self.foreground):
            raise ValueError("trimap thresholds must be finite")
        if not 0.0 <= self.background <= 1.0 or not 0.0 <= self.foreground <= 1.0:
            raise ValueError("trimap thresholds must be in [0, 1]")
        if self.background >= self.foreground:
            raise ValueError("background threshold must be less than foreground threshold")


DEFAULT_TRIMAP_THRESHOLDS = TrimapThresholds()


def probability_mask_to_trimap(
    mask: ProbabilityMask,
    thresholds: TrimapThresholds = DEFAULT_TRIMAP_THRESHOLDS,
) -> Trimap:
    """Map probabilities to background, unknown, or foreground deterministically.

    Values equal to the background boundary are background; values equal to the
    foreground boundary are foreground. Values strictly between them are unknown.
    """

    if type(mask) is not ProbabilityMask:
        raise TypeError("mask must be a ProbabilityMask")
    if type(thresholds) is not TrimapThresholds:
        raise TypeError("thresholds must be TrimapThresholds")

    values = bytes(
        TrimapValue.BACKGROUND
        if value <= thresholds.background
        else TrimapValue.FOREGROUND
        if value >= thresholds.foreground
        else TrimapValue.UNKNOWN
        for value in mask.values
    )
    return Trimap(width=mask.width, height=mask.height, values=values)
