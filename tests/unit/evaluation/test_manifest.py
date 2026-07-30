import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from extract_entity.evaluation import (
    DatasetCollection,
    load_evaluation_manifest,
    parse_evaluation_manifest,
    verify_evaluation_sample,
)


def sample(
    *,
    sample_id: object = "object-001",
    collection: object = "smoke",
    tags: object = None,
    input_path: object = "inputs/object-001.png",
    input_sha256: object = "a" * 64,
    ground_truth_path: object = None,
    ground_truth_sha256: object = None,
) -> dict[str, object]:
    return {
        "id": sample_id,
        "collection": collection,
        "category": "camera",
        "tags": ["hard-edge", "internal-hole"] if tags is None else tags,
        "input_path": input_path,
        "input_sha256": input_sha256,
        "ground_truth_path": ground_truth_path,
        "ground_truth_sha256": ground_truth_sha256,
        "source": "project-owner",
        "license": "project-owned",
        "expected_subject": "The camera body and attached strap.",
        "notes": "Preserve the opening inside the strap loop.",
    }


def manifest(samples: object) -> str:
    return json.dumps({"schema_version": 1, "samples": samples})


def test_empty_manifest_is_valid_but_contains_no_quality_evidence() -> None:
    parsed = parse_evaluation_manifest('{"schema_version": 1, "samples": []}')
    assert parsed.schema_version == 1
    assert parsed.samples == ()


@pytest.mark.parametrize("collection", [item.value for item in DatasetCollection])
def test_all_four_collections_are_supported(collection: str) -> None:
    parsed = parse_evaluation_manifest(manifest([sample(collection=collection)]))
    assert parsed.samples[0].collection.value == collection


def test_non_empty_manifest_preserves_metadata_and_optional_ground_truth() -> None:
    parsed = parse_evaluation_manifest(
        manifest(
            [
                sample(
                    ground_truth_path="ground-truth/object-001.png",
                    ground_truth_sha256="b" * 64,
                )
            ]
        )
    )
    value = parsed.samples[0]
    assert value.tags == ("hard-edge", "internal-hole")
    assert value.source == "project-owner"
    assert value.license == "project-owned"
    assert value.ground_truth_path is not None
    assert value.ground_truth_path.as_posix() == "ground-truth/object-001.png"


def test_load_manifest_reads_local_file(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(manifest([]), encoding="utf-8")
    assert load_evaluation_manifest(path).samples == ()


@pytest.mark.parametrize(
    "content",
    [
        "not-json",
        '{"schema_version":1,"schema_version":1,"samples":[]}',
    ],
)
def test_invalid_json_and_duplicate_keys_are_rejected(content: str) -> None:
    with pytest.raises(ValueError):
        parse_evaluation_manifest(content)


def test_invalid_utf8_is_rejected_clearly() -> None:
    with pytest.raises(ValueError, match="UTF-8"):
        parse_evaluation_manifest(b"\xff")


@pytest.mark.parametrize(
    "document",
    [
        {"schema_version": 1, "samples": [], "unknown": True},
        {"schema_version": 1},
        {"schema_version": True, "samples": []},
        {"schema_version": 2, "samples": []},
        {"schema_version": 1, "samples": {}},
        {"schema_version": 1, "samples": [{**sample(), "unknown": "value"}]},
    ],
)
def test_schema_shape_is_strict(document: dict[str, object]) -> None:
    with pytest.raises((TypeError, ValueError)):
        parse_evaluation_manifest(json.dumps(document))


def test_sample_ids_are_globally_unique() -> None:
    with pytest.raises(ValueError, match="duplicate sample id"):
        parse_evaluation_manifest(
            manifest([sample(collection="smoke"), sample(collection="common")])
        )


@pytest.mark.parametrize("sample_id", ["", "Object-1", "object_1", " object-1", "object-1 "])
def test_sample_id_must_be_a_canonical_slug(sample_id: str) -> None:
    with pytest.raises(ValueError):
        parse_evaluation_manifest(manifest([sample(sample_id=sample_id)]))


def test_unknown_collection_is_rejected() -> None:
    with pytest.raises(ValueError, match="supported collection"):
        parse_evaluation_manifest(manifest([sample(collection="training")]))


@pytest.mark.parametrize(
    "tags",
    [
        "hard-edge",
        [],
        [1],
        ["Hard-Edge"],
        ["hard_edge"],
        ["hard-edge", "hard-edge"],
        ["internal-hole", "hard-edge"],
    ],
)
def test_tags_must_be_non_empty_unique_sorted_canonical_slugs(tags: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        parse_evaluation_manifest(manifest([sample(tags=tags)]))


@pytest.mark.parametrize(
    ("path", "digest"),
    [(None, "a" * 64), ("ground-truth/a.png", None), (1, "a" * 64), ("ground-truth/a.png", 1)],
)
def test_ground_truth_path_and_hash_are_paired(path: object, digest: object) -> None:
    with pytest.raises((TypeError, ValueError), match="ground_truth"):
        parse_evaluation_manifest(
            manifest([sample(ground_truth_path=path, ground_truth_sha256=digest)])
        )


def test_direct_sample_construction_cannot_break_ground_truth_pair() -> None:
    parsed = parse_evaluation_manifest(manifest([sample()])).samples[0]
    with pytest.raises(ValueError, match="both be present"):
        replace(parsed, ground_truth_sha256="a" * 64)


@pytest.mark.parametrize(
    "path",
    [
        "",
        ".",
        "/a.png",
        "../a.png",
        "x/../a.png",
        "./a.png",
        "x//a.png",
        "x\\a.png",
        "C:/a.png",
        "C:a.png",
        "x/\x00a.png",
    ],
)
def test_input_path_must_be_safe_portable_and_relative(path: str) -> None:
    with pytest.raises(ValueError, match="input_path"):
        parse_evaluation_manifest(manifest([sample(input_path=path)]))


@pytest.mark.parametrize("digest", ["a" * 63, "A" * 64, "g" * 64, 1])
def test_input_sha256_is_canonical_lowercase_hex(digest: object) -> None:
    with pytest.raises((TypeError, ValueError), match="input_sha256"):
        parse_evaluation_manifest(manifest([sample(input_sha256=digest)]))


def test_ground_truth_path_and_sha_use_the_same_strict_validators() -> None:
    with pytest.raises(ValueError, match="ground_truth_path"):
        parse_evaluation_manifest(
            manifest([sample(ground_truth_path="../truth.png", ground_truth_sha256="a" * 64)])
        )
    with pytest.raises(ValueError, match="ground_truth_sha256"):
        parse_evaluation_manifest(
            manifest(
                [
                    sample(
                        ground_truth_path="ground-truth/truth.png",
                        ground_truth_sha256="A" * 64,
                    )
                ]
            )
        )


@pytest.mark.parametrize("field", ["category", "source", "license", "expected_subject", "notes"])
def test_required_text_fields_are_nonblank(field: str) -> None:
    value = sample()
    value[field] = " "
    with pytest.raises(ValueError, match=field):
        parse_evaluation_manifest(manifest([value]))


def test_verify_sample_checks_input_then_optional_ground_truth(tmp_path: Path) -> None:
    input_content = b"input"
    truth_content = b"truth"
    input_path = tmp_path / "inputs" / "object-001.png"
    truth_path = tmp_path / "ground-truth" / "object-001.png"
    input_path.parent.mkdir(parents=True)
    truth_path.parent.mkdir()
    input_path.write_bytes(input_content)
    truth_path.write_bytes(truth_content)
    parsed = parse_evaluation_manifest(
        manifest(
            [
                sample(
                    input_sha256=hashlib.sha256(input_content).hexdigest(),
                    ground_truth_path="ground-truth/object-001.png",
                    ground_truth_sha256=hashlib.sha256(truth_content).hexdigest(),
                )
            ]
        )
    ).samples[0]

    assert verify_evaluation_sample(parsed, tmp_path) == (
        input_path.resolve(),
        truth_path.resolve(),
    )


def test_verify_sample_without_ground_truth(tmp_path: Path) -> None:
    content = b"input"
    path = tmp_path / "inputs" / "object-001.png"
    path.parent.mkdir()
    path.write_bytes(content)
    parsed = parse_evaluation_manifest(
        manifest([sample(input_sha256=hashlib.sha256(content).hexdigest())])
    ).samples[0]
    assert verify_evaluation_sample(parsed, tmp_path) == (path.resolve(), None)


def test_verifier_errors_identify_sample_and_input_field(tmp_path: Path) -> None:
    parsed = parse_evaluation_manifest(manifest([sample()])).samples[0]
    with pytest.raises(FileNotFoundError, match="sample object-001 input"):
        verify_evaluation_sample(parsed, tmp_path)


def test_verifier_errors_identify_ground_truth_field(tmp_path: Path) -> None:
    content = b"input"
    path = tmp_path / "inputs" / "object-001.png"
    path.parent.mkdir()
    path.write_bytes(content)
    parsed = parse_evaluation_manifest(
        manifest(
            [
                sample(
                    input_sha256=hashlib.sha256(content).hexdigest(),
                    ground_truth_path="ground-truth/object-001.png",
                    ground_truth_sha256="b" * 64,
                )
            ]
        )
    ).samples[0]
    with pytest.raises(FileNotFoundError, match="sample object-001 ground_truth"):
        verify_evaluation_sample(parsed, tmp_path)


def test_verifier_rejects_hash_mismatch_and_symlink_escape(tmp_path: Path) -> None:
    root = tmp_path / "benchmarks"
    input_path = root / "inputs" / "object-001.png"
    input_path.parent.mkdir(parents=True)
    input_path.write_bytes(b"wrong")
    parsed = parse_evaluation_manifest(manifest([sample()])).samples[0]
    with pytest.raises(ValueError, match="sample object-001 input.*SHA-256 mismatch"):
        verify_evaluation_sample(parsed, root)

    outside = tmp_path / "outside.png"
    outside.write_bytes(b"outside")
    input_path.unlink()
    input_path.symlink_to(outside)
    with pytest.raises(ValueError, match="sample object-001 input.*escapes"):
        verify_evaluation_sample(parsed, root)
