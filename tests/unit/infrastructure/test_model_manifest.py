import hashlib
import json
from pathlib import Path

import pytest

from extract_entity.infrastructure import (
    ModelAsset,
    load_model_manifest,
    parse_model_manifest,
    verify_model_weights,
)


def entry(
    *,
    model_id: object = "model-a",
    local_path: object = "model-a/weights.bin",
    sha256: object = "a" * 64,
) -> dict[str, object]:
    return {
        "id": model_id,
        "role": "automatic-segmentation",
        "code": {
            "source": "https://code.invalid/project",
            "revision": "code-revision",
            "license": "code-license",
        },
        "weights": {
            "source": "https://weights.invalid/file",
            "revision": "weight-revision",
            "license": "weight-license",
            "sha256": sha256,
            "path": local_path,
        },
    }


def manifest(models: object) -> str:
    return json.dumps({"schema_version": 1, "models": models})


def parse_entry(**overrides: object) -> ModelAsset:
    return parse_model_manifest(manifest([entry(**overrides)])).models[0]


def test_empty_manifest_is_valid() -> None:
    parsed = parse_model_manifest('{"schema_version": 1, "models": []}')
    assert parsed.schema_version == 1
    assert parsed.models == ()


def test_non_empty_manifest_keeps_code_and_weight_provenance_separate() -> None:
    model = parse_entry()
    assert model.id == "model-a"
    assert model.code.revision == "code-revision"
    assert model.code.license == "code-license"
    assert model.weights.revision == "weight-revision"
    assert model.weights.license == "weight-license"
    assert model.weights.path.as_posix() == "model-a/weights.bin"


def test_load_manifest_reads_utf8_file(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(manifest([]), encoding="utf-8")
    assert load_model_manifest(path).models == ()


@pytest.mark.parametrize(
    "content",
    [
        "not json",
        '{"schema_version":1,"schema_version":1,"models":[]}',
    ],
)
def test_invalid_json_and_duplicate_fields_are_rejected(content: str) -> None:
    with pytest.raises(ValueError):
        parse_model_manifest(content)


def test_invalid_utf8_is_rejected() -> None:
    with pytest.raises(ValueError, match="UTF-8"):
        parse_model_manifest(b"\xff")


@pytest.mark.parametrize(
    "document",
    [
        {"schema_version": 1, "models": [], "unknown": True},
        {"schema_version": 1},
        {"schema_version": True, "models": []},
        {"schema_version": 2, "models": []},
        {"schema_version": 1, "models": {}},
        {"schema_version": 1, "models": [{**entry(), "unknown": "value"}]},
    ],
)
def test_schema_shape_and_scalar_types_are_strict(document: dict[str, object]) -> None:
    with pytest.raises((TypeError, ValueError)):
        parse_model_manifest(json.dumps(document))


def test_duplicate_and_blank_model_ids_are_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate model id"):
        parse_model_manifest(manifest([entry(), entry()]))
    with pytest.raises(ValueError, match="must not be blank"):
        parse_model_manifest(manifest([entry(model_id="  ")]))


def test_blank_provenance_fields_are_rejected_independently() -> None:
    value = entry()
    code = value["code"]
    assert isinstance(code, dict)
    code["license"] = ""
    with pytest.raises(ValueError, match="code.license"):
        parse_model_manifest(manifest([value]))


@pytest.mark.parametrize("section", ["code", "weights"])
def test_nested_unknown_fields_are_rejected(section: str) -> None:
    value = entry()
    nested = value[section]
    assert isinstance(nested, dict)
    nested["unexpected"] = "value"
    with pytest.raises(ValueError, match="unknown fields"):
        parse_model_manifest(manifest([value]))


@pytest.mark.parametrize(("section", "field"), [("code", "revision"), ("weights", "revision")])
def test_nested_missing_fields_are_rejected(section: str, field: str) -> None:
    value = entry()
    nested = value[section]
    assert isinstance(nested, dict)
    del nested[field]
    with pytest.raises(ValueError, match="missing fields"):
        parse_model_manifest(manifest([value]))


@pytest.mark.parametrize("value", [" model-a", "model-a "])
def test_strings_reject_leading_or_trailing_whitespace(value: str) -> None:
    with pytest.raises(ValueError, match="whitespace"):
        parse_entry(model_id=value)


@pytest.mark.parametrize(
    "path",
    [
        "",
        ".",
        "/absolute.bin",
        "C:/weights.bin",
        "C:weights.bin",
        "../outside.bin",
        "folder/../outside.bin",
        "./weights.bin",
        "folder//weights.bin",
        "folder\\weights.bin",
        "folder/\x00weights.bin",
    ],
)
def test_unsafe_or_non_portable_paths_are_rejected(path: str) -> None:
    with pytest.raises(ValueError, match="path"):
        parse_entry(local_path=path)


@pytest.mark.parametrize("digest", ["a" * 63, "a" * 65, "A" * 64, "g" * 64, 1])
def test_sha256_requires_canonical_lowercase_hex(digest: object) -> None:
    with pytest.raises((TypeError, ValueError), match="sha256"):
        parse_entry(sha256=digest)


def test_verify_weights_returns_resolved_file_for_matching_digest(tmp_path: Path) -> None:
    content = b"local test weight\x00content"
    digest = hashlib.sha256(content).hexdigest()
    model = parse_entry(sha256=digest)
    weight = tmp_path / "model-a" / "weights.bin"
    weight.parent.mkdir()
    weight.write_bytes(content)

    assert verify_model_weights(model, tmp_path) == weight.resolve()


def test_verify_weights_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="missing"):
        verify_model_weights(parse_entry(), tmp_path)


def test_verify_weights_rejects_hash_mismatch(tmp_path: Path) -> None:
    model = parse_entry()
    weight = tmp_path / "model-a" / "weights.bin"
    weight.parent.mkdir()
    weight.write_bytes(b"wrong")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        verify_model_weights(model, tmp_path)


def test_verify_weights_rejects_directory_at_weight_path(tmp_path: Path) -> None:
    directory = tmp_path / "model-a" / "weights.bin"
    directory.mkdir(parents=True)
    with pytest.raises(FileNotFoundError, match="missing"):
        verify_model_weights(parse_entry(), tmp_path)


def test_verify_weights_rejects_symlink_escape(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "weights.bin").write_bytes(b"content")
    root = tmp_path / "models"
    root.mkdir()
    (root / "model-a").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="escapes"):
        verify_model_weights(parse_entry(), root)
