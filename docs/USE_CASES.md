# Use Cases — Lumina

## Overview

Each use case below describes a concrete interaction pattern between a Lumina user and the platform. These are grounded in real clinical workflows, not hypothetical scenarios.

---

## UC-01: Morning Risk Triage

**Actor**: Clinical Psychologist (Dr. Beatriz Tavares)  
**Trigger**: Beginning of clinical day  
**Precondition**: Patient panel data is current; at least one patient has new assessment data or a detected risk signal change

**Flow:**

1. Clinician opens Lumina dashboard
2. Dashboard displays **Priority Queue** — patients ordered by risk signal change in the last 48 hours
3. For each flagged patient, Lumina shows:
   - Risk level (low / moderate / high / urgent)
   - What changed (e.g., "PHQ-9 score increased 6 points since last assessment")
   - AI-generated signal summary with reasoning
   - Suggested action (e.g., "Consider same-day contact")
4. Clinician reviews, accepts or overrides priority rankings
5. Clinician uses the queue to structure their day's clinical attention

**Value delivered**: Clinician starts the day knowing where to direct attention — without manual chart review of 38 patients.

---

## UC-02: Intake Triage for New Patient

**Actor**: Care Coordinator (Marcos Dutra)  
**Trigger**: New patient intake form completed  
**Precondition**: Patient has completed structured intake assessments

**Flow:**

1. Coordinator submits intake assessment data via Lumina's triage endpoint
2. Lumina processes PHQ-9, GAD-7, and intake narrative (structured)
3. Risk profile is generated within seconds:
   - Severity estimate with confidence
   - Recommended care intensity (routine / enhanced / urgent)
   - Identified risk dimensions with reasoning
   - Suggested next step (e.g., "Assign to senior clinician; initiate within 5 days")
4. Coordinator reviews and assigns to appropriate team member
5. Assignment is logged; patient enters care journey tracking

**Value delivered**: Objective, evidence-informed triage recommendation enables faster, more consistent intake decisions.

---

## UC-03: Between-Session Risk Detection

**Actor**: System (automated) → Clinical Psychologist (notification)  
**Trigger**: Patient completes digital between-session check-in  
**Precondition**: Patient enrolled in between-session monitoring program; care plan specifies check-in cadence

**Flow:**

1. Patient completes brief digital check-in (PHQ-2 equivalent + 2 open-ended items)
2. Lumina processes check-in response
3. Risk analysis detects score increase + language patterns consistent with worsening state
4. System generates flag and notifies assigned clinician:
   - "Patient completed between-session check-in. Risk indicators suggest possible symptom worsening since last session. Clinical review recommended."
5. Clinician reviews in 2 clicks — can dismiss, log a note, or initiate contact
6. Outcome is recorded in patient timeline

**Value delivered**: Deterioration detected between appointments, not after.

---

## UC-04: Care Gap Alert

**Actor**: System (automated) → Care Coordinator (notification)  
**Trigger**: Patient exceeds planned care gap threshold  
**Precondition**: Patient has active care plan with specified contact frequency

**Flow:**

1. System detects: patient with moderate risk profile has had no care contact in 14 days (care plan specifies 10-day maximum)
2. Alert generated for assigned care coordinator: patient, risk level, days since last contact, care plan reference
3. Coordinator reviews; context shows last interaction and current risk status
4. Coordinator logs outreach attempt
5. If patient non-responsive after 2 attempts, alert escalates to assigned clinician

**Value delivered**: Care dropout is intercepted before it becomes permanent disengagement.

---

## UC-05: Session Preparation Briefing

**Actor**: Clinical Psychologist (Dr. Beatriz Tavares)  
**Trigger**: Upcoming appointment scheduled for tomorrow  
**Precondition**: Patient has at least 60 days of data in Lumina

**Flow:**

1. Evening before scheduled session, Lumina generates session-prep briefing
2. Clinician receives notification: "Session briefing ready for [Patient ID]"
3. Briefing includes:
   - 90-day symptom trajectory summary
   - Key changes since last session
   - Open flags from previous session notes
   - Risk dimension summary
   - Suggested clinical focus areas (advisory)
4. Clinician reviews on mobile, adds their own notes, and enters the session prepared

**Value delivered**: Clinician enters session with full longitudinal context — not just what they can recall from memory.

---

## UC-06: Team Capacity Planning

**Actor**: Clinical Director (Dra. Fernanda Lins)  
**Trigger**: Monthly service review  
**Precondition**: Team data populated; at least 60 days of operation

**Flow:**

1. Director opens Team Intelligence dashboard
2. Views aggregate (de-identified) data:
   - Caseload distribution by risk level across team members
   - Mean time from risk flag to clinical action
   - Care plan adherence rates by team
   - Trend in average risk profile of active patient panel
3. Identifies imbalance: one clinician carrying disproportionate share of high-risk cases
4. Uses data to make reallocation decision with clinical lead
5. Decision logged; caseload distribution monitored following month

**Value delivered**: Resource allocation decisions based on risk-adjusted data, not intuition.

---

## UC-07: Clinical Override and Annotation

**Actor**: Clinical Psychologist  
**Trigger**: Disagreement with AI-generated risk assessment  
**Precondition**: AI triage has generated a risk assessment the clinician considers incorrect

**Flow:**

1. Clinician views AI risk assessment for patient
2. Clinician disagrees with severity estimate (e.g., AI flagged moderate; clinician assesses low based on contextual knowledge)
3. Clinician clicks "Override"
4. Provides brief annotation: "Patient context: stable support system not captured in structured data. Assess as low risk."
5. Override is applied; patient's priority queue position is updated
6. Override is logged with clinician attribution for audit and model improvement

**Value delivered**: Clinical expertise always supersedes AI output; context AI cannot access is captured in the system.

---

## Anti-Use Cases (What Lumina Explicitly Prevents)

| Scenario                                                              | Why prevented                                                                            |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Using AI output to deny care                                          | Access controls prevent risk data from being shared with non-clinical actors             |
| Automated response to acute safety signals                            | Hard-coded escalation to human clinician; no AI autonomous response                      |
| Clinician delegating care decision to AI                              | Output schema and UX design make advisory framing unavoidable                            |
| Patient accessing their own AI risk scores without clinical mediation | Patient-facing access is out of scope; if implemented, requires clinical co-presentation |
