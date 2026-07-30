"""Narrow trust boundaries around calls to model adapters."""

from extract_entity.domain import (
    AlphaMatte,
    ImageDocument,
    InteractiveSegmentationModel,
    MattingModel,
    SegmentationCandidate,
    SegmentationModel,
    SubjectPrompt,
    Trimap,
)


def _validate_image(image: ImageDocument) -> None:
    if type(image) is not ImageDocument:
        raise TypeError("image must be an ImageDocument")


def _validate_candidate(candidate: SegmentationCandidate, image: ImageDocument) -> None:
    if type(candidate) is not SegmentationCandidate:
        raise TypeError("segmentation model must return a SegmentationCandidate")
    if candidate.image_size != image.size:
        raise ValueError("segmentation candidate size does not match input image")


def run_segmentation(model: SegmentationModel, image: ImageDocument) -> SegmentationCandidate:
    """Call an automatic segmenter and validate its result against ``image``."""

    _validate_image(image)
    candidate = model.segment(image)
    _validate_candidate(candidate, image)
    return candidate


def run_interactive_segmentation(
    model: InteractiveSegmentationModel,
    image: ImageDocument,
    prompt: SubjectPrompt,
) -> SegmentationCandidate:
    """Validate prompts, call an interactive segmenter, and validate its result."""

    _validate_image(image)
    if type(prompt) is not SubjectPrompt:
        raise TypeError("prompt must be a SubjectPrompt")
    prompt.validate_for(image)
    candidate = model.segment(image, prompt)
    _validate_candidate(candidate, image)
    return candidate


def run_matting(model: MattingModel, image: ImageDocument, trimap: Trimap) -> AlphaMatte:
    """Validate matting inputs and output while preserving the returned object."""

    _validate_image(image)
    if type(trimap) is not Trimap:
        raise TypeError("trimap must be a Trimap")
    if (trimap.width, trimap.height) != image.size:
        raise ValueError("trimap size does not match input image")
    alpha = model.matte(image, trimap)
    if type(alpha) is not AlphaMatte:
        raise TypeError("matting model must return an AlphaMatte")
    if (alpha.width, alpha.height) != image.size:
        raise ValueError("alpha matte size does not match input image")
    return alpha
