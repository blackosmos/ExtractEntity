"""Small shared validators for versioned, offline JSON manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, cast


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"manifest contains duplicate field: {key}")
        result[key] = value
    return result


def parse_json(content: str | bytes) -> object:
    if type(content) not in (str, bytes):
        raise TypeError("manifest content must be str or bytes")
    try:
        return cast(object, json.loads(content, object_pairs_hook=reject_duplicate_keys))
    except UnicodeDecodeError as error:
        raise ValueError("manifest bytes must be valid UTF-8") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid manifest JSON: {error.msg}") from error


def exact_mapping(value: object, *, name: str, keys: frozenset[str]) -> dict[str, object]:
    if type(value) is not dict:
        raise TypeError(f"{name} must be an object")
    mapping = cast(dict[str, object], value)
    actual = frozenset(mapping)
    missing = keys - actual
    unknown = actual - keys
    if missing:
        raise ValueError(f"{name} is missing fields: {', '.join(sorted(missing))}")
    if unknown:
        raise ValueError(f"{name} has unknown fields: {', '.join(sorted(unknown))}")
    return mapping


def nonblank_text(value: object, *, name: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must not be blank")
    if value != value.strip():
        raise ValueError(f"{name} must not have leading or trailing whitespace")
    return value


def sha256_digest(value: object, *, name: str) -> str:
    digest = nonblank_text(value, name=name)
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise ValueError(f"{name} must be 64 lowercase hexadecimal characters")
    return digest


def safe_posix_path(value: object, *, name: str) -> PurePosixPath:
    text = nonblank_text(value, name=name)
    if "\\" in text or "\x00" in text:
        raise ValueError(f"{name} must be a portable POSIX path")
    if any(segment in ("", ".", "..") for segment in text.split("/")):
        raise ValueError(f"{name} must not contain empty, dot or parent segments")
    path = PurePosixPath(text)
    if path.is_absolute() or PureWindowsPath(text).drive:
        raise ValueError(f"{name} must be a safe relative path")
    return path


def verify_local_file(*, root: Path, relative_path: PurePosixPath, expected_sha256: str) -> Path:
    resolved_root = root.resolve()
    candidate = (resolved_root / Path(*relative_path.parts)).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(f"path escapes the configured root: {relative_path}") from error
    if not candidate.is_file():
        raise FileNotFoundError(f"local file is missing: {relative_path}")
    digest = hashlib.sha256()
    with candidate.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual != expected_sha256:
        raise ValueError(
            f"SHA-256 mismatch for {relative_path}: expected {expected_sha256}, got {actual}"
        )
    return candidate
