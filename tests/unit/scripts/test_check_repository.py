import os
import subprocess
import sys
from pathlib import Path

from scripts.check_repository import (
    check_gitignore,
    check_manifests,
    check_markdown_links,
    check_quality_workflow,
    check_runtime_dependencies,
    check_tracked_files,
    tracked_files,
)


def git(root: Path, *arguments: str) -> None:
    subprocess.run(("git", "-C", str(root), *arguments), check=True, capture_output=True)


def test_tracked_files_is_nul_safe_and_independent_of_working_directory(tmp_path: Path) -> None:
    git(tmp_path, "init", "--quiet")
    unusual = tmp_path / "file with spaces.md"
    unusual.write_text("# File\n", encoding="utf-8")
    git(tmp_path, "add", unusual.name)
    assert tracked_files(tmp_path) == (Path("file with spaces.md"),)


def test_repository_cli_is_independent_of_calling_working_directory(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[3]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(root / "src")
    result = subprocess.run(
        (sys.executable, str(root / "scripts/check_repository.py")),
        cwd=tmp_path,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Repository checks passed" in result.stdout


def test_markdown_relative_links_accept_existing_target_and_reject_missing_or_escape(
    tmp_path: Path,
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "target.md").write_text("# Target\n", encoding="utf-8")
    source = docs / "source.md"
    source.write_text(
        "[valid](target.md#section)\n[external](https://example.invalid)\n"
        "[email](mailto:owner@example.invalid)\n"
        "[missing](missing.md)\n[escape](../../outside.md)\n",
        encoding="utf-8",
    )
    problems = check_markdown_links(tmp_path, (Path("docs/source.md"),))
    assert len(problems) == 2
    assert "does not exist" in problems[0]
    assert "escapes repository" in problems[1]


def test_manifest_check_reports_each_invalid_manifest(tmp_path: Path) -> None:
    (tmp_path / "models").mkdir()
    (tmp_path / "benchmarks").mkdir()
    valid_model = '{"schema_version":1,"models":[]}'
    valid_evaluation = '{"schema_version":1,"samples":[]}'
    (tmp_path / "models/manifest.json").write_text("{}", encoding="utf-8")
    (tmp_path / "benchmarks/manifest.json").write_text(valid_evaluation, encoding="utf-8")
    problems = check_manifests(tmp_path)
    assert len(problems) == 1 and problems[0].startswith("models/manifest.json")

    (tmp_path / "models/manifest.json").write_text(valid_model, encoding="utf-8")
    (tmp_path / "benchmarks/manifest.json").write_text("{}", encoding="utf-8")
    problems = check_manifests(tmp_path)
    assert len(problems) == 1 and problems[0].startswith("benchmarks/manifest.json")


def test_gitignore_check_covers_required_ignored_and_controlled_visible_paths(
    tmp_path: Path,
) -> None:
    root = Path(__file__).resolve().parents[3]
    (tmp_path / ".gitignore").write_text(
        (root / ".gitignore").read_text(encoding="utf-8"), encoding="utf-8"
    )
    git(tmp_path, "init", "--quiet")
    assert check_gitignore(tmp_path) == []

    (tmp_path / ".gitignore").write_text("*\n", encoding="utf-8")
    assert any("controlled path" in problem for problem in check_gitignore(tmp_path))


def test_quality_workflow_has_the_complete_two_version_gate(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[3]
    workflow = root / ".github/workflows/quality.yml"
    assert check_quality_workflow(root) == []

    target = tmp_path / ".github/workflows"
    target.mkdir(parents=True)
    (target / "quality.yml").write_text(
        workflow.read_text(encoding="utf-8").replace("python -m pytest", "echo skipped"),
        encoding="utf-8",
    )
    assert any("python -m pytest" in problem for problem in check_quality_workflow(tmp_path))

    content = workflow.read_text(encoding="utf-8")
    (target / "quality.yml").write_text(
        content.replace("actions/checkout@v4", "actions/checkout@main"), encoding="utf-8"
    )
    assert any("actions must be exactly" in problem for problem in check_quality_workflow(tmp_path))

    (target / "quality.yml").write_text(
        f"{content}\n      - uses: third-party/example@main\n", encoding="utf-8"
    )
    assert any("actions must be exactly" in problem for problem in check_quality_workflow(tmp_path))


def test_runtime_dependency_check_requires_an_explicit_empty_array(tmp_path: Path) -> None:
    configuration = tmp_path / "pyproject.toml"
    configuration.write_text(
        '[project]\nname = "example"\ndependencies = ["Pillow>=12.0,<13"]\n',
        encoding="utf-8",
    )
    assert check_runtime_dependencies(tmp_path) == []

    configuration.write_text(
        '[project]\nname = "example"\ndependencies = ["numpy"]\n', encoding="utf-8"
    )
    assert "only the reviewed Pillow range" in check_runtime_dependencies(tmp_path)[0]


def test_tracked_file_check_is_targeted_and_does_not_reject_controlled_images() -> None:
    allowed = (
        Path("benchmarks/inputs/object.png"),
        Path("benchmarks/ground-truth/object.png"),
        Path("tests/fixtures/tiny.bin"),
        Path("models/README.md"),
        Path("models/manifest.json"),
    )
    assert check_tracked_files(allowed) == []

    forbidden = (
        Path("src/__pycache__/module.pyc"),
        Path("models/model.safetensors"),
        Path("benchmarks/reports/full.json"),
        Path("output/result.png"),
        Path(".env.production"),
        Path("credentials.json"),
        Path("module.pyc"),
        Path("module.pyo"),
        Path(".cache/huggingface/model.bin"),
        Path("build/package.whl"),
        Path("dist/package.tar.gz"),
        Path("src/package.egg-info/PKG-INFO"),
        Path(".coverage"),
        Path("htmlcov/index.html"),
    )
    problems = check_tracked_files(forbidden)
    assert len(problems) == len(forbidden)
    assert all("forbidden" in problem for problem in problems)
