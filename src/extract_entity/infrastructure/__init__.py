"""Infrastructure adapters for local files and external implementations."""

from .image_io import ImageDecodeError, decode_image
from .model_manifest import (
    ModelAsset,
    ModelManifest,
    SourceRecord,
    WeightRecord,
    load_model_manifest,
    parse_model_manifest,
    verify_model_weights,
)

__all__ = [
    "ImageDecodeError",
    "ModelAsset",
    "ModelManifest",
    "SourceRecord",
    "WeightRecord",
    "decode_image",
    "load_model_manifest",
    "parse_model_manifest",
    "verify_model_weights",
]
