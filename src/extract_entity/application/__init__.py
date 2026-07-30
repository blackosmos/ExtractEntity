"""Application-level use-case boundaries."""

from .composition import compose_straight_alpha_rgba
from .extraction import extract_image
from .model_calls import run_interactive_segmentation, run_matting, run_segmentation
from .trimaps import DEFAULT_TRIMAP_THRESHOLDS, TrimapThresholds, probability_mask_to_trimap

__all__ = [
    "DEFAULT_TRIMAP_THRESHOLDS",
    "TrimapThresholds",
    "compose_straight_alpha_rgba",
    "extract_image",
    "probability_mask_to_trimap",
    "run_interactive_segmentation",
    "run_matting",
    "run_segmentation",
]
