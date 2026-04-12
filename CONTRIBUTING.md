# Contributing to Lumina

Thank you for your interest in contributing to Lumina! We welcome contributions from clinicians, engineers, researchers, and anyone passionate about improving mental health care with AI.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Commit Standards](#commit-standards)
- [Pull Request Process](#pull-request-process)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Reporting Issues](#reporting-issues)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

---

## Getting Started

### Prerequisites

- **Node.js** 18+ (frontend)
- **Python** 3.11+ (backend)
- **Docker** & **Docker Compose** (optional but recommended)
- **Git** 2.30+

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/moisesandradee/lumina-care.git
cd lumina-care

# Setup frontend dependencies
cd src/web
npm install
cd ../..

# Setup backend dependencies (optional, if working on API)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd src/api
pip install -r requirements.txt
cd ../..

# Copy environment file
cp .env.example .env
# Edit .env with your configuration (API keys, database URLs, etc.)

# Start development
npm run dev          # Frontend runs on http://localhost:3000
# In another terminal:
cd src/api && uvicorn main:app --reload  # API runs on http://localhost:8000
```

### Using Docker Compose

```bash
cp .env.example .env
# Edit .env as needed
docker-compose up --build
# Web: http://localhost:3000
# API: http://localhost:8000
# PostgreSQL: localhost:5432
# Redis: localhost:6379
```

---

## Development Workflow

### 1. Create a Branch

Use these branch naming conventions:

```
feat/feature-name        → New feature
fix/bug-description      → Bug fix
docs/doc-update         → Documentation only
test/test-name          → Tests only
chore/task-description  → Maintenance, dependencies
refactor/change-name    → Code refactoring
perf/optimization-name  → Performance improvements
security/issue-name     → Security fixes
```

**Example:**

```bash
git checkout -b feat/intelligent-triage-v2
```

### 2. Write Code

**Frontend (Next.js/TypeScript):**

- Follow [TypeScript strict mode](https://www.typescriptlang.org/tsconfig#strict)
- Use functional components with hooks
- Prefer React Query for data fetching
- Style with Tailwind CSS
- Run `npm run type-check` to validate

**Backend (FastAPI/Python):**

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints (Python 3.11+)
- Validate with Pydantic
- Write docstrings for functions
- Use async/await for I/O operations

### 3. Run Tests Locally

```bash
# Frontend tests
cd src/web
npm run test                # Run tests
npm run test:watch        # Watch mode
npm run test:coverage     # Coverage report

# Backend tests
cd src/api
pytest --cov=.            # Run with coverage

# Type checking
npm run type-check        # TypeScript
mypy src/api              # Python (if configured)
```

### 4. Lint and Format

```bash
# Format code (auto-fix)
npm run format            # All
cd src/web && npm run format   # Frontend only

# Check linting
npm run lint              # Strict mode
npm run lint:fix          # Auto-fix issues
```

### 5. Commit Your Changes

Use **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `chore`: Maintenance, dependency updates
- `refactor`: Code restructuring
- `perf`: Performance improvements
- `security`: Security-related fixes

**Example:**

```
feat(triage): add risk score normalization for C-SSRS

- Implement Z-score normalization for cross-framework comparison
- Add unit tests for edge cases (min/max scores)
- Update API response schema to include normalized_score field

Closes #42
```

**Important:**

- Keep commits atomic (one logical change per commit)
- Write descriptive commit messages
- Reference GitHub issues: `Closes #123`, `Fixes #456`

---

## Pull Request Process

### Before Submitting

```bash
# Ensure branch is up-to-date
git fetch origin
git rebase origin/master

# Run complete validation
npm run validate          # tsc + lint + test

# Push your branch
git push -u origin feat/your-feature
```

### PR Template

When creating a PR, include:

```markdown
## 📝 Description

Brief summary of changes.

## 🎯 Type of Change

- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change
- [ ] Documentation update

## 📋 Related Issues

Closes #123

## ✅ Testing

- [ ] Added unit tests
- [ ] Added integration tests
- [ ] Manual testing completed
- [ ] No regressions detected

## 📚 Documentation

- [ ] Updated README if needed
- [ ] Updated API docs if applicable
- [ ] Added/updated code comments
- [ ] Updated CHANGELOG

## ⚠️ Breaking Changes

None / Description if applicable

## 🔍 Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] No new warnings generated
- [ ] Tests pass locally
```

### Review Process

1. **Automated Checks** (required to pass)
   - ✅ Linting passes
   - ✅ Type checking passes
   - ✅ All tests pass
   - ✅ No security vulnerabilities

2. **Code Review** (minimum 1 approval)
   - Architecture alignment
   - Code quality
   - Test coverage
   - Documentation completeness

3. **Maintainer Approval** (for releases)
   - Overall quality
   - Scope alignment
   - Changelog update

---

## Testing Requirements

### Frontend Tests

All new components and hooks must have tests:

```typescript
// Button.test.tsx
import { render, screen } from '@testing-library/react';
import Button from './Button';

describe('Button', () => {
  it('renders with correct label', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  it('calls onClick handler when clicked', () => {
    const onClick = jest.fn();
    render(<Button onClick={onClick}>Click</Button>);
    screen.getByRole('button').click();
    expect(onClick).toHaveBeenCalled();
  });
});
```

### Backend Tests

All endpoints and services must have tests:

```python
# tests/test_triage.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_triage_analysis():
    response = client.post(
        "/api/v1/triage/analyze",
        json={"patient_id": "pat_001", "phq9_score": 18}
    )
    assert response.status_code == 200
    assert "risk_level" in response.json()
```

### Coverage Requirements

- **Frontend:** Minimum 70% coverage
- **Backend:** Minimum 80% coverage
- **Critical paths:** 100% coverage required

---

## Documentation Standards

### Code Documentation

```typescript
/**
 * Analyzes patient risk signals using Claude AI
 *
 * @param patientData - Patient assessment data
 * @returns Promise<RiskAnalysis> - Structured risk assessment with confidence scores
 *
 * @throws {ValidationError} If patient data is invalid
 * @throws {AIServiceError} If Claude API fails
 *
 * @example
 * const analysis = await analyzeRisk(patientData);
 * console.log(analysis.riskLevel);
 */
export async function analyzeRisk(patientData: PatientData): Promise<RiskAnalysis> {
  // Implementation
}
```

### Markdown Documentation

- Use clear headings (H1, H2, H3)
- Include code examples
- Link to related docs
- Keep line length ≤ 100 characters
- Use tables for structured data

---

## Reporting Issues

### Bug Reports

Use the **Bug Report** template:

```markdown
## 🐛 Bug Description

Clear and concise description of what the bug is.

## 📍 Steps to Reproduce

1. Go to...
2. Click on...
3. See error

## 🎯 Expected Behavior

What should happen

## 😞 Actual Behavior

What actually happens

## 📸 Screenshots

If applicable

## 💻 Environment

- OS: [e.g. macOS 14.1]
- Node version: [e.g. 20.10]
- Browser: [if applicable]

## 🔍 Additional Context

Any other context
```

### Feature Requests

Use the **Feature Request** template:

```markdown
## 📋 Summary

Brief description of the feature

## 🎯 Problem Statement

What problem does this solve?

## 💡 Proposed Solution

How should this work?

## 🔍 Alternatives Considered

Any alternatives?

## 🎁 Additional Context

Relevant information
```

---

## Security

If you discover a security vulnerability, **do NOT open a public issue**. See [SECURITY.md](SECURITY.md) for reporting instructions.

---

## Questions?

- 📖 See [SETUP.md](docs/SETUP.md) for detailed setup instructions
- 📚 See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for development guides
- 💬 Open a [discussion](https://github.com/moisesandradee/lumina-care/discussions)

---

## License

By contributing to Lumina, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to better mental health care! 💙**
