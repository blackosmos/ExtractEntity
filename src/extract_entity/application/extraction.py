"""Synchronous, in-memory M0 extraction pipeline."""

from extract_entity.domain import (
    ExtractionResult,
    ImageDocument,
    MattingModel,
    SegmentationModel,
)

from .model_calls import run_matting, run_segmentation
from .trimaps import DEFAULT_TRIMAP_THRESHOLDS, TrimapThresholds, probability_mask_to_trimap


def extract_image(
    image: ImageDocument,
    segmentation_model: SegmentationModel,
    matting_model: MattingModel,
    thresholds: TrimapThresholds = DEFAULT_TRIMAP_THRESHOLDS,
) -> ExtractionResult:
    """Run automatic segmentation, baseline trimap conversion, and matting once."""

    if type(thresholds) is not TrimapThresholds:
        raise TypeError("thresholds must be TrimapThresholds")
    candidate = run_segmentation(segmentation_model, image)
    trimap = probability_mask_to_trimap(candidate.mask, thresholds)
    alpha = run_matting(matting_model, image, trimap)
    return ExtractionResult(image=image, alpha=alpha)
