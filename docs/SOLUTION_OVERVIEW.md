# Solution Overview — Lumina

## What Lumina Is, Precisely

Lumina is a **clinical intelligence platform** for mental health care teams.

It processes structured clinical data — assessment scores, care interaction logs, appointment history, digital check-ins — and transforms it into actionable intelligence that helps clinicians and coordinators prioritize attention, detect risk earlier, and maintain care continuity.

It does not replace any part of the clinical relationship. It replaces the information gap between sessions.

---

## How the Solution Works

### Step 1: Data Ingestion
Patient clinical data enters Lumina through:
- Direct assessment entry (via web interface)
- API integration with existing EHR / care management systems
- Digital patient check-ins (between-session touchpoints)

### Step 2: Signal Processing
The risk analysis engine processes incoming data against validated clinical instruments and computes:
- Individual risk dimension scores (safety, functioning, engagement, trajectory)
- Composite psychosocial risk score
- Delta from previous assessment (what changed, in which direction)

### Step 3: AI Analysis
For patients flagged by the risk engine, the AI service generates:
- Human-readable signal summary
- Clinical context interpretation
- Priority level recommendation
- Suggested next actions (advisory)
- Confidence estimate and reasoning

### Step 4: Clinical Interface
Processed intelligence is surfaced to the care team through:
- Priority queue (who needs attention today)
- Patient-specific intelligence view (what has changed)
- Session-prep briefings (what to know before the next appointment)
- Team-level dashboard (where attention should be concentrated)

### Step 5: Clinical Action and Feedback Loop
Clinicians act — or override — and log outcomes. This feedback:
- Updates patient trajectory data
- Informs future risk assessments
- Provides override data for model performance monitoring

---

## What Makes This Approach Different

### 1. Clinical framework-grounded AI
Lumina does not use raw LLM inference for risk assessment. AI interpretation is constrained by validated clinical instruments (PHQ-9, GAD-7, C-SSRS) and structured prompt templates that encode clinical logic. The result is AI that reasons *with* clinical evidence, not independently of it.

### 2. Designed for clinical trust
Every output includes confidence, reasoning, and a one-click override. Clinicians control the system — the system never controls the clinician. This is the only design that earns clinical adoption.

### 3. Between-session reach
Most deterioration happens in the 7–14 days between sessions. Lumina is the only layer of the care system that monitors the space between appointments — not by replacing the therapeutic relationship, but by extending clinical awareness into that gap.

### 4. Team intelligence, not just individual tools
Care is delivered by teams. Lumina surfaces team-level intelligence — caseload distribution, risk concentration, care plan adherence — that enables better coordination and resource allocation.

---

## Core Platform Components

| Component | Description |
|---|---|
| **Triage Engine** | Automated psychosocial risk scoring and priority ranking |
| **AI Intelligence Layer** | Claude-powered signal analysis with clinical constraints |
| **Care Continuity Monitor** | Real-time care gap and engagement tracking |
| **Clinical Dashboard** | Team and individual patient intelligence interface |
| **Audit System** | Immutable log of all AI outputs and clinical overrides |
| **Assessment Module** | Structured intake of validated clinical instruments |

---

## Integration Approach

Lumina is designed to complement existing clinical infrastructure, not replace it. In the current phase:

- Standalone deployment with manual data entry
- API-first architecture enables integration with any EHR system that supports standard APIs
- Phase 4 introduces native HL7 FHIR adapter for deep EHR integration

This progression allows Lumina to deliver value immediately, without depending on complex integration projects that can delay deployment by months.

---

## Value Proposition Summary

| Stakeholder | Before Lumina | With Lumina |
|---|---|---|
| **Clinician** | Reviews 38 charts manually to find who needs attention | Opens priority queue: 5 patients flagged with reasons |
| **Coordinator** | Discovers care gap after patient drops out | Alert generated 4 days before gap becomes dropout |
| **Director** | Monthly reports on last month's data | Real-time risk dashboard updated daily |
| **Patient** | Deteriorates between sessions undetected | Deterioration flagged within 48 hours for clinical review |
