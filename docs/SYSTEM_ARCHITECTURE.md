# System Architecture — Lumina

## Architectural Principles

Before describing the architecture, the principles that shaped it:

1. **Clinical data never leaves the security boundary unencrypted**
2. **Every AI output is traceable to its inputs** — full audit trail
3. **Human override is always possible, never costly**
4. **The AI layer is stateless** — no clinical decisions are made by persisting AI state
5. **Failure modes are safe** — if any AI component fails, the system degrades gracefully to manual workflows

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
│  ┌─────────────────────┐    ┌──────────────────────────────┐   │
│  │   Clinical Dashboard │    │    Care Coordinator View     │   │
│  │   (Next.js / Web)   │    │    (Next.js / Web)           │   │
│  └──────────┬──────────┘    └──────────────┬───────────────┘   │
└─────────────┼────────────────────────────── ┼──────────────────┘
              │                               │
┌─────────────┼────────────────────────────── ┼──────────────────┐
│             │        API Gateway            │                   │
│  ┌──────────▼───────────────────────────────▼──────────────┐   │
│  │              FastAPI Application Server                  │   │
│  │                                                          │   │
│  │  ┌──────────────┐  ┌───────────────┐  ┌─────────────┐  │   │
│  │  │ Triage Router│  │Insights Router│  │Patient Router│  │   │
│  │  └──────┬───────┘  └───────┬───────┘  └──────┬──────┘  │   │
│  └─────────┼──────────────────┼─────────────────┼──────────┘   │
│            │                  │                 │               │
│  ┌─────────▼──────────────────▼─────────────────▼──────────┐   │
│  │                    Service Layer                         │   │
│  │                                                          │   │
│  │  ┌────────────────┐    ┌──────────────────────────┐     │   │
│  │  │  AI Service    │    │  Risk Analysis Service   │     │   │
│  │  │ (Claude API)   │    │  (Clinical Scoring)      │     │   │
│  │  └───────┬────────┘    └─────────────┬────────────┘     │   │
│  └──────────┼──────────────────────────┼───────────────────┘   │
└─────────────┼──────────────────────────┼───────────────────────┘
              │                          │
┌─────────────┼──────────────────────────┼───────────────────────┐
│             │       Data Layer         │                        │
│  ┌──────────▼──────────┐  ┌────────────▼────────┐             │
│  │  PostgreSQL 15      │  │    Redis 7           │             │
│  │  (Primary store)    │  │    (Cache/Sessions)  │             │
│  └─────────────────────┘  └─────────────────────┘             │
└────────────────────────────────────────────────────────────────┘
              │
┌─────────────▼──────────────────────────────────────────────────┐
│               External AI Layer (Isolated)                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Anthropic Claude API                       │   │
│  │  (No raw patient data transmitted — only structured     │   │
│  │   anonymized clinical signals per prompt template)      │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. API Layer (FastAPI)

**Responsibilities:**
- Request validation and authentication
- Route dispatch to service layer
- Response serialization and error handling
- Rate limiting per clinical role

**Key design decisions:**
- All endpoints return structured responses with `confidence`, `evidence_refs`, and `override_allowed` fields
- Async by default — all I/O operations are non-blocking
- OpenAPI schema auto-generated for developer and clinical governance documentation

### 2. AI Service (`src/api/services/ai_service.py`)

**Responsibilities:**
- Constructs structured prompts from patient data using clinical prompt templates
- Calls Anthropic Claude API with appropriate system context
- Parses and validates LLM responses against expected clinical output schemas
- Logs all AI interactions to the audit store

**Critical safety constraints:**
- Raw patient PII is **never** included in prompts — only de-identified clinical signals
- Prompts include explicit safety instructions (see `prompts/`)
- All AI outputs are tagged `source: ai, requires_human_review: true`

### 3. Risk Analysis Service (`src/api/services/risk_analysis.py`)

**Responsibilities:**
- Computes multi-dimensional psychosocial risk scores from structured assessment data
- Applies validated clinical frameworks (PHQ-9, GAD-7, C-SSRS)
- Generates longitudinal trajectory models
- Produces risk priority rankings for care queues

**Risk dimensions tracked:**
- Acute safety risk (suicidal/self-harm ideation)
- Functional impairment severity
- Social support deficit
- Care engagement trajectory
- Symptom trajectory (improving / stable / deteriorating)

### 4. Database Schema (PostgreSQL)

**Core tables:**

```sql
-- Patients (de-identified internal representation)
patients (id, external_ref, created_at, care_team_id, status)

-- Clinical assessments
assessments (id, patient_id, type, scores_json, completed_at, clinician_id)

-- Risk snapshots (computed, not raw)
risk_snapshots (id, patient_id, computed_at, risk_score, dimensions_json, ai_run_id)

-- AI audit log (immutable)
ai_audit_log (id, patient_id, prompt_hash, output_hash, model, created_at, clinician_override)

-- Care interactions
care_interactions (id, patient_id, type, occurred_at, clinician_id, notes_hash)
```

### 5. Frontend (Next.js 14)

**Pages:**
- `/dashboard` — Clinical team overview, priority queue, risk heatmap
- `/patients/[id]` — Individual patient intelligence view
- `/triage` — Intake triage workflow
- `/insights` — Team-level analytics

**Key components:**
- `RiskQueue` — Prioritized patient list with risk indicators
- `PatientTimeline` — Longitudinal view of patient trajectory
- `AssessmentForm` — Structured intake and follow-up assessments
- `AIInsightCard` — Displays AI output with confidence, reasoning, and override button

---

## Security Architecture

| Layer | Control |
|---|---|
| **Transport** | TLS 1.3 everywhere |
| **Authentication** | JWT with short expiry + refresh token rotation |
| **Authorization** | Role-based (clinician / coordinator / director / admin) |
| **Data at rest** | AES-256 encryption for all patient-linked data |
| **AI boundary** | No PII crosses to external AI provider — prompt templates use anonymized signals only |
| **Audit** | Immutable audit log for all AI outputs and clinical overrides |
| **Access logging** | Every patient record access is logged with actor, timestamp, and context |

---

## Deployment Architecture

```
                    ┌───────────────┐
                    │   CloudFlare  │
                    │   (WAF/CDN)   │
                    └───────┬───────┘
                            │
              ┌─────────────▼──────────────┐
              │        Load Balancer        │
              └──────────┬──────────────────┘
                         │
           ┌─────────────┴──────────────┐
           │                            │
    ┌──────▼──────┐             ┌───────▼──────┐
    │  Web Servers│             │  API Servers  │
    │  (Next.js)  │             │  (FastAPI)    │
    └─────────────┘             └───────┬───────┘
                                        │
                           ┌────────────┴────────────┐
                           │                         │
                    ┌──────▼──────┐         ┌────────▼───────┐
                    │  PostgreSQL │         │  Redis Cluster │
                    │  (Primary + │         │  (Cache)       │
                    │  Replica)   │         └────────────────┘
                    └─────────────┘
```

---

## Scalability Considerations

- **Horizontal scaling**: API and web layers are stateless — scale by adding instances
- **Database**: Read replicas for analytics queries; write path isolated to primary
- **AI calls**: Queued and rate-limited; expensive analyses run async with webhook callback
- **Multi-tenancy**: Tenant isolation at database schema level (v2) or row-level security (v1)
