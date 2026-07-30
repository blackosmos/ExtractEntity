#!/usr/bin/env python3
"""Offline repository invariants shared by local development and CI."""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote, urlsplit

from extract_entity.evaluation import load_evaluation_manifest
from extract_entity.infrastructure import load_model_manifest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
_MODEL_WEIGHT_SUFFIXES = frozenset({".ckpt", ".onnx", ".pt", ".pth", ".safetensors"})
_FORBIDDEN_DIRECTORY_PARTS = frozenset(
    {".mypy_cache", ".pytest_cache", ".pyright", ".ruff_cache", ".venv", "__pycache__", "venv"}
)
_FORBIDDEN_ROOTS = frozenset({"artifacts", "checkpoints", "output", "outputs"})
_BUILD_OUTPUT_ROOTS = frozenset({"build", "dist", "htmlcov"})
_SECRET_NAMES = frozenset({"credentials.json", "secrets.json"})


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=False,
        capture_output=True,
    )


def tracked_files(root: Path) -> tuple[Path, ...]:
    result = _git(root, "ls-files", "-z")
    if result.returncode != 0:
        detail = result.stderr.decode(errors="replace").strip()
        raise RuntimeError(f"cannot list tracked files: {detail}")
    return tuple(Path(value.decode()) for value in result.stdout.split(b"\0") if value)


def check_markdown_links(root: Path, files: tuple[Path, ...]) -> list[str]:
    problems: list[str] = []
    resolved_root = root.resolve()
    for relative_file in files:
        if relative_file.suffix.lower() != ".md":
            continue
        document = root / relative_file
        for line_number, line in enumerate(document.read_text(encoding="utf-8").splitlines(), 1):
            for match in _MARKDOWN_LINK.finditer(line):
                raw_target = match.group(1).strip()
                if raw_target.startswith("<") and raw_target.endswith(">"):
                    raw_target = raw_target[1:-1]
                target_without_fragment = raw_target.split("#", 1)[0]
                if not target_without_fragment or urlsplit(target_without_fragment).scheme:
                    continue
                target = (document.parent / unquote(target_without_fragment)).resolve()
                try:
                    target.relative_to(resolved_root)
                except ValueError:
                    problems.append(
                        f"{relative_file}:{line_number}: relative link escapes repository: "
                        f"{raw_target}"
                    )
                    continue
                if not target.exists():
                    problems.append(
                        f"{relative_file}:{line_number}: relative link does not exist: {raw_target}"
                    )
    return problems


def check_runtime_dependencies(root: Path) -> list[str]:
    with (root / "pyproject.toml").open("rb") as stream:
        configuration = tomllib.load(stream)
    project = configuration.get("project")
    if type(project) is not dict:
        return ["pyproject.toml: project table is missing"]
    dependencies = project.get("dependencies")
    if dependencies != ["Pillow>=12.0,<13"]:
        return ["pyproject.toml: project.dependencies must contain only the reviewed Pillow range"]
    return []


def check_manifests(root: Path) -> list[str]:
    problems: list[str] = []
    for relative, loader in (
        (Path("models/manifest.json"), load_model_manifest),
        (Path("benchmarks/manifest.json"), load_evaluation_manifest),
    ):
        try:
            loader(root / relative)
        except (OSError, TypeError, ValueError) as error:
            problems.append(f"{relative}: {error}")
    return problems


def check_quality_workflow(root: Path) -> list[str]:
    path = root / ".github/workflows/quality.yml"
    try:
        workflow = path.read_text(encoding="utf-8")
    except OSError as error:
        return [f".github/workflows/quality.yml: {error}"]
    required = (
        "permissions:\n  contents: read",
        "actions/checkout@v4",
        "actions/setup-python@v5",
        'python-version: ["3.11", "3.12"]',
        "fail-fast: false",
        "timeout-minutes: 15",
        "python -m pip install -e '.[dev]'",
        "python -m pip check",
        "python scripts/check_repository.py",
        "python -m ruff format --check .",
        "python -m ruff check .",
        "python -m pyright",
        "python -m pytest",
    )
    problems = [
        f"quality workflow is missing required text: {text}"
        for text in required
        if text not in workflow
    ]
    uses = re.findall(r"^\s*(?:-\s*)?uses:\s*(\S+)\s*$", workflow, flags=re.MULTILINE)
    allowed_actions = ("actions/checkout@v4", "actions/setup-python@v5")
    if tuple(uses) != allowed_actions:
        problems.append(
            "quality workflow actions must be exactly one actions/checkout@v4 followed by "
            "one actions/setup-python@v5"
        )
    return problems


def check_tracked_files(files: tuple[Path, ...]) -> list[str]:
    problems: list[str] = []
    for path in files:
        parts = path.parts
        name = path.name
        forbidden_reason: str | None = None
        if any(part in _FORBIDDEN_DIRECTORY_PARTS for part in parts):
            forbidden_reason = "cache or virtual-environment content"
        elif path.suffix.lower() in {".pyc", ".pyo"}:
            forbidden_reason = "Python bytecode"
        elif len(parts) >= 2 and parts[0:2] == (".cache", "huggingface"):
            forbidden_reason = "model cache"
        elif (parts and parts[0] in _BUILD_OUTPUT_ROOTS) or any(
            part.endswith(".egg-info") for part in parts
        ):
            forbidden_reason = "build output"
        elif name == ".coverage":
            forbidden_reason = "coverage output"
        elif parts and parts[0] in _FORBIDDEN_ROOTS:
            forbidden_reason = "generated extraction content"
        elif len(parts) >= 2 and parts[0:2] == ("benchmarks", "reports"):
            forbidden_reason = "generated benchmark report"
        elif (
            parts
            and parts[0] == "models"
            and path
            not in {
                Path("models/README.md"),
                Path("models/manifest.json"),
            }
        ):
            forbidden_reason = "model binary or cache"
        elif path.suffix.lower() in _MODEL_WEIGHT_SUFFIXES:
            forbidden_reason = "model weight"
        elif name == ".env" or (name.startswith(".env.") and name != ".env.example"):
            forbidden_reason = "local environment or secret file"
        elif name in _SECRET_NAMES:
            forbidden_reason = "common secret file"
        if forbidden_reason is not None:
            problems.append(f"{path}: tracked {forbidden_reason} is forbidden")
    return problems


def _is_ignored(root: Path, path: str) -> bool:
    return _git(root, "check-ignore", "--no-index", "--quiet", "--", path).returncode == 0


def check_gitignore(root: Path) -> list[str]:
    expected_ignored = (
        ".venv/file",
        "package/__pycache__/module.pyc",
        "models/weights.bin",
        "checkpoints/model.bin",
        "output/result.png",
        "outputs/result.png",
        "artifacts/debug.png",
        "benchmarks/reports/report.json",
        ".env",
        ".env.local",
        "module.pyc",
        ".cache/huggingface/model.bin",
        "build/package.whl",
        "dist/package.tar.gz",
        "src/package.egg-info/PKG-INFO",
        ".coverage",
        "htmlcov/index.html",
    )
    expected_visible = (
        ".env.example",
        "models/README.md",
        "models/manifest.json",
        "benchmarks/manifest.json",
        "benchmarks/inputs/controlled.png",
    )
    problems = [
        f".gitignore does not ignore required path: {path}"
        for path in expected_ignored
        if not _is_ignored(root, path)
    ]
    problems.extend(
        f".gitignore unexpectedly ignores controlled path: {path}"
        for path in expected_visible
        if _is_ignored(root, path)
    )
    return problems


def run_checks(root: Path = REPOSITORY_ROOT) -> list[str]:
    """Return every repository invariant violation without changing files."""

    files = tracked_files(root)
    return [
        *check_markdown_links(root, files),
        *check_runtime_dependencies(root),
        *check_manifests(root),
        *check_quality_workflow(root),
        *check_tracked_files(files),
        *check_gitignore(root),
    ]


def main() -> int:
    problems = run_checks()
    if problems:
        print("Repository checks failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print("Repository checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
