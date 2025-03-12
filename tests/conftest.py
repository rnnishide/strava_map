#   ---------------------------------------------------------------------------------
#   Copyright (c) Microsoft Corporation. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
"""
This is a configuration file for pytest containing customizations and fixtures.

In VSCode, Code Coverage is recorded in config.xml. Delete this file to reset reporting.
"""

from __future__ import annotations
import pathlib
import pytest


@pytest.fixture
def test_data(request) -> pathlib.Path:
    """Include Mocks here to execute all commands offline and fast."""
    return pathlib.Path(request.path.parent) / "data"
