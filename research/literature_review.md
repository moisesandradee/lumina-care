# Literature Review — Clinical Foundations

## Purpose

This document summarizes the clinical evidence base informing Lumina's risk scoring logic, AI prompt design, and product philosophy. All clinical frameworks implemented in the platform are grounded in peer-reviewed literature.

---

## 1. Assessment Instruments

### PHQ-9 (Patient Health Questionnaire-9)

**Primary reference**: Kroenke K, Spitzer RL, Williams JB. "The PHQ-9: validity of a brief depression severity measure." J Gen Intern Med. 2001;16(9):606-613.

**Severity thresholds used in Lumina**:

- 1–4: Minimal depression symptoms
- 5–9: Mild depression symptoms
- 10–14: Moderate depression symptoms
- 15–19: Moderately severe depression symptoms
- 20–27: Severe depression symptoms

**Clinical note**: PHQ-9 is a self-report instrument. Lumina uses it as one signal among several — not as a standalone diagnostic tool. Item 9 (suicidal ideation item) is specifically flagged for enhanced clinical review.

---

### GAD-7 (Generalized Anxiety Disorder-7)

**Primary reference**: Spitzer RL, Kroenke K, Williams JB, Löwe B. "A brief measure for assessing generalized anxiety disorder." Arch Intern Med. 2006;166(10):1092-1097.

**Severity thresholds used in Lumina**:

- 0–4: Minimal anxiety symptoms
- 5–9: Mild anxiety symptoms
- 10–14: Moderate anxiety symptoms
- 15–21: Severe anxiety symptoms

---

### C-SSRS (Columbia Suicide Severity Rating Scale)

**Primary reference**: Posner K, et al. "The Columbia-Suicide Severity Rating Scale: initial validity and internal consistency findings from three multisite studies." Am J Psychiatry. 2011;168(12):1266-1277.

**Implementation in Lumina**: Binary flags for ideation presence and behavior presence are used as the primary safety signal layer. Any C-SSRS positive response triggers immediate escalation logic — not AI analysis.

---

## 2. Care Gap and Engagement

### Treatment Dropout in Outpatient Mental Health

**Reference**: Edlund MJ, et al. "Dropout from mental health treatment: patterns and predictors." J Nerv Ment Dis. 2002;190(4):239-247.

**Key finding**: Rates of premature termination from outpatient mental health treatment range from 30–50%. Early identification of engagement risk is associated with better retention outcomes.

**Lumina application**: Care engagement metrics (days since last contact, appointment adherence rate) are incorporated as explicit risk dimensions in the triage model.

---

### Early Intervention and Outcomes

**Reference**: McGorry PD, et al. "Early intervention in psychosis: concepts, evidence and future directions." World Psychiatry. 2008;7(3):148-156.

**Key finding**: Early intervention at first signs of deterioration is consistently associated with better long-term outcomes in serious mental illness. The "critical period" concept underscores the time-sensitivity of clinical response.

**Lumina application**: The core value proposition of Lumina — detecting risk earlier, before crisis — is grounded in the evidence for early intervention.

---

## 3. Clinical Decision Support Systems

### AI in Mental Health: Evidence Review

**Reference**: Graham S, et al. "Artificial intelligence for mental health and mental illnesses: an overview." Curr Psychiatry Rep. 2019;21(11):116.

**Key finding**: AI applications in mental health show promise for screening, prediction, and personalization, but clinical deployment requires careful attention to explainability, bias, and integration into clinical workflow.

**Lumina application**: Lumina's design choices — explainability-first, advisory framing, clinical workflow integration — are directly informed by this evidence base.

---

### Clinician Adoption of Decision Support Tools

**Reference**: Sittig DF, et al. "Grand challenges in clinical decision support." J Biomed Inform. 2008;41(2):387-392.

**Key finding**: Clinician adoption of decision support tools is strongly predicted by: fit with workflow, transparency of recommendations, and ability to override.

**Lumina application**: The override mechanism, workflow integration priority, and explainability architecture are responses to the empirical evidence on adoption barriers.

---

## 3. Limitations and Gaps

This literature review is not comprehensive. Lumina's clinical evidence base requires:

- [ ] Review by a practicing mental health clinician
- [ ] Formal literature search on AI-assisted triage in outpatient mental health settings
- [ ] Review of LGPD/CFP (Conselho Federal de Psicologia) guidance on technology in psychological practice
- [ ] Assessment of instrument validity in Brazilian clinical population contexts

These gaps will be addressed before any production clinical deployment.
