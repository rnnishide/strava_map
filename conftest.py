from __future__ import annotations
import pathlib
import pytest


@pytest.fixture
def test_data(request) -> pathlib.Path:
    """Get path to test data directory."""
    return pathlib.Path(request.path.parent.parent) / "tests" / "data"
