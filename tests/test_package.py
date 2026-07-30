"""Smoke tests for the installable package."""

import extract_entity


def test_package_is_importable() -> None:
    """The project package resolves to the expected module."""
    assert extract_entity.__name__ == "extract_entity"
