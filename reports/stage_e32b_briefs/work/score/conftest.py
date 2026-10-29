"""pytest setup for the Stage E.32b scoring scripts: this folder on sys.path, and the synthetic fixture docs."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import make_fixture  # noqa: E402


@pytest.fixture
def docs():
    """A fresh copy of the synthetic fixture (make_fixture.build), safe to modify in a test."""
    return make_fixture.build()
