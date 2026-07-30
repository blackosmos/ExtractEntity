"""Model-independent domain data contracts."""

from .images import (
    AlphaMatte,
    BinaryMask,
    ExtractionResult,
    ImageDocument,
    ProbabilityMask,
    RgbaImage,
    Trimap,
    TrimapValue,
)
from .models import (
    BoxPrompt,
    InteractiveSegmentationModel,
    MattingModel,
    ModelIdentity,
    PointKind,
    PointPrompt,
    SegmentationCandidate,
    SegmentationModel,
    SubjectPrompt,
)

__all__ = [
    "AlphaMatte",
    "BinaryMask",
    "BoxPrompt",
    "ExtractionResult",
    "ImageDocument",
    "InteractiveSegmentationModel",
    "MattingModel",
    "ModelIdentity",
    "PointKind",
    "PointPrompt",
    "ProbabilityMask",
    "RgbaImage",
    "SegmentationCandidate",
    "SegmentationModel",
    "SubjectPrompt",
    "Trimap",
    "TrimapValue",
]
