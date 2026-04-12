"""
Pytest Configuration and Fixtures for Lumina Care API Tests

Provides:
- FastAPI TestClient
- Mock database fixtures
- Mock Anthropic API client
- Common test data factories
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from src.api.main import app


# =============================================================================
# FastAPI Test Client
# =============================================================================

@pytest.fixture
def client():
    """
    FastAPI test client for making requests to the application.

    Usage:
        def test_health(client):
            response = client.get("/health")
            assert response.status_code == 200
    """
    return TestClient(app)


# =============================================================================
# Mock Database Fixtures
# =============================================================================

@pytest.fixture
def mock_db():
    """
    Mock database connection for testing.

    In production, this would connect to PostgreSQL.
    For testing, we return a mock object that can be configured per test.
    """
    db = MagicMock()
    db.execute = MagicMock(return_value=None)
    db.fetch = MagicMock(return_value=[])
    db.fetchone = MagicMock(return_value=None)
    db.close = MagicMock(return_value=None)
    return db


@pytest.fixture
def mock_redis():
    """
    Mock Redis cache connection for testing.

    In production, this would connect to Redis.
    For testing, we return a mock object with cache operations.
    """
    cache = MagicMock()
    cache.get = MagicMock(return_value=None)
    cache.set = MagicMock(return_value=True)
    cache.delete = MagicMock(return_value=True)
    cache.close = MagicMock(return_value=None)
    return cache


# =============================================================================
# Mock Anthropic API
# =============================================================================

@pytest.fixture
def mock_anthropic_client():
    """
    Mock Anthropic API client for testing AI features.

    Returns a configured mock that simulates API responses
    without making actual API calls.
    """
    client = MagicMock()

    # Mock message creation (for insights generation)
    client.messages.create = MagicMock(
        return_value=MagicMock(
            content=[MagicMock(text="Test AI response")]
        )
    )

    return client


# =============================================================================
# Test Data Factories
# =============================================================================

@pytest.fixture
def sample_triage_request():
    """
    Sample triage request payload for testing.

    Represents a patient assessment submission.
    """
    return {
        "patient_id": "test-patient-123",
        "phq9_score": 15,
        "gad7_score": 12,
        "clinical_notes": "Patient reports increased anxiety and depression symptoms",
        "risk_indicators": ["suicidal_ideation", "substance_use"],
    }


@pytest.fixture
def sample_patient_data():
    """
    Sample patient data for testing patient management endpoints.
    """
    return {
        "id": "patient-123",
        "name": "João Silva",
        "age": 35,
        "email": "joao@example.com",
        "phone": "11999999999",
        "medical_record_number": "MRN-12345",
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_assessment_data():
    """
    Sample assessment/screening data for testing.
    """
    return {
        "patient_id": "patient-123",
        "assessment_type": "PHQ9",
        "score": 15,
        "interpretation": "Moderate depression",
        "timestamp": "2024-04-12T10:30:00Z",
    }


# =============================================================================
# Mock Patches
# =============================================================================

@pytest.fixture
def patch_db_connection(mock_db):
    """
    Patch database connection globally for all tests.

    Useful when you want all database calls to use the mock
    without needing to patch in each test.
    """
    with patch("src.api.db.get_connection", return_value=mock_db):
        yield mock_db


@pytest.fixture
def patch_redis_connection(mock_redis):
    """
    Patch Redis connection globally for all tests.
    """
    with patch("src.api.cache.get_redis", return_value=mock_redis):
        yield mock_redis


@pytest.fixture
def patch_anthropic_client(mock_anthropic_client):
    """
    Patch Anthropic API client globally for all tests.
    """
    with patch("src.api.services.ai.client", mock_anthropic_client):
        yield mock_anthropic_client


# =============================================================================
# Test Markers
# =============================================================================

def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests (no external deps)")
    config.addinivalue_line("markers", "integration: Integration tests (with services)")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "security: Security-related tests")
