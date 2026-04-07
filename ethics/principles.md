# Ethical Principles — Lumina

These principles are not aspirational. They are design constraints. Features that violate these principles are not shipped.

---

## 1. Human Authority Is Inviolable

AI outputs inform. Humans decide. Always.

No clinical action can be attributed to an AI output alone. Every recommendation, flag, and suggestion produced by Lumina is explicitly advisory. The clinician retains full authority and full accountability.

This principle is implemented technically: no endpoint or workflow allows an AI output to automatically trigger a clinical action without human confirmation.

---

## 2. Transparency Over Sophistication

A system that produces accurate outputs a clinician can't understand or explain is less valuable — and more dangerous — than a system that produces good-enough outputs with full transparency.

Lumina chooses explainability over complexity. Every AI output includes:
- The reasoning behind it
- The evidence it references
- The confidence level (with genuine uncertainty quantification)
- A clear label identifying it as AI-generated

---

## 3. Acute Safety Is Never Delegated

Suicidal ideation, self-harm, and acute psychiatric crisis are not AI problems. They are immediate human responsibilities.

Lumina's role when acute safety signals are detected: escalate to a human, immediately. The AI does not attempt to respond, manage, or resolve safety events. This boundary is hardcoded and non-negotiable.

---

## 4. Privacy Is Structural, Not Declarative

Saying "we respect patient privacy" is easy. Building a system where patient privacy protection is architecturally enforced is harder — and required.

Privacy in Lumina is implemented through:
- Data minimization (collect only what is clinically necessary)
- Encryption by default (at rest and in transit)
- Role-based access (minimum necessary access per role)
- Audit logging (every access to patient data is recorded)
- AI boundary enforcement (no PII reaches external AI providers)

---

## 5. Equity Is a Technical Requirement

AI systems inherit the biases present in their training data. In clinical contexts, those biases can translate to differential care quality across demographic groups.

Lumina treats bias monitoring as a non-optional technical requirement, not a secondary consideration. Risk models are subject to demographic performance analysis before broad deployment.

---

## 6. Clinical Boundaries Are Explicit and Enforced

Lumina knows what it is not:
- Not a diagnostic tool
- Not a crisis intervention service
- Not a therapy platform
- Not a clinical record system

These are not humility postures. They are precise technical scopes that prevent harm when AI capabilities are misapplied.

---

## 7. Ethics Governance Is Ongoing, Not One-Time

Ethical review is not a gate that a product passes through once at launch. As Lumina's capabilities evolve, the ethics review process evolves with it.

Any new AI capability, new data type, or new clinical use case requires documented ethics review before deployment. This process is lightweight enough to not impede progress — and rigorous enough to catch genuine risks.
