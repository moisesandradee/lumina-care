# Clinical Boundaries — Lumina

## What Lumina Can Do

| Capability                   | Description                                                         | Clinical status |
| ---------------------------- | ------------------------------------------------------------------- | --------------- |
| Risk signal detection        | Identify psychosocial risk patterns from structured assessment data | Advisory        |
| Care gap detection           | Flag patients outside care plan contact frequency                   | Informational   |
| Priority queue generation    | Order patients by computed risk for team review                     | Advisory        |
| Session preparation briefing | Summarize longitudinal data for pre-session review                  | Advisory        |
| Team analytics               | Aggregate, de-identified service intelligence                       | Informational   |
| Trend analysis               | Longitudinal trajectory of clinical indicators                      | Advisory        |

---

## What Lumina Cannot Do

These capabilities are explicitly excluded — not by technical limitation, but by deliberate ethical and clinical design:

| Excluded capability                                   | Why excluded                                                                |
| ----------------------------------------------------- | --------------------------------------------------------------------------- |
| Diagnose mental health conditions                     | Requires licensed clinical training and therapeutic relationship            |
| Prescribe or recommend specific treatments            | Clinical decision requiring licensed authority                              |
| Respond to or manage acute crisis                     | Immediate human clinical response required; AI intervention contraindicated |
| Generate therapy content for patients                 | Different safety profile; out of scope for clinical team tool               |
| Make autonomous care decisions                        | Human authority is non-delegable in clinical settings                       |
| Replace any component of the therapeutic relationship | Ethically inviolable                                                        |
| Score insurance risk                                  | Ethical conflict; risk of discriminatory application                        |
| Generate clinical documentation autonomously          | Accuracy and accountability are clinician responsibilities                  |

---

## The Escalation Boundary

When Lumina detects signals consistent with any of the following, escalation to a human clinician is **mandatory and immediate**:

- Suicidal ideation (any C-SSRS positive ideation item)
- Suicidal behavior (any C-SSRS positive behavior item)
- Self-harm disclosure
- Acute psychiatric crisis indicators

In these scenarios:

- AI does not attempt to respond or provide guidance
- Human clinician is notified with urgency indicator
- All other Lumina outputs for that patient are suppressed until clinician reviews
- If no clinician acknowledges within defined timeframe, coordinator is notified for escalation

---

## Clinical Validation Requirements

Before any AI capability is deployed in a clinical setting, it must:

1. Be reviewed by at least one licensed mental health clinician with product context
2. Pass output review — a sample of 50+ outputs reviewed for safety, framing, and accuracy
3. Be documented with clear scope, limitations, and known failure modes
4. Have a monitoring plan in place for post-deployment performance tracking

These requirements apply to new capabilities and to significant changes to existing capabilities.
