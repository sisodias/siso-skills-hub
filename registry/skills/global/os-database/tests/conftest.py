"""Pytest configuration for os-database tests."""
import os
import pytest

SCRIPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "scripts"
)


@pytest.fixture
def scripts_dir():
    """Return the scripts directory path."""
    return SCRIPTS_DIR
