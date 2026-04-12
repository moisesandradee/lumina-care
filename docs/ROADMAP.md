# Roadmap do Produto — Lumina

> **Documento de ideação.** Este roadmap representa a trajetória conceitual proposta para o Lumina. As fases descrevem sequências lógicas de construção — não compromissos de entrega firmados.

## Filosofia do Roadmap

O roadmap do Lumina é sequenciado para construir confiança clínica antes de expandir o escopo clínico. Nenhuma capacidade seria adicionada mais rápido do que sua segurança e utilidade podem ser validadas. Cada fase entregaria algo que um clínico pode genuinamente usar antes de construir a próxima camada.

---

## Fase 1 — Fundação (Conceito)

**Objetivo**: Entregar um núcleo de inteligência de triagem funcional, seguro e implantável.

**Horizonte estimado**: Q1–Q2

**Entregas propostas:**

| Funcionalidade | Descrição | Status |
|---|---|---|
| Core API | Backend FastAPI com autenticação, modelo de paciente, endpoints de avaliação | 📐 Conceito |
| Motor de Análise de Risco | Pontuação e priorização com PHQ-9, GAD-7, C-SSRS | 📐 Conceito |
| Serviço de Triagem por IA | Análise de sinais via Claude com saída estruturada | 📐 Conceito |
| Dashboard Clínico MVP | Fila de prioridade, lista de pacientes, visualização básica de risco | 📐 Conceito |
| Log de Auditoria | Registro imutável de outputs de IA e acessos | 📐 Conceito |
| Autenticação & RBAC | JWT com controle de acesso baseado em função (clínico/coordenador/diretor) | 📐 Conceito |
| Deploy Docker | Implantação local e em nuvem com um comando | 📐 Conceito |

**Critérios de saída da Fase 1:**
- API aprovada em revisão clínica para enquadramento seguro de outputs
- Motor de risco validado contra conjuntos de dados de referência
- Dois clínicos concluem testes de usabilidade com feedback positivo

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
