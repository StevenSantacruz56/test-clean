"""
Pytest Configuration and Fixtures.

Shared test fixtures and configuration.
"""

import pytest


@pytest.fixture
def sample_fixture():
    """Example fixture for testing."""
    return "sample_data"
