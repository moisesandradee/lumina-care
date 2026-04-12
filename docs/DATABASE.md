# Database Guide

PostgreSQL schema, migrations, and operations.

**Version:** PostgreSQL 15+

---

## 📊 Database Schema

### Core Tables

#### patients

```sql
CREATE TABLE patients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  age INTEGER NOT NULL CHECK (age >= 0 AND age <= 150),
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(20),
  medical_record_number VARCHAR(50) UNIQUE,
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patients_email ON patients(email);
CREATE INDEX idx_patients_status ON patients(status);
```

#### assessments

```sql
CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL REFERENCES patients(id),
  assessment_type VARCHAR(50) NOT NULL,  -- 'PHQ9', 'GAD7', etc.
  score INTEGER NOT NULL,
  interpretation VARCHAR(50),
  clinical_notes TEXT,
  completed_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assessments_patient ON assessments(patient_id);
CREATE INDEX idx_assessments_type ON assessments(assessment_type);
CREATE INDEX idx_assessments_date ON assessments(completed_at DESC);
```

#### triage_results

```sql
CREATE TABLE triage_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL REFERENCES patients(id),
  assessment_id UUID REFERENCES assessments(id),
  priority VARCHAR(20) NOT NULL,  -- 'critical', 'high', 'normal'
  risk_level VARCHAR(20) NOT NULL,
  risk_indicators TEXT[],
  recommended_actions TEXT[],
  clinician_notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  reviewed_at TIMESTAMP,
  reviewed_by VARCHAR(255)
);

CREATE INDEX idx_triage_patient ON triage_results(patient_id);
CREATE INDEX idx_triage_priority ON triage_results(priority);
CREATE INDEX idx_triage_created ON triage_results(created_at DESC);
```

#### ai_insights

```sql
CREATE TABLE ai_insights (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL REFERENCES patients(id),
  triage_id UUID REFERENCES triage_results(id),
  category VARCHAR(50),  -- 'diagnosis', 'recommendations', etc.
  confidence DECIMAL(3,2),
  insight_text TEXT NOT NULL,
  model_version VARCHAR(50),
  human_reviewed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_insights_patient ON ai_insights(patient_id);
CREATE INDEX idx_insights_reviewed ON ai_insights(human_reviewed);
CREATE INDEX idx_insights_created ON ai_insights(created_at DESC);
```

#### audit_log

```sql
CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR(255),
  action VARCHAR(100) NOT NULL,
  resource_type VARCHAR(50),
  resource_id VARCHAR(255),
  changes JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ip_address INET
);

CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_created ON audit_log(created_at DESC);
CREATE INDEX idx_audit_resource ON audit_log(resource_type, resource_id);
```

---

## 🔄 Migrations

### Run Migrations

```bash
# Forward
poetry run python src/lib/db/migrate.ts

# Rollback (development only)
poetry run python src/lib/db/migrate.ts rollback

# Status
poetry run python src/lib/db/migrate.ts status
```

### Create New Migration

```bash
# Alembic (if configured)
alembic revision --autogenerate -m "Add new column to patients"

# Manual
cat > migrations/002_add_phone_to_patients.sql << 'EOF'
-- Add phone column
ALTER TABLE patients ADD COLUMN phone VARCHAR(20);

-- Down: ALTER TABLE patients DROP COLUMN phone;
EOF
```

---

## 📊 Data Models (Python)

### Patient Schema

```python
from pydantic import BaseModel, EmailStr

class PatientCreate(BaseModel):
    name: str
    age: int
    email: EmailStr
    phone: Optional[str] = None

class PatientResponse(BaseModel):
    id: str
    name: str
    age: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
```

### Assessment Schema

```python
class AssessmentCreate(BaseModel):
    patient_id: str
    assessment_type: str  # 'PHQ9', 'GAD7'
    score: int
    clinical_notes: Optional[str] = None

    @validator('score')
    def validate_score(cls, v, values):
        assessment_type = values.get('assessment_type')
        if assessment_type == 'PHQ9' and not 0 <= v <= 27:
            raise ValueError('PHQ9 score must be 0-27')
        if assessment_type == 'GAD7' and not 0 <= v <= 21:
            raise ValueError('GAD7 score must be 0-21')
        return v
```

---

## 🔑 Queries

### Find Patients by Risk Level

```sql
SELECT p.*, t.priority, t.created_at
FROM patients p
LEFT JOIN triage_results t ON p.id = t.patient_id
WHERE t.priority = 'high'
ORDER BY t.created_at DESC;
```

### Recent Assessments

```sql
SELECT p.name, a.assessment_type, a.score, a.completed_at
FROM patients p
JOIN assessments a ON p.id = a.patient_id
WHERE a.completed_at >= NOW() - INTERVAL '7 days'
ORDER BY a.completed_at DESC;
```

### Patient Assessment History

```sql
SELECT * FROM assessments
WHERE patient_id = $1
ORDER BY completed_at DESC;
```

### AI Insights Without Review

```sql
SELECT * FROM ai_insights
WHERE human_reviewed = FALSE
ORDER BY created_at DESC;
```

---

## 🔐 Data Protection

### PII Encryption

Sensitive fields should be encrypted:

```python
from cryptography.fernet import Fernet

# Encrypt on write
cipher = Fernet(encryption_key)
encrypted_email = cipher.encrypt(patient.email.encode())

# Decrypt on read
decrypted = cipher.decrypt(encrypted_email).decode()
```

### Access Control

```sql
-- Only clinicians can view assessments
SELECT * FROM assessments
WHERE patient_id = $1
AND clinician_id IN (
  SELECT id FROM clinicians
  WHERE clinic_id = $2
);
```

### Audit Logging

Every data access logged:

```python
@app.get("/api/v1/patients/{patient_id}")
async def get_patient(patient_id: str, current_user: User):
    # Log access
    await log_audit(
        user_id=current_user.id,
        action="READ",
        resource_type="patient",
        resource_id=patient_id
    )
    return patient
```

---

## 📦 Backup & Recovery

### Backup

```bash
# Full backup
pg_dump -U postgres lumina_care > backup.sql

# Compressed
pg_dump -U postgres lumina_care | gzip > backup.sql.gz

# Using Docker
docker exec postgres-container pg_dump -U postgres lumina_care > backup.sql
```

### Restore

```bash
# From SQL file
psql -U postgres lumina_care < backup.sql

# From compressed
gunzip -c backup.sql.gz | psql -U postgres lumina_care
```

### Schedule Backups

```bash
# Daily backup at 2am (crontab)
0 2 * * * pg_dump -U postgres lumina_care | gzip > /backups/lumina_$(date +\%Y\%m\%d).sql.gz
```

---

## 🧹 Data Maintenance

### Delete Old Audit Logs

```sql
DELETE FROM audit_log
WHERE created_at < NOW() - INTERVAL '90 days';
```

### Archive Completed Assessments

```sql
-- Move to archive table (if configured)
INSERT INTO assessments_archive
SELECT * FROM assessments
WHERE completed_at < NOW() - INTERVAL '1 year';

DELETE FROM assessments
WHERE completed_at < NOW() - INTERVAL '1 year';
```

### Vacuum & Analyze

```bash
# Optimize database
vacuumdb -U postgres lumina_care
analyzedb -U postgres lumina_care

# Scheduled (cron)
0 3 * * 0 vacuumdb -U postgres lumina_care
```

---

## 🔍 Monitoring

### Check Database Size

```sql
SELECT pg_database.datname,
       pg_size_pretty(pg_database_size(pg_database.datname))
FROM pg_database
WHERE datname = 'lumina_care';
```

### Table Sizes

```sql
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Active Connections

```sql
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;
```

### Slow Queries

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## 🆘 Troubleshooting

### Connection Refused

```bash
# Check PostgreSQL running
psql -U postgres -c "SELECT 1;"

# Restart
brew services restart postgresql@15
# or
docker restart postgres-container
```

### Disk Space

```bash
# Check usage
df -h /var/lib/postgresql

# Archive and delete old data
# (implement data retention policy)
```

### Corruption

```bash
# Verify
vacuumdb --analyze-in-stages -U postgres lumina_care

# Reindex if needed
reindexdb -U postgres lumina_care
```

---

**Next:** [DEPLOYMENT.md](./DEPLOYMENT.md) — Deployment guide
