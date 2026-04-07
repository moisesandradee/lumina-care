# AI Strategy — Lumina

## Philosophy: AI as Clinical Amplifier

The temptation in AI-powered healthcare products is to position AI as the primary value driver — to make it the hero. Lumina takes the opposite approach.

**AI in Lumina is infrastructure, not identity.**

The clinical relationship — the trust between patient and clinician, the judgment built over years of practice, the irreducibly human act of care — is the hero. AI is what makes that hero more effective.

This is not modesty. It is a deliberate product strategy grounded in three beliefs:

1. Clinicians will adopt AI tools that augment their judgment, not ones that threaten it
2. Patient safety requires that a human is always accountable for care decisions
3. The most defensible AI in healthcare is AI that knows its own boundaries

---

## AI Capabilities in Lumina

### Capability 1: Psychosocial Risk Signal Analysis

**What it does**: Analyzes structured assessment data (PHQ-9, GAD-7, C-SSRS, WHO-5, etc.) alongside longitudinal interaction data to identify risk signal patterns that warrant clinical attention.

**What it does not do**: Diagnose. Predict with certainty. Make clinical decisions.

**How it works**:
```
Input: Structured patient signals (de-identified)
       + Temporal context (trend data, care gaps)
       + Clinical framework references

Prompt architecture: System prompt with safety constraints
                   + Clinical context template
                   + Specific analysis request

Output: Structured JSON with:
        - risk_indicators: list of identified signals
        - severity_estimate: low/moderate/high/acute
        - confidence: 0.0–1.0
        - reasoning: human-readable explanation
        - recommended_actions: advisory list
        - escalation_required: boolean
        - evidence_refs: clinical framework citations
```

### Capability 2: Care Journey Gap Detection

**What it does**: Identifies deviations from agreed care plans — missed appointments, assessment gaps, communication lapses — and generates prioritized outreach recommendations.

**Model approach**: Rule-based engine for deterministic gap detection, augmented by LLM for natural language summary generation and contextual prioritization.

### Capability 3: Clinical Summary Generation

**What it does**: Synthesizes longitudinal patient data into structured session-prep summaries for clinicians — highlighting what has changed, what remains stable, and what warrants discussion.

**Critical constraint**: Summaries are explicitly framed as "information for review" not "clinical conclusions." Clinicians can accept, edit, or dismiss any generated content.

---

## Prompt Architecture

Lumina uses a layered prompt architecture designed for clinical safety:

### Layer 1: System Prompt (Fixed, versioned)
Establishes the AI's clinical role, capabilities, and hard constraints:
- "You are a clinical decision support system, not a diagnostic tool"
- "You must never suggest a specific diagnosis"
- "If acute safety risk is detected, escalation is mandatory regardless of other analysis"
- "All outputs must include confidence estimates and reasoning"

### Layer 2: Clinical Context Template
Injects patient context using a strict schema — no free-text PII, only structured clinical signals:
```
Assessment scores: {phq9_score}, {gad7_score}, {cssrs_flag}
Trend direction: {symptom_trend_30d}
Care engagement: {days_since_last_contact}, {appointment_adherence_rate}
Active flags: {open_risk_flags}
```

### Layer 3: Task-Specific Request
Specifies what kind of analysis or output is required, with explicit output schema.

### Layer 4: Output Validation
Every AI response is validated against a Pydantic schema before being passed to the application layer. Malformed or out-of-bounds responses trigger graceful fallback to manual review queue.

---

## Model Selection

**Primary model**: Anthropic Claude (claude-3-5-sonnet)

**Why Claude**:
- Strong performance on structured reasoning tasks
- Reliable adherence to system prompt constraints
- Consistently refuses inappropriate clinical requests
- Supports structured output (JSON mode)
- Anthropic's safety-focused development aligns with Lumina's ethical commitments

**Fallback strategy**: If AI service is unavailable, Lumina degrades gracefully — risk queues remain functional via rule-based scoring; AI-generated content fields display "pending review" rather than breaking the interface.

---

## AI Governance Model

### Transparency
- Every AI output is labeled as AI-generated
- Confidence scores are always displayed alongside outputs
- Reasoning is always accessible — never hidden in a black box

### Accountability
- Every AI interaction is logged with model version, prompt hash, and output hash
- Clinical overrides are recorded and attributed
- Monthly model performance review against clinical outcome data (when available)

### Continuous Improvement
- Override rates by output type are monitored (high override rate = low utility)
- Clinician feedback can be attached to any AI output
- Prompt versions are tracked and A/B testable

### Hard Limits
These behaviors are hardcoded and not configurable by any user:
- Acute safety risk signals always trigger human escalation
- No clinical decision can be attributed to AI alone in any documentation
- AI outputs cannot be shared directly with patients without clinician review

---

## What We Are Not Building

| AI pattern | Why we reject it |
|---|---|
| Autonomous treatment recommendations | Requires clinical licensure and accountability |
| Patient-facing mental health chatbot | Different risk profile, different regulatory posture |
| Predictive readmission scoring for payers | Risk of discriminatory insurance application |
| Sentiment analysis of therapy transcripts | Patient trust and consent implications too complex for v1 |
| Autonomous clinical note generation | Documentation accuracy is a clinical and legal responsibility |

These are not permanent exclusions — some may be revisited with appropriate clinical validation and ethics review. But they are out of scope for the current phase of development.
