# Testing Guide

Comprehensive guide for writing and running tests in Lumina Care.

**Last updated:** April 12, 2026  
**Coverage requirement:** Backend ≥80%, Frontend ≥70%

---

## 🎯 Testing Overview

Lumina Care uses:

- **FastAPI + pytest** — Backend unit/integration tests
- **Next.js + Jest** — Frontend component/unit tests
- **pytest-cov** — Coverage reporting

**Test structure:**

```
src/api/tests/
├── conftest.py              # Fixtures, mocks, setup
├── test_main.py             # Core app tests (20 tests)
├── routers/
│   ├── test_triage.py      # Triage endpoint tests
│   ├── test_insights.py    # Insights endpoint tests
│   └── test_patients.py    # Patient endpoint tests
├── models/
│   └── test_schemas.py     # Data model validation tests
└── services/
    └── (service tests)

src/web/__tests__/
├── setup.ts
├── components/
│   └── __tests__/
│       ├── Button.test.tsx
│       └── Card.test.tsx
└── hooks/
    └── __tests__/
        └── useAuth.test.ts
```

---

## 📊 Current Status

**Backend Tests:**

- ✅ 73 tests passing
- ❌ 30 tests pending (waiting for router implementation)
- 📍 Total: 109 tests

**Frontend Tests:**

- ⏳ To be implemented

---

## 🚀 Running Tests

### Quick Commands

```bash
# Run all tests
make test

# Backend only
make test-backend
make test-backend-quick

# Frontend only
make test-frontend

# With coverage report
make test-coverage

# Validate everything (type-check + lint + test)
make validate
```

### Manual Commands

**Backend:**

```bash
# All tests
ANTHROPIC_API_KEY="sk-test-key" poetry run pytest src/api/tests/ -v

# Specific file
ANTHROPIC_API_KEY="sk-test-key" poetry run pytest src/api/tests/test_main.py -v

# Specific test class
ANTHROPIC_API_KEY="sk-test-key" poetry run pytest src/api/tests/test_main.py::TestHealthEndpoints -v

# Specific test
ANTHROPIC_API_KEY="sk-test-key" poetry run pytest src/api/tests/test_main.py::TestHealthEndpoints::test_health_check_returns_ok -v

# With coverage
ANTHROPIC_API_KEY="sk-test-key" poetry run pytest src/api/tests/ --cov=src/api --cov-report=html

# Only unit tests (no integration)
ANTHROPIC_API_KEY="sk-test-key" poetry run pytest src/api/tests/ -m unit -v

# Skip slow tests
ANTHROPIC_API_KEY="sk-test-key" poetry run pytest src/api/tests/ -m "not slow" -v

# Watch mode (rerun on changes)
ANTHROPIC_API_KEY="sk-test-key" poetry run pytest-watch src/api/tests/
```

**Frontend:**

```bash
# All tests
npm run test -- --coverage

# Specific file
npm run test -- src/web/__tests__/components/Button.test.tsx

# Watch mode
npm run test:watch

# Coverage only
npm run test:coverage
```

---

## 📝 Writing Backend Tests

### Test File Structure

```python
"""
Unit tests for [Module Name]

Tests [what is being tested].
"""

import pytest
from unittest.mock import patch, MagicMock


class TestFeatureName:
    """Tests for specific feature."""

    @pytest.mark.unit
    def test_simple_behavior(self):
        """Verify expected behavior."""
        # Arrange
        value = 10

        # Act
        result = value * 2

        # Assert
        assert result == 20

    @pytest.mark.unit
    def test_with_fixture(self, client):
        """Test using provided fixture."""
        response = client.get("/health")
        assert response.status_code == 200
```

### Using Fixtures

**Available fixtures (in conftest.py):**

```python
@pytest.mark.unit
def test_with_client(client):
    """FastAPI test client."""
    response = client.get("/health")
    assert response.status_code == 200

@pytest.mark.unit
def test_with_mock_db(mock_db):
    """Mock database connection."""
    mock_db.execute.return_value = None
    # ... test code

@pytest.mark.unit
def test_with_sample_data(sample_triage_request):
    """Sample request data."""
    assert sample_triage_request["patient_id"] == "test-patient-123"

@pytest.mark.unit
def test_with_mock_anthropic(mock_anthropic_client):
    """Mock Anthropic API."""
    mock_anthropic_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="AI response")]
    )
```

### Test Markers

```python
# Unit test (no external deps)
@pytest.mark.unit
def test_calculation():
    assert 2 + 2 == 4

# Integration test (with services)
@pytest.mark.integration
def test_api_with_db(client, mock_db):
    response = client.get("/data")
    mock_db.fetch.assert_called_once()

# Security test
@pytest.mark.security
def test_endpoint_requires_auth():
    response = client.get("/protected")
    assert response.status_code == 401

# Slow test
@pytest.mark.slow
def test_heavy_computation():
    # Long-running operation
    pass

# Run only unit tests:
# ANTHROPIC_API_KEY=... poetry run pytest -m unit

# Run without slow tests:
# ANTHROPIC_API_KEY=... poetry run pytest -m "not slow"
```

### Testing Endpoints

```python
class TestTiageEndpoints:
    """Test POST /api/v1/triage"""

    @pytest.mark.unit
    def test_triage_accepts_valid_request(self, client, sample_triage_request):
        """Verify endpoint accepts valid triage data."""
        response = client.post(
            "/api/v1/triage",
            json=sample_triage_request
        )

        assert response.status_code in [200, 201, 501]  # 501 = not implemented

        if response.status_code in [200, 201]:
            data = response.json()
            assert "patient_id" in data

    @pytest.mark.unit
    def test_triage_rejects_invalid_data(self, client):
        """Verify endpoint validates input."""
        invalid_request = {
            "phq9_score": 100,  # Invalid: max is 27
        }

        response = client.post("/api/v1/triage", json=invalid_request)

        assert response.status_code in [400, 422]  # Validation error

    @pytest.mark.unit
    def test_triage_requires_patient_id(self, client):
        """Verify endpoint requires patient_id."""
        incomplete_request = {
            "phq9_score": 10,
            "gad7_score": 8,
            # Missing patient_id
        }

        response = client.post("/api/v1/triage", json=incomplete_request)

        assert response.status_code in [400, 422]
```

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

@pytest.mark.unit
def test_with_mocked_anthropic():
    """Test without calling real Anthropic API."""
    with patch("src.api.services.ai.client") as mock_ai:
        # Configure mock
        mock_ai.messages.create.return_value = MagicMock(
            content=[MagicMock(text="Mocked AI response")]
        )

        # Test code using AI service
        from src.api.services.ai import generate_insights
        result = generate_insights({"score": 15})

        # Verify mock was called correctly
        mock_ai.messages.create.assert_called_once()
        assert "Mocked" in result
```

---

## 📝 Writing Frontend Tests

### Test File Structure

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import Button from '@/components/Button';

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick handler', () => {
    const onClick = jest.fn();
    render(<Button onClick={onClick}>Click</Button>);

    fireEvent.click(screen.getByText('Click'));
    expect(onClick).toHaveBeenCalled();
  });
});
```

### Testing React Components

```typescript
import { render, screen } from '@testing-library/react';
import Card from '@/components/Card';

describe('Card', () => {
  it('displays title and content', () => {
    render(
      <Card title="Test" content="Description" />
    );

    expect(screen.getByText('Test')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const onClick = jest.fn();
    render(
      <Card title="Test" onClick={onClick} />
    );

    screen.getByRole('button').click();
    expect(onClick).toHaveBeenCalled();
  });
});
```

### Testing Hooks

```typescript
import { renderHook, act } from "@testing-library/react";
import { useAuth } from "@/hooks/useAuth";

describe("useAuth hook", () => {
  it("initializes with null user", () => {
    const { result } = renderHook(() => useAuth());
    expect(result.current.user).toBeNull();
  });

  it("login sets user", async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.login("user@example.com", "password");
    });

    expect(result.current.user).not.toBeNull();
  });
});
```

### Testing API Calls

```typescript
import { fetchPatients } from "@/api/patients";
import axios from "axios";

jest.mock("axios");

describe("fetchPatients", () => {
  it("fetches patients list", async () => {
    const mockData = [
      { id: "1", name: "John" },
      { id: "2", name: "Jane" },
    ];

    (axios.get as jest.Mock).mockResolvedValue({ data: mockData });

    const result = await fetchPatients();

    expect(result).toEqual(mockData);
    expect(axios.get).toHaveBeenCalledWith("/api/v1/patients");
  });
});
```

---

## 📊 Coverage Reports

### Generate Coverage Report

**Backend:**

```bash
ANTHROPIC_API_KEY="sk-test-key" poetry run pytest src/api/tests/ \
  --cov=src/api \
  --cov-report=html \
  --cov-report=term

# View HTML report
open htmlcov/index.html
```

**Frontend:**

```bash
npm run test:coverage

# View HTML report
open coverage/lcov-report/index.html
```

### Coverage Thresholds

**Backend (pyproject.toml):**

```toml
[tool.coverage.report]
fail_under = 80  # 80% minimum
```

**Frontend (jest.config.js):**

```javascript
module.exports = {
  collectCoverageFrom: ["src/**/*.{ts,tsx}", "!src/**/*.d.ts"],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
```

---

## ✅ Best Practices

### DO ✅

- ✅ Write **descriptive test names** that explain what is tested
- ✅ Use **fixtures** for common setup
- ✅ Follow **Arrange-Act-Assert** pattern
- ✅ **Mock external services** (APIs, databases)
- ✅ Test **happy path AND error cases**
- ✅ Keep tests **focused** (one behavior per test)
- ✅ Use **meaningful assertions**

### DON'T ❌

- ❌ Don't test **implementation details**
- ❌ Don't use **overly broad mocks**
- ❌ Don't make tests **dependent on each other**
- ❌ Don't **skip flaky tests** — fix them
- ❌ Don't test **third-party libraries**
- ❌ Don't make tests **too slow** (< 100ms per test)

---

## 🔄 CI/CD Integration

**Tests run automatically on:**

- Push to `master` branch
- Pull requests to `master`

**Workflows:**

- `backend-tests.yml` — FastAPI tests + coverage
- `frontend-tests.yml` — Next.js tests + coverage
- `validate.yml` — Type checking + linting

**Required checks:**

- ✅ All tests pass
- ✅ Coverage ≥80% (backend)
- ✅ Coverage ≥70% (frontend)
- ✅ No linting errors

---

## 📚 Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [Jest documentation](https://jestjs.io/)
- [Testing Library docs](https://testing-library.com/)
- [Pydantic validation](https://docs.pydantic.dev/)

---

## 🆘 Common Issues

### "ANTHROPIC_API_KEY not set"

**Solution:**

```bash
export ANTHROPIC_API_KEY="sk-test-key"
poetry run pytest ...
```

### "Test timeout"

**Solution:**

```bash
# Increase timeout
poetry run pytest --timeout=300

# Or skip slow tests
poetry run pytest -m "not slow"
```

### "Module not found"

**Solution:**

```bash
poetry install
npm install
```

### "Database connection refused"

**Solution:**
Tests use mocks by default — no real database needed.
If integration tests fail, ensure PostgreSQL is running.

---

**Next:** [DEVELOPMENT.md](./DEVELOPMENT.md) — Development workflow
