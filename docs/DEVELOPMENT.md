# Development Workflow

Guidelines for contributing to Lumina Care.

**Last updated:** April 12, 2026

---

## 🌿 Branch Strategy

### Branch Naming Convention

```
feature/<feature-name>      # New features
fix/<bug-name>             # Bug fixes
hotfix/<critical-fix>      # Production hotfixes
refactor/<description>     # Code refactoring
docs/<topic>              # Documentation updates
chore/<task>              # Maintenance tasks
```

**Examples:**

```
feature/triage-risk-algorithm
fix/phq9-score-validation
hotfix/critical-auth-bypass
refactor/extract-ai-service
docs/api-endpoints
```

---

## 📝 Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat** — New feature
- **fix** — Bug fix
- **docs** — Documentation
- **style** — Code style (formatting, missing semicolons)
- **refactor** — Code refactoring
- **perf** — Performance improvements
- **test** — Tests
- **chore** — Maintenance, dependencies

### Examples

```
feat(triage): implement risk prioritization algorithm

- Added PHQ-9/GAD-7 score interpretation
- Implemented risk escalation logic
- Added unit tests (95% coverage)

Closes #42
```

```
fix(api): prevent division by zero in scoring

Previously, empty risk indicators would cause 500 error.
Now defaults to neutral scoring.

Fixes #87
```

```
docs(setup): add PostgreSQL troubleshooting

Added section for common connection issues and solutions.
```

---

## 🔄 Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

```bash
# Create/edit files
nano src/api/routers/new_feature.py

# Run tests (validates your changes)
make test-backend

# Type checking
npm run type-check
poetry run mypy src/

# Linting
npm run lint
poetry run ruff check src/

# Format code
npm run format
poetry run black src/
```

### 3. Commit Changes

```bash
# Stage changes
git add src/api/routers/new_feature.py

# Commit with conventional format
git commit -m "feat(api): add new feature endpoint

- Implemented POST /api/v1/new-feature
- Added input validation with Pydantic
- Added 5 unit tests"

# Pre-commit hooks validate automatically
```

### 4. Push to Remote

```bash
# First push: set upstream
git push -u origin feature/your-feature-name

# Subsequent pushes
git push
```

### 5. Create Pull Request

1. Go to https://github.com/moisesandradee/lumina-care
2. Click "New Pull Request"
3. Select your branch as source, `master` as target
4. Fill in PR template:
   - **Description** — What does this PR do?
   - **Type** — Bug fix, Feature, Docs, etc.
   - **Testing** — How did you test this?
   - **Checklist** — Verify all items

### 6. Code Review

- Address reviewer comments
- Push additional commits if needed
- Re-request review when ready

### 7. Merge to Master

Once approved:

```bash
# Merge via GitHub UI
# or locally:
git checkout master
git pull origin master
git merge feature/your-feature-name
git push origin master
```

---

## 🧪 Testing During Development

### Run Tests After Each Change

```bash
# Full validation
make validate

# Quick check (most critical)
make test-backend-quick

# Watch mode (auto-rerun on changes)
ANTHROPIC_API_KEY=sk-test poetry run pytest-watch src/api/tests/
```

### Test Coverage

```bash
# View coverage
make test-coverage

# Open HTML report
open htmlcov/index.html

# Fail if coverage < threshold
ANTHROPIC_API_KEY=sk-test poetry run pytest \
  src/api/tests/ \
  --cov=src/api \
  --cov-fail-under=80
```

---

## 🏗️ Project Structure

### Backend (FastAPI)

```
src/api/
├── main.py                  # FastAPI application
├── routers/
│   ├── triage.py           # Triage endpoints
│   ├── insights.py         # AI insights endpoints
│   └── patients.py         # Patient management endpoints
├── models/
│   └── schemas.py          # Pydantic models
├── services/
│   ├── ai_service.py       # Anthropic integration
│   ├── db_service.py       # Database operations
│   └── cache_service.py    # Redis caching
└── tests/
    ├── conftest.py         # Fixtures and mocks
    ├── test_main.py        # Core app tests
    └── routers/            # Endpoint tests
```

### Frontend (Next.js)

```
src/web/
├── app/                     # Next.js app router
│   ├── layout.tsx
│   ├── page.tsx
│   └── (routes)/           # Route grouping
├── components/
│   ├── ui/                 # Reusable UI components
│   └── dashboard/          # Feature components
├── hooks/                  # Custom React hooks
├── lib/
│   ├── api/                # API client functions
│   └── utils/              # Utility functions
└── __tests__/              # Component tests
```

---

## 🔒 Code Quality Standards

### Minimum Requirements

- ✅ **Type Safety** — No `any` types without justification
- ✅ **Linting** — ESLint + Ruff pass
- ✅ **Formatting** — Prettier + Black applied
- ✅ **Testing** — ≥70% code coverage
- ✅ **Security** — No hardcoded secrets

### Pre-commit Validation

```bash
# Automatically run before commit
npm run type-check      # TypeScript
npm run lint           # ESLint
npm run format:check   # Prettier
poetry run mypy src/   # Python types
poetry run ruff check  # Python lint
```

### CI/CD Checks

Pull requests must pass:

- ✅ `frontend-tests` — Next.js tests & coverage
- ✅ `backend-tests` — FastAPI tests & coverage
- ✅ `validate` — Type checking + linting
- ✅ `dependencies` — Security audit

---

## 🚫 Troubleshooting

### "Pre-commit hook failed"

**Solution:** Fix the errors shown:

```bash
# Run linters manually to see issues
npm run lint
poetry run ruff check src/

# Auto-fix where possible
npm run lint:fix
poetry run black src/
poetry run ruff check --fix src/
```

### "Type checking failed"

**Solution:** Add type hints:

```typescript
// ❌ Wrong
const calculate = (values) => {
  return values.reduce((a, b) => a + b, 0);
};

// ✅ Right
const calculate = (values: number[]): number => {
  return values.reduce((a, b) => a + b, 0);
};
```

### "Tests failing locally but passing in CI"

**Solution:** Ensure you have test API key:

```bash
export ANTHROPIC_API_KEY="sk-test-key"
make test
```

### "Package version conflicts"

**Solution:** Refresh lock files:

```bash
npm ci              # Use package-lock.json exactly
poetry install      # Use poetry.lock exactly
```

---

## 📚 Style Guide

### Python

```python
# Follow PEP 8
# Use type hints
def process_patient(patient_id: str, score: int) -> dict:
    """Process patient assessment."""
    # Docstrings for public functions
    return {"patient_id": patient_id, "score": score}

# Use f-strings
message = f"Patient {patient_id} has score {score}"

# Prefer pathlib
from pathlib import Path
config_file = Path("config/settings.json")

# Avoid bare except
try:
    risky_operation()
except ValueError as e:
    log_error(f"Invalid value: {e}")
```

### TypeScript/React

```typescript
// Use interfaces for component props
interface ButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

// Use const for components
const Button: React.FC<ButtonProps> = ({ onClick, disabled = false }) => (
  <button onClick={onClick} disabled={disabled}>
    Click me
  </button>
);

// Use hooks for state
const [count, setCount] = useState<number>(0);

// Use async/await, not promises
async function fetchData() {
  const response = await fetch("/api/data");
  return response.json();
}
```

---

## 🎯 Code Review Checklist

Before requesting review, verify:

- [ ] Branch created from `master`
- [ ] All tests passing locally
- [ ] `npm run validate` passes
- [ ] No `console.log` statements (except for debugging)
- [ ] No hardcoded secrets or API keys
- [ ] Updated tests if behavior changed
- [ ] Updated documentation if needed
- [ ] Conventional commit message used
- [ ] Self-reviewed your own PR

---

## 📞 Getting Help

- **Questions?** Ask in #development on Slack
- **Bug found?** Create an issue on GitHub
- **Need review?** Request specific reviewers
- **Stuck?** Check [SETUP.md](./SETUP.md) or [FAQ.md](./FAQ.md)

---

**Next:** [TESTING.md](./TESTING.md) — Testing best practices
