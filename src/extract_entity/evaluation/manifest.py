"""Strict, offline manifest for controlled evaluation assets."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import cast

from extract_entity.infrastructure._manifest_validation import (
    exact_mapping,
    nonblank_text,
    parse_json,
    safe_posix_path,
    sha256_digest,
    verify_local_file,
)

_ROOT_KEYS = frozenset({"schema_version", "samples"})
_SAMPLE_KEYS = frozenset(
    {
        "id",
        "collection",
        "category",
        "tags",
        "input_path",
        "input_sha256",
        "ground_truth_path",
        "ground_truth_sha256",
        "source",
        "license",
        "expected_subject",
        "notes",
    }
)
_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class DatasetCollection(StrEnum):
    SMOKE = "smoke"
    COMMON = "common"
    DIFFICULT = "difficult"
    REGRESSION = "regression"


@dataclass(frozen=True, slots=True)
class EvaluationSample:
    id: str
    collection: DatasetCollection
    category: str
    tags: tuple[str, ...]
    input_path: PurePosixPath
    input_sha256: str
    ground_truth_path: PurePosixPath | None
    ground_truth_sha256: str | None
    source: str
    license: str
    expected_subject: str
    notes: str

    def __post_init__(self) -> None:
        if (self.ground_truth_path is None) != (self.ground_truth_sha256 is None):
            raise ValueError("ground_truth path and SHA-256 must both be present or both be absent")


@dataclass(frozen=True, slots=True)
class EvaluationManifest:
    schema_version: int
    samples: tuple[EvaluationSample, ...]


def _slug(value: object, *, name: str) -> str:
    text = nonblank_text(value, name=name)
    if _SLUG.fullmatch(text) is None:
        raise ValueError(f"{name} must be a lowercase canonical slug")
    return text


def _tags(value: object, *, name: str) -> tuple[str, ...]:
    if type(value) is not list:
        raise TypeError(f"{name} must be an array")
    raw_tags = cast(list[object], value)
    if not raw_tags:
        raise ValueError(f"{name} must not be empty")
    tags = tuple(_slug(tag, name=f"{name} item") for tag in raw_tags)
    if len(tags) != len(set(tags)):
        raise ValueError(f"{name} must not contain duplicates")
    if tags != tuple(sorted(tags)):
        raise ValueError(f"{name} must already be sorted")
    return tags


def _collection(value: object, *, name: str) -> DatasetCollection:
    text = nonblank_text(value, name=name)
    try:
        return DatasetCollection(text)
    except ValueError as error:
        raise ValueError(f"{name} is not a supported collection: {text}") from error


def _optional_ground_truth(
    path_value: object, digest_value: object, *, name: str
) -> tuple[PurePosixPath | None, str | None]:
    if path_value is None and digest_value is None:
        return None, None
    if path_value is None or digest_value is None:
        raise ValueError(f"{name} path and SHA-256 must both be strings or both be null")
    return (
        safe_posix_path(path_value, name=f"{name}_path"),
        sha256_digest(digest_value, name=f"{name}_sha256"),
    )


def parse_evaluation_manifest(content: str | bytes) -> EvaluationManifest:
    """Parse an evaluation manifest without accessing assets or the network."""

    root = exact_mapping(parse_json(content), name="manifest", keys=_ROOT_KEYS)
    version = root["schema_version"]
    if type(version) is not int:
        raise TypeError("schema_version must be an integer")
    if version != 1:
        raise ValueError(f"unsupported schema_version: {version}")
    samples_value = root["samples"]
    if type(samples_value) is not list:
        raise TypeError("samples must be an array")
    raw_samples = cast(list[object], samples_value)

    samples: list[EvaluationSample] = []
    ids: set[str] = set()
    for index, raw_sample in enumerate(raw_samples):
        name = f"samples[{index}]"
        sample = exact_mapping(raw_sample, name=name, keys=_SAMPLE_KEYS)
        sample_id = _slug(sample["id"], name=f"{name}.id")
        if sample_id in ids:
            raise ValueError(f"duplicate sample id: {sample_id}")
        ids.add(sample_id)
        gt_path, gt_digest = _optional_ground_truth(
            sample["ground_truth_path"], sample["ground_truth_sha256"], name="ground_truth"
        )
        samples.append(
            EvaluationSample(
                id=sample_id,
                collection=_collection(sample["collection"], name=f"{name}.collection"),
                category=nonblank_text(sample["category"], name=f"{name}.category"),
                tags=_tags(sample["tags"], name=f"{name}.tags"),
                input_path=safe_posix_path(sample["input_path"], name=f"{name}.input_path"),
                input_sha256=sha256_digest(sample["input_sha256"], name=f"{name}.input_sha256"),
                ground_truth_path=gt_path,
                ground_truth_sha256=gt_digest,
                source=nonblank_text(sample["source"], name=f"{name}.source"),
                license=nonblank_text(sample["license"], name=f"{name}.license"),
                expected_subject=nonblank_text(
                    sample["expected_subject"], name=f"{name}.expected_subject"
                ),
                notes=nonblank_text(sample["notes"], name=f"{name}.notes"),
            )
        )
    return EvaluationManifest(schema_version=version, samples=tuple(samples))


def load_evaluation_manifest(path: Path) -> EvaluationManifest:
    """Read and parse one local manifest file as UTF-8 JSON."""

    return parse_evaluation_manifest(path.read_bytes())


def _verify_sample_file(
    sample: EvaluationSample,
    root: Path,
    *,
    field: str,
    path: PurePosixPath,
    digest: str,
) -> Path:
    try:
        return verify_local_file(root=root, relative_path=path, expected_sha256=digest)
    except FileNotFoundError as error:
        raise FileNotFoundError(f"sample {sample.id} {field}: {error}") from error
    except ValueError as error:
        raise ValueError(f"sample {sample.id} {field}: {error}") from error


def verify_evaluation_sample(
    sample: EvaluationSample, benchmarks_root: Path
) -> tuple[Path, Path | None]:
    """Verify input first and optional Ground Truth second for one sample."""

    if type(sample) is not EvaluationSample:
        raise TypeError("sample must be an EvaluationSample")
    input_path = _verify_sample_file(
        sample,
        benchmarks_root,
        field="input",
        path=sample.input_path,
        digest=sample.input_sha256,
    )
    if sample.ground_truth_path is None or sample.ground_truth_sha256 is None:
        return input_path, None
    ground_truth_path = _verify_sample_file(
        sample,
        benchmarks_root,
        field="ground_truth",
        path=sample.ground_truth_path,
        digest=sample.ground_truth_sha256,
    )
    return input_path, ground_truth_path
