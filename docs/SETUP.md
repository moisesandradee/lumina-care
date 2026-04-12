# Local Development Setup

Complete guide for setting up Lumina Care locally.

**Time to complete:** ~15 minutes  
**Last updated:** April 12, 2026

---

## 📋 Prerequisites

### System Requirements

- **OS:** macOS, Linux, or Windows (WSL2)
- **Git:** 2.30+
- **Node.js:** 20 LTS
- **Python:** 3.11+
- **PostgreSQL:** 15+
- **Redis:** 7+

### Optional

- **Docker & Docker Compose** (for PostgreSQL/Redis without local install)
- **Make** (for convenient command running)

---

## 🚀 Quick Start (5 minutes)

### 1. Clone Repository

```bash
git clone https://github.com/moisesandradee/lumina-care.git
cd lumina-care
```

### 2. Install Dependencies

**Frontend + Backend:**
```bash
# Using make (recommended)
make setup

# Or manually:
npm install          # Frontend dependencies
poetry install       # Backend dependencies
```

### 3. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your settings
# (See Environment Variables section below)
```

### 4. Start Services

**Terminal 1 - Backend:**
```bash
make dev-backend
# or: poetry run uvicorn src.api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
make dev-frontend
# or: cd src/web && npm run dev
```

**Terminal 3 - Database (if not installed):**
```bash
docker-compose up -d postgres redis
```

### 5. Verify Setup

```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
open http://localhost:3000

# Run tests
make test-backend-quick
```

**✅ Done!** Both services running locally.

---

## 🔧 Detailed Setup

### Step 1: Install Node.js (Frontend)

**macOS (using Homebrew):**
```bash
brew install node@20
```

**Ubuntu/Debian:**
```bash
curl -sL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Verify:**
```bash
node --version  # Should be v20.x.x
npm --version   # Should be 10.x.x
```

---

### Step 2: Install Python (Backend)

**macOS (using Homebrew):**
```bash
brew install python@3.11 poetry
```

**Ubuntu/Debian:**
```bash
sudo apt-get install -y python3.11 python3-pip
pip install poetry
```

**Verify:**
```bash
python3.11 --version   # Should be Python 3.11.x
poetry --version       # Should be Poetry x.x.x
```

---

### Step 3: Install PostgreSQL 15

**Option A: Using Homebrew (macOS)**
```bash
brew install postgresql@15
brew services start postgresql@15
createdb lumina_care
```

**Option B: Using Docker (Recommended)**
```bash
docker run -d \
  --name postgres-15 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=lumina_care \
  -p 5432:5432 \
  postgres:15
```

**Option C: Using Docker Compose**
```bash
# See docker-compose.yml in project root
docker-compose up -d postgres
```

**Verify:**
```bash
psql -U postgres -d lumina_care -c "SELECT 1;"
# Should return: 1
```

---

### Step 4: Install Redis 7

**macOS (using Homebrew):**
```bash
brew install redis@7
brew services start redis@7
```

**Ubuntu/Debian:**
```bash
sudo apt-get install -y redis-server
sudo systemctl start redis-server
```

**Using Docker:**
```bash
docker run -d \
  --name redis-7 \
  -p 6379:6379 \
  redis:7
```

**Verify:**
```bash
redis-cli ping
# Should return: PONG
```

---

### Step 5: Clone & Install Project

```bash
# Clone repository
git clone https://github.com/moisesandradee/lumina-care.git
cd lumina-care

# Create branch for your work
git checkout -b feature/your-feature-name

# Install dependencies
make setup

# Or manually:
npm install
poetry install
```

---

### Step 6: Configure Environment

**Frontend (.env.local in src/web/):**
```bash
cd src/web
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Lumina Care
EOF
```

**Backend (.env in project root):**
```bash
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/lumina_care

# Cache
REDIS_URL=redis://localhost:6379/0

# AI Service
ANTHROPIC_API_KEY=sk-your-api-key-here

# Environment
ENVIRONMENT=development
DEBUG=true

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# Logging
LOG_LEVEL=INFO
EOF
```

---

### Step 7: Start Development Services

**Terminal 1 - Backend API:**
```bash
poetry run uvicorn src.api.main:app --reload --port 8000
```

**Terminal 2 - Frontend Web:**
```bash
cd src/web
npm run dev
```

**Terminal 3 - Database (if using Docker):**
```bash
docker-compose up
```

---

### Step 8: Database Setup

**Run migrations:**
```bash
poetry run python src/lib/db/migrate.ts
```

**Seed sample data (optional):**
```bash
poetry run python src/lib/db/seed.ts
```

---

## 📍 Service Endpoints

Once running, services are available at:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Web UI |
| **API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **PostgreSQL** | localhost:5432 | Database |
| **Redis** | localhost:6379 | Cache |

---

## 🧪 Running Tests

**Run all tests:**
```bash
make test
```

**Run backend tests only:**
```bash
make test-backend
# Coverage report in htmlcov/index.html
```

**Run frontend tests only:**
```bash
make test-frontend
```

**Run with coverage:**
```bash
make test-coverage
```

**Run specific test:**
```bash
# Backend
ANTHROPIC_API_KEY=sk-test poetry run pytest src/api/tests/test_main.py -v

# Frontend
npm run test -- src/web/__tests__/components/Button.test.tsx
```

---

## 🔍 Code Quality

**Type checking:**
```bash
npm run type-check
poetry run mypy src/api
```

**Linting:**
```bash
npm run lint
poetry run ruff check src/api
```

**Formatting:**
```bash
npm run format
poetry run black src/api
```

**Full validation:**
```bash
make validate
```

---

## 📱 Git Workflow

### Create Feature Branch
```bash
git checkout -b feature/feature-name
```

### Commit Changes
```bash
# Pre-commit hooks validate code
git add .
git commit -m "feat: add feature description"
```

### Push to Remote
```bash
git push -u origin feature/feature-name
```

### Create Pull Request
1. Go to GitHub
2. Create PR from your branch to `master`
3. Wait for CI/CD to pass
4. Request review from team
5. Merge when approved

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
poetry install
poetry run pytest ...
```

### "ANTHROPIC_API_KEY environment variable is required"

**Solution:**
```bash
export ANTHROPIC_API_KEY="sk-test-key"
poetry run pytest ...
```

### PostgreSQL connection refused

**Solution:**
```bash
# Check if running
psql -U postgres -c "SELECT 1;"

# If not running:
brew services start postgresql@15
# or
docker-compose up -d postgres
```

### Redis connection refused

**Solution:**
```bash
# Check if running
redis-cli ping

# If not running:
brew services start redis@7
# or
docker run -d --name redis -p 6379:6379 redis:7
```

### Node modules cache issue

**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Port already in use

**Solution:**
```bash
# Frontend (3000)
# Find and kill process on port 3000
lsof -i :3000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

# Backend (8000)
lsof -i :8000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

# Redis (6379)
lsof -i :6379 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

# PostgreSQL (5432)
lsof -i :5432 | grep -v COMMAND | awk '{print $2}' | xargs kill -9
```

---

## 📚 Next Steps

1. **Read** [DEVELOPMENT.md](./DEVELOPMENT.md) — Development workflow
2. **Read** [TESTING.md](./TESTING.md) — How to write tests
3. **Read** [API.md](./API.md) — API documentation
4. **Check** [CONTRIBUTING.md](../CONTRIBUTING.md) — Contributing guidelines

---

## ✅ Verification Checklist

- [ ] Node.js 20+ installed
- [ ] Python 3.11+ installed
- [ ] PostgreSQL 15 running on localhost:5432
- [ ] Redis 7 running on localhost:6379
- [ ] `npm install` completed
- [ ] `poetry install` completed
- [ ] `.env` file configured
- [ ] Backend starts: `poetry run uvicorn src.api.main:app --reload`
- [ ] Frontend starts: `cd src/web && npm run dev`
- [ ] Tests pass: `make test-backend-quick`
- [ ] Health check: `curl http://localhost:8000/health`

---

**Questions?** Check [FAQ.md](./FAQ.md) or open an issue on GitHub.

**Need help?** Email [support@lumina-care.dev](mailto:support@lumina-care.dev)
