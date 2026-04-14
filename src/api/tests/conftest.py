"""
Lumina Care — Test Configuration
Shared fixtures for the API test suite.
"""

import os
import sys
import pytest

# Ensure the API source directory is on the path so tests can import
# `models`, `routers`, and `services` without a package install.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    """
    Synchronous TestClient for the FastAPI application.

    AIService is instantiated at module load time and requires ANTHROPIC_API_KEY.
    We set a dummy value here so the import succeeds; individual tests that
    exercise the AI path should mock the Anthropic client.
    """
    os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-not-used-in-unit-tests")

    from main import app

    with TestClient(app) as c:
        yield c
