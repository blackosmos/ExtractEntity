"""Offline evaluation dataset contracts and verification."""

from .manifest import (
    DatasetCollection,
    EvaluationManifest,
    EvaluationSample,
    load_evaluation_manifest,
    parse_evaluation_manifest,
    verify_evaluation_sample,
)

__all__ = [
    "DatasetCollection",
    "EvaluationManifest",
    "EvaluationSample",
    "load_evaluation_manifest",
    "parse_evaluation_manifest",
    "verify_evaluation_sample",
]
