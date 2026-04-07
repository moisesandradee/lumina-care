# Demo Guide — Lumina

## Overview

This directory contains demo scenarios, sample data, and walkthrough guides for evaluating Lumina in a development or demonstration context.

---

## Demo Scenario 1: Morning Triage Workflow

**Goal**: Demonstrate the priority queue and risk analysis capabilities.

**Setup**:
1. Start the application: `docker-compose up`
2. Open `http://localhost:3000/dashboard`
3. The dashboard displays a pre-populated mock priority queue

**What to show**:
- Priority queue ordered by risk score
- Risk level badges (low / moderate / high / acute)
- Days-since-contact indicator with color coding
- Recommended action per patient
- Override functionality with one click

---

## Demo Scenario 2: Triage API Analysis

**Goal**: Show the triage API processing assessment data and returning structured AI analysis.

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/triage/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "demo_patient_001",
    "assessments": {
      "phq9": {
        "total_score": 16,
        "assessed_at": "2024-04-01T10:00:00Z"
      },
      "gad7": {
        "total_score": 12,
        "assessed_at": "2024-04-01T10:00:00Z"
      },
      "cssrs": {
        "ideation_present": false,
        "behavior_present": false,
        "assessed_at": "2024-04-01T10:00:00Z"
      },
      "days_since_last_contact": 15,
      "appointment_adherence_rate": 0.65
    },
    "include_ai_analysis": true,
    "requesting_clinician_id": "demo_clinician_001"
  }'
```

**Expected output**: Risk level `high`, priority score ~75, AI analysis with reasoning, recommended action `URGENT_CLINICAL_REVIEW`.

---

## Demo Scenario 3: Team Intelligence Dashboard

**API call**:
```bash
curl "http://localhost:8000/api/v1/insights/team-summary?care_team_id=team_alpha"
```

**What to show**: Aggregate risk distribution, care continuity metrics, trend indicators — all de-identified.

---

## Demo Scenario 4: Acute Safety Escalation

**Goal**: Demonstrate hard-coded safety escalation logic.

**Request** (same as Scenario 2, but with C-SSRS positive):
```json
"cssrs": {
  "ideation_present": true,
  "ideation_intensity": 5,
  "behavior_present": true,
  "assessed_at": "2024-04-01T10:00:00Z"
}
```

**Expected output**: Risk level `ACUTE`, `requires_override_review: true`, recommended action `IMMEDIATE_ESCALATION`, AI analysis will include `escalation_required: true`.

---

## Interactive API Documentation

With the application running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
