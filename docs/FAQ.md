# FAQ — Lumina

## Product

**Is Lumina a mental health app for patients?**  
No. Lumina is a clinical intelligence tool for mental health care teams — psychologists, psychiatrists, care coordinators, and clinical directors. Patients interact with their care team as normal; Lumina makes that team more effective.

**Does Lumina diagnose mental health conditions?**  
No. Lumina explicitly does not diagnose. It identifies risk signals, flags clinical patterns, and surfaces prioritization recommendations. Every output is labeled as advisory and requires human clinical review.

**Can Lumina replace a psychologist or psychiatrist?**  
No, and it is not designed to. Lumina is built on the premise that the clinical relationship is irreplaceable. It provides intelligence to support the clinician — it does not substitute for clinical judgment, therapeutic relationship, or clinical responsibility.

**How is Lumina different from a risk assessment checklist?**  
A checklist is static, point-in-time, and requires manual interpretation. Lumina is dynamic — it tracks change over time, synthesizes multiple data sources, integrates longitudinal context, and proactively surfaces patterns. It turns a snapshot into a trajectory.

---

## AI and Technology

**What AI model does Lumina use?**  
Lumina uses Anthropic's Claude as its primary language model. Clinical outputs use structured prompt templates designed and validated for clinical safety.

**Does raw patient data get sent to Anthropic?**  
No. Only de-identified, structured clinical signals are transmitted to the AI provider. No names, dates of birth, contact information, or free-text clinical notes containing PII are included in AI prompts.

**What happens if the AI is wrong?**  
Clinicians can override any AI output with one click. Overrides are logged. The AI is an advisory system — the clinician is always the decision-maker. If a clinician consistently overrides a particular type of AI output, that's valuable signal for model improvement.

**Can Lumina explain why it flagged a patient?**  
Yes. Every risk flag includes human-readable reasoning, the clinical signals that contributed to it, confidence level, and references to the clinical frameworks informing the assessment. There are no black-box outputs.

---

## Privacy and Security

**Is patient data encrypted?**  
Yes. All patient-linked data is encrypted at rest (AES-256) and in transit (TLS 1.3). Access is role-controlled and fully auditable.

**Does Lumina sell patient data?**  
Never. Patient data is used exclusively to provide the clinical intelligence service. It is not sold, licensed, or shared with any third party for non-clinical purposes.

**What data does Lumina collect?**  
Lumina collects structured clinical assessment data (assessment scores, interaction logs, care plan data) that is entered by care team members or integrated from existing clinical systems. It does not record therapy sessions, collect biometric data, or access communication content.

**Is Lumina LGPD / GDPR compliant?**  
Lumina is designed with LGPD (Brazil) and GDPR (EU) principles as baseline requirements. Formal compliance certification will be obtained prior to production deployment in regulated markets.

---

## Clinical Safety

**What happens if a patient expresses suicidal ideation?**  
Lumina includes hard-coded escalation logic for acute safety signals. Any pattern consistent with suicidal ideation or acute self-harm risk is immediately flagged to the assigned clinician with an urgent indicator. Lumina does not attempt to respond to, manage, or resolve acute safety events — these require immediate human clinical response.

**What if Lumina misses a high-risk patient?**  
Lumina is a support tool, not a safety net. Clinical teams retain full responsibility for patient safety using all available information and clinical judgment. Lumina is designed to reduce the probability of missed signals — not to be the only system responsible for catching them.

**Has Lumina been clinically validated?**  
The underlying clinical instruments (PHQ-9, GAD-7, C-SSRS) are extensively validated. Lumina's AI layer is currently in MVP development. Clinical validation of Lumina's risk outputs against patient outcomes is planned for Phase 5. We are transparent about the distinction between validated instruments and validated AI application.

---

## Deployment

**What's needed to deploy Lumina?**  
Docker and Docker Compose for local/cloud deployment. An Anthropic API key for the AI layer. PostgreSQL and Redis for data persistence. See the README for full setup instructions.

**Is Lumina available as a hosted service?**  
Cloud-hosted SaaS is on the roadmap. The current release is self-hosted. This gives healthcare organizations full control over their data environment.

**Can Lumina integrate with our existing EHR?**  
Direct HL7 FHIR integration is planned for Phase 4. Currently, Lumina integrates via REST API, which can be connected to most modern EHR systems with appropriate middleware. Contact us to discuss your integration requirements.
