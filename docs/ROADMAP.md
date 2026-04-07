# Product Roadmap — Lumina

## Roadmap Philosophy

Lumina's roadmap is sequenced to build clinical trust before expanding clinical scope. We will not add capabilities faster than we can validate their safety and utility. Every phase ships something a clinician can genuinely use before we build the next layer.

---

## Phase 1 — Foundation (Current)

**Objective**: Deliver a working, safe, deployable triage intelligence core.

**Timeframe**: Q1–Q2

**Deliverables:**

| Feature | Description | Status |
|---|---|---|
| Core API | FastAPI backend with auth, patient model, assessment endpoints | 🔄 In progress |
| Risk Analysis Engine | PHQ-9, GAD-7, C-SSRS scoring and prioritization | 🔄 In progress |
| AI Triage Service | Claude-powered signal analysis with structured output | 🔄 In progress |
| Clinical Dashboard MVP | Priority queue, patient list, basic risk visualization | 📋 Planned |
| Audit Logging | Immutable AI output and access log | 📋 Planned |
| Auth & RBAC | JWT auth with role-based access (clinician/coordinator/director) | 📋 Planned |
| Docker deployment | One-command local and cloud deployment | 📋 Planned |

**Exit criteria for Phase 1:**
- API passes clinical review for safe output framing
- Risk engine validated against reference datasets
- Two clinicians complete user testing with positive usability feedback

---

## Phase 2 — Intelligence Layer (Q3)

**Objective**: Deepen the AI intelligence and add longitudinal trajectory analysis.

**Deliverables:**

| Feature | Description |
|---|---|
| Longitudinal trajectory modeling | 30/60/90-day trend analysis per patient |
| Care gap detection | Automated identification of patients outside care plan cadence |
| Session-prep briefings | AI-generated pre-session patient summaries for clinicians |
| Multi-assessment fusion | Synthesize multiple instrument scores into unified risk profile |
| Prompt v2 architecture | Refined prompts with bias audit and clinical validation |
| Confidence calibration | Empirical confidence score validation |

---

## Phase 3 — Care Coordination Interface (Q4)

**Objective**: Full care coordinator workflow, outreach management, and team coordination.

**Deliverables:**

| Feature | Description |
|---|---|
| Coordinator dashboard | Priority outreach queue with recommended actions |
| Outreach tracking | Log and schedule patient contact attempts |
| Care plan adherence monitoring | Visual care plan timeline with deviation flags |
| Team communication layer | Structured clinical handoffs and escalation notifications |
| Patient-facing check-in (beta) | Brief digital check-in between sessions (consent-gated) |
| Mobile-responsive interface | Clinical dashboard accessible on tablet and mobile |

---

## Phase 4 — Integration & Interoperability (Year 2 Q1)

**Objective**: Connect Lumina to existing health infrastructure.

**Deliverables:**

| Feature | Description |
|---|---|
| HL7 FHIR adapter | Bidirectional integration with FHIR-compliant EHR systems |
| Webhook framework | Event-driven integrations with external care platforms |
| SSO / Identity federation | SAML 2.0 / OIDC for enterprise identity providers |
| API public documentation | Developer portal for integration partners |
| Multi-tenant architecture | Isolated tenants with independent configuration |

---

## Phase 5 — Scale & Clinical Validation (Year 2 Q2–Q4)

**Objective**: Clinical validation, regulatory readiness, and scale.

**Deliverables:**

| Feature | Description |
|---|---|
| Clinical outcome study | Prospective study correlating Lumina flags with clinical outcomes |
| Bias & equity audit | Demographic performance analysis of risk models |
| Regulatory documentation | Clinical decision support tool classification documentation |
| SOC 2 Type II | Security and availability compliance certification |
| Clinical governance module | Director-facing AI transparency and audit tooling |
| Research data export | Anonymized, consent-gated research data pipeline |

---

## Deprioritized (Not in Roadmap)

These items have been explicitly evaluated and deprioritized:

| Item | Reason |
|---|---|
| Patient-facing AI assistant | Requires different clinical safety posture; separate product track |
| Insurance risk scoring | Ethical conflict with clinical mission |
| Autonomous note generation | Clinical accountability concerns |
| Consumer mental wellness features | Out of clinical scope |

---

## How the Roadmap Evolves

The roadmap is reviewed at the end of each phase. Changes require:
- Evidence of clinical utility (or disutility) from the current phase
- Ethics review for any new AI capability
- Clinician input on priority ordering

The roadmap is a living document — not a commitment. Clinical evidence and user feedback take precedence over the original plan.
