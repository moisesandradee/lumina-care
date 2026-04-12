# API Documentation

RESTful API reference for Lumina Care backend.

**Base URL:** `http://localhost:8000` (development)  
**Version:** 0.1.0

---

## 📋 Overview

Lumina Care API provides three main endpoint groups:

- **Triage** — Patient risk assessment and prioritization
- **Insights** — AI-generated clinical recommendations
- **Patients** — Patient data management

All endpoints return JSON. Authentication via Bearer token (development: optional).

---

## 🏥 Health Endpoints

### GET /health

Server health check.

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{
  "status": "ok",
  "service": "lumina-care-api",
  "version": "0.1.0"
}
```

**Status Codes:**

- `200` — Service is healthy

---

### GET /ready

Readiness check — confirms dependent services accessible.

```bash
curl http://localhost:8000/ready
```

**Response:**

```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "cache": "ok",
    "ai_service": "ok"
  }
}
```

**Status Codes:**

- `200` — All services ready
- `503` — Service unavailable

---

## 🚨 Triage Endpoints

### POST /api/v1/triage

Submit patient assessment for risk triage and prioritization.

```bash
curl -X POST http://localhost:8000/api/v1/triage \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-123",
    "phq9_score": 18,
    "gad7_score": 15,
    "clinical_notes": "Patient reports persistent sadness and anxiety",
    "risk_indicators": ["suicidal_ideation"]
  }'
```

**Request Body:**

```json
{
  "patient_id": "string",              // Unique patient identifier (required)
  "phq9_score": 0-27,                  // Depression severity (required)
  "gad7_score": 0-21,                  // Anxiety severity (required)
  "clinical_notes": "string",          // Clinician notes (required)
  "risk_indicators": ["string"]        // Risk flags: suicidal_ideation, self_harm, substance_use, etc.
}
```

**Response (201):**

```json
{
  "patient_id": "patient-123",
  "triage_id": "triage-abc123",
  "priority": "high",
  "risk_level": "moderate",
  "recommended_actions": [
    "Schedule immediate mental health assessment",
    "Consider psychiatric consultation"
  ],
  "timestamp": "2024-04-12T10:30:00Z"
}
```

**Status Codes:**

- `200/201` — Triage completed
- `400` — Invalid request
- `422` — Validation error
- `500` — Server error

**PHQ-9 Interpretation:**

- 0-4: Minimal
- 5-9: Mild
- 10-14: Moderate
- 15-19: Moderately severe
- 20-27: Severe

**GAD-7 Interpretation:**

- 0-4: Minimal
- 5-9: Mild
- 10-14: Moderate
- 15-21: Severe

---

## 💡 Insights Endpoints

### POST /api/v1/insights

Generate AI-powered clinical insights and recommendations.

```bash
curl -X POST http://localhost:8000/api/v1/insights \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-123",
    "assessment_data": {
      "phq9_score": 18,
      "gad7_score": 15,
      "clinical_notes": "Symptoms worsening"
    }
  }'
```

**Request Body:**

```json
{
  "patient_id": "string",           // Patient identifier (required)
  "assessment_data": {              // Assessment context (required)
    "phq9_score": 0-27,
    "gad7_score": 0-21,
    "clinical_notes": "string"
  }
}
```

**Response (200):**

```json
{
  "patient_id": "patient-123",
  "insights": [
    {
      "category": "diagnosis",
      "confidence": 0.85,
      "text": "Symptoms consistent with major depressive disorder..."
    },
    {
      "category": "recommendations",
      "confidence": 0.92,
      "text": "Consider SSRI medication combined with therapy..."
    }
  ],
  "generated_at": "2024-04-12T10:35:00Z"
}
```

**Status Codes:**

- `200` — Insights generated
- `400` — Invalid request
- `500` — AI service error

---

## 👥 Patient Endpoints

### GET /api/v1/patients

List all patients.

```bash
curl http://localhost:8000/api/v1/patients
```

**Response (200):**

```json
[
  {
    "id": "patient-123",
    "name": "João Silva",
    "age": 35,
    "email": "joao@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### POST /api/v1/patients

Create new patient.

```bash
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "age": 35,
    "email": "joao@example.com",
    "phone": "11999999999"
  }'
```

**Request Body:**

```json
{
  "name": "string",              // Patient name (required)
  "age": 18-120,                 // Patient age (required)
  "email": "email@domain.com",   // Email (required)
  "phone": "string"              // Phone number (optional)
}
```

**Response (201):**

```json
{
  "id": "patient-123",
  "name": "João Silva",
  "age": 35,
  "email": "joao@example.com",
  "created_at": "2024-04-12T10:40:00Z"
}
```

---

### GET /api/v1/patients/{id}

Retrieve single patient.

```bash
curl http://localhost:8000/api/v1/patients/patient-123
```

**Response (200):**

```json
{
  "id": "patient-123",
  "name": "João Silva",
  "age": 35,
  "email": "joao@example.com",
  "medical_record_number": "MRN-12345",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-04-12T10:40:00Z"
}
```

**Status Codes:**

- `200` — Patient found
- `404` — Patient not found

---

### PUT /api/v1/patients/{id}

Update patient.

```bash
curl -X PUT http://localhost:8000/api/v1/patients/patient-123 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "age": 36
  }'
```

**Response (200):**

```json
{
  "id": "patient-123",
  "name": "João Silva",
  "age": 36,
  "updated_at": "2024-04-12T10:45:00Z"
}
```

---

### DELETE /api/v1/patients/{id}

Delete patient.

```bash
curl -X DELETE http://localhost:8000/api/v1/patients/patient-123
```

**Status Codes:**

- `204` — Patient deleted
- `404` — Patient not found

---

## 🔐 Authentication

Currently in development mode (optional). Production will use:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/v1/patients
```

---

## 📊 Response Codes

| Code  | Meaning                                |
| ----- | -------------------------------------- |
| `200` | OK — Request successful                |
| `201` | Created — Resource created             |
| `400` | Bad Request — Invalid input            |
| `401` | Unauthorized — Auth required           |
| `404` | Not Found — Resource doesn't exist     |
| `422` | Validation Error — Invalid data format |
| `500` | Server Error — Unexpected error        |
| `503` | Service Unavailable — Dependency down  |

---

## 📚 Interactive Documentation

**Swagger UI:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc

Try endpoints directly in the browser!

---

## 🧪 Testing Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Readiness
curl http://localhost:8000/ready

# List patients
curl http://localhost:8000/api/v1/patients

# Create patient
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","age":30,"email":"test@example.com"}'

# Triage assessment
curl -X POST http://localhost:8000/api/v1/triage \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"test","phq9_score":15,"gad7_score":12,"clinical_notes":"test","risk_indicators":[]}'
```

---

**Next:** [DATABASE.md](./DATABASE.md) — Database schema and migrations
