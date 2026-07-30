"""Strict, offline parsing and verification of the model asset manifest."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import cast

from ._manifest_validation import (
    exact_mapping,
    nonblank_text,
    parse_json,
    safe_posix_path,
    sha256_digest,
    verify_local_file,
)

_ROOT_KEYS = frozenset({"schema_version", "models"})
_MODEL_KEYS = frozenset({"id", "role", "code", "weights"})
_SOURCE_KEYS = frozenset({"source", "revision", "license"})
_WEIGHT_KEYS = frozenset({"source", "revision", "license", "sha256", "path"})


@dataclass(frozen=True, slots=True)
class SourceRecord:
    source: str
    revision: str
    license: str


@dataclass(frozen=True, slots=True)
class WeightRecord:
    source: str
    revision: str
    license: str
    sha256: str
    path: PurePosixPath


@dataclass(frozen=True, slots=True)
class ModelAsset:
    id: str
    role: str
    code: SourceRecord
    weights: WeightRecord


@dataclass(frozen=True, slots=True)
class ModelManifest:
    schema_version: int
    models: tuple[ModelAsset, ...]


def _source_record(value: object, *, name: str) -> SourceRecord:
    mapping = exact_mapping(value, name=name, keys=_SOURCE_KEYS)
    return SourceRecord(
        source=nonblank_text(mapping["source"], name=f"{name}.source"),
        revision=nonblank_text(mapping["revision"], name=f"{name}.revision"),
        license=nonblank_text(mapping["license"], name=f"{name}.license"),
    )


def _local_path(value: object) -> PurePosixPath:
    return safe_posix_path(value, name="weights.path")


def _weights_record(value: object) -> WeightRecord:
    mapping = exact_mapping(value, name="weights", keys=_WEIGHT_KEYS)
    return WeightRecord(
        source=nonblank_text(mapping["source"], name="weights.source"),
        revision=nonblank_text(mapping["revision"], name="weights.revision"),
        license=nonblank_text(mapping["license"], name="weights.license"),
        sha256=sha256_digest(mapping["sha256"], name="weights.sha256"),
        path=_local_path(mapping["path"]),
    )


def parse_model_manifest(content: str | bytes) -> ModelManifest:
    """Parse manifest JSON without reading files or performing network access."""

    root = exact_mapping(parse_json(content), name="manifest", keys=_ROOT_KEYS)
    version = root["schema_version"]
    if type(version) is not int:
        raise TypeError("schema_version must be an integer")
    if version != 1:
        raise ValueError(f"unsupported schema_version: {version}")
    raw_models_value = root["models"]
    if type(raw_models_value) is not list:
        raise TypeError("models must be an array")
    raw_models = cast(list[object], raw_models_value)

    models: list[ModelAsset] = []
    seen_ids: set[str] = set()
    for index, raw_model in enumerate(raw_models):
        mapping = exact_mapping(raw_model, name=f"models[{index}]", keys=_MODEL_KEYS)
        model_id = nonblank_text(mapping["id"], name=f"models[{index}].id")
        if model_id in seen_ids:
            raise ValueError(f"duplicate model id: {model_id}")
        seen_ids.add(model_id)
        models.append(
            ModelAsset(
                id=model_id,
                role=nonblank_text(mapping["role"], name=f"models[{index}].role"),
                code=_source_record(mapping["code"], name=f"models[{index}].code"),
                weights=_weights_record(mapping["weights"]),
            )
        )
    return ModelManifest(schema_version=version, models=tuple(models))


def load_model_manifest(path: Path) -> ModelManifest:
    """Read and parse one local UTF-8 manifest file."""

    return parse_model_manifest(path.read_bytes())


def verify_model_weights(model: ModelAsset, models_root: Path) -> Path:
    """Verify one existing local weight file and return its resolved path."""

    if type(model) is not ModelAsset:
        raise TypeError("model must be a ModelAsset")
    return verify_local_file(
        root=models_root,
        relative_path=model.weights.path,
        expected_sha256=model.weights.sha256,
    )
