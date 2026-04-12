# Cenários de Uso Propostos — Lumina

> **Documento de ideação.** Os cenários abaixo são propostas conceituais — descrevem como o Lumina se comportaria em uso real, não demonstrações de um sistema funcional.

## Visão Geral

Este diretório contém cenários de uso, dados de exemplo e guias de walkthrough que ilustram o funcionamento proposto do Lumina em contexto clínico real.

---

## Cenário 1: Triagem da Manhã

**Objetivo**: Ilustrar as capacidades de fila de prioridade e análise de risco.

**Proposta de experiência**:
- Dashboard abre com fila de prioridade pré-calculada
- Pacientes ordenados por score de risco
- Badges de nível de risco (baixo / moderado / alto / agudo)
- Indicador de dias-sem-contato com codificação de cores
- Ação recomendada por paciente
- Override clínico com um clique — sempre disponível

**Como seria no produto:**
1. Profissional acessa `http://localhost:3000/dashboard`
2. Visualiza fila priorizada gerada pelos modelos de risco
3. Revisa os 3 pacientes com maior variação de sinal nas últimas 48h
4. Confirma ou ajusta prioridade antes da reunião de equipe

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
