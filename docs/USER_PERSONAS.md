# User Personas — Lumina

## Overview

Lumina serves three primary user types, each with distinct needs, workflows, and success criteria. Every design and product decision is evaluated against the impact it has on these personas.

---

## Persona 1: The Responsible Clinician

**Name**: Dr. Beatriz Tavares  
**Role**: Clinical Psychologist, Outpatient Mental Health Service  
**Experience**: 9 years in practice, 4 years in digital health settings

### Profile

Beatriz carries a caseload of 38 active patients. She is rigorous, evidence-driven, and genuinely invested in patient outcomes. She is not skeptical of technology — she is demanding of it. She has seen too many "AI solutions" that either oversimplify clinical complexity or produce outputs she can't explain to patients or supervisors.

### Core needs

- A way to quickly identify which patients need attention _before_ they reach her inbox or miss an appointment
- Structured clinical summaries that respect the complexity of the patient relationship
- AI outputs she can trust, explain, and override without friction
- Reduced administrative cognitive load without reduced clinical depth

### Pains

- Opening every session cold, with no synthesized view of what's changed since the last contact
- Missing early deterioration signals in patients who are "too stable to worry about"
- Documentation overhead that competes with clinical presence
- Zero visibility into what's happening between appointments

### How Lumina serves her

- Session-prep briefings with trajectory highlights and flagged changes
- Risk queue that surfaces patients who warrant proactive contact
- Explainable AI outputs she can discuss with colleagues and supervisors
- Audit trail that supports clinical documentation, not replaces it

### What would make her reject Lumina

- Any suggestion that the AI is "diagnosing" or "deciding"
- Outputs without clear reasoning or confidence indication
- Any breach of patient trust or data ethics
- A tool that adds administrative steps rather than removing them

---

## Persona 2: The Care Coordinator

**Name**: Marcos Dutra  
**Role**: Care Coordinator / Case Manager, Integrated Behavioral Health Team  
**Experience**: 5 years in care coordination, background in social work

### Profile

Marcos manages the care continuity for a panel of 65 patients across a multidisciplinary team. His job is to ensure no patient falls through the cracks — which is significantly harder than it sounds. He works at the intersection of clinical, administrative, and logistical complexity.

### Core needs

- A real-time view of which patients are at risk of disengaging or deteriorating
- Proactive alerts that help him prioritize outreach before crisis
- A coordination layer that reduces the number of manual touchpoints needed to keep a care plan on track
- Tools that work with his existing workflow, not against it

### Pains

- Discovering care gaps retrospectively — after a patient has already dropped out
- Managing care continuity via spreadsheets and shared inboxes
- No structured way to prioritize which of his 65 patients needs his attention most urgently today
- Being the last to know when a patient's clinical status has changed

### How Lumina serves him

- Daily priority queue: the 5 patients who most need coordination attention today, and why
- Automated care gap detection with outreach prompts
- Cross-provider care plan visibility
- Escalation triggers that route to the right team member based on risk level

### What would make him reject Lumina

- Alert fatigue — a system that flags everything flags nothing
- Outputs that require clinical expertise to interpret (he is not a clinician)
- A tool that creates more tasks than it resolves

---

## Persona 3: The Clinical Director

**Name**: Dra. Fernanda Lins  
**Role**: Clinical Director, Digital Health Platform  
**Experience**: 15 years in psychiatry, 3 years in health technology leadership

### Profile

Fernanda is responsible for clinical quality, team performance, and service design across a platform with 4,000 active patients. She is strategic, numbers-fluent, and deeply aware of the difference between metrics that matter and metrics that mislead. She is evaluating Lumina not just as a clinical tool but as an organizational capability.

### Core needs

- Aggregate intelligence: where is risk concentrated? What patterns are emerging?
- Capacity planning data: are caseloads appropriately distributed relative to risk?
- Clinical quality indicators: are care plans being followed? Are outcomes improving?
- A defensible AI governance posture she can present to regulators and clinical boards

### Pains

- Relying on monthly reports that are always 30 days out of date
- No visibility into service-level mental health risk distribution without manual chart review
- Difficulty making evidence-based resource allocation decisions
- Being responsible for AI outputs she doesn't understand or can't explain

### How Lumina serves her

- Executive dashboard: aggregate risk profile, trend lines, service utilization
- Clinical quality monitoring: adherence to care plans, outcome trajectories
- AI governance module: audit logs, override rates, model performance transparency
- Capacity planning intelligence: risk-adjusted caseload distribution recommendations

### What would make her reject Lumina

- Any liability exposure from AI outputs she cannot control or explain
- Data that tells a story she can't act on
- A system that requires more clinical governance than it provides

---

## Non-Users (Explicitly Out of Scope for v1)

| Role                   | Why out of scope                                                                  |
| ---------------------- | --------------------------------------------------------------------------------- |
| **Patients**           | Lumina v1 is a clinical team tool; patient-facing features are roadmap phase 3    |
| **Emergency services** | Crisis intervention requires different tooling and protocols                      |
| **Insurance/payers**   | Risk of misuse in coverage decisions; deliberately excluded from access           |
| **Researchers**        | Research-grade data access is a phase 4 capability, with additional ethics review |
