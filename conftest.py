from __future__ import annotations
import pathlib
import pytest


@pytest.fixture
def test_data(request) -> pathlib.Path:
    """Include Mocks here to execute all commands offline and fast."""
    return pathlib.Path(request.path.parent.parent) / "tests" / "data"
