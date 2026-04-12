# Deployment Guide

Production deployment for Lumina Care.

**Status:** ⚠️ Development → Production Ready (Phase 3)

---

## 🚀 Deployment Overview

### Current Stage

- ✅ Development environment fully functional
- ✅ CI/CD pipeline implemented
- ⏳ Production deployment in Phase 3

### Deployment Strategy

**Manual Deployment (Current)**

1. Merge PR to `master` (triggers CI/CD)
2. Wait for all checks to pass
3. Deploy manually to staging/production

**Automated Deployment (Phase 3)**

1. Merge to `master`
2. GitHub Actions automatically deploys to production
3. No manual intervention needed

---

## 🔧 Prerequisites for Production

### Infrastructure Requirements

- ✅ PostgreSQL 15+ managed database (AWS RDS, GCP Cloud SQL, etc.)
- ✅ Redis 7+ cache layer (AWS ElastiCache, GCP Memorystore, etc.)
- ✅ Container registry (Docker Hub, AWS ECR, GCP Artifact Registry)
- ✅ Load balancer (AWS ALB, GCP Cloud Load Balancer)
- ✅ SSL/TLS certificates (AWS ACM, Let's Encrypt)
- ✅ CDN for static assets (CloudFront, Cloudflare, etc.)
- ✅ Monitoring & logging (DataDog, New Relic, Splunk, etc.)

### API Keys & Secrets

```bash
# Required production secrets (GitHub Secrets)
ANTHROPIC_API_KEY        # AI service key
DATABASE_URL            # PostgreSQL connection string
REDIS_URL              # Redis connection string
SECRET_KEY             # Django-style session secret
ENVIRONMENT            # "production"
```

### Monitoring & Alerts

- ✅ Error tracking (Sentry)
- ✅ Performance monitoring (New Relic, DataDog)
- ✅ Log aggregation (ELK Stack, Splunk)
- ✅ Uptime monitoring (Pingdom, Datadog)

---

## 📦 Docker Containerization

### Dockerfile (Backend)

```dockerfile
# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

# Runtime stage
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.cache/pypoetry /root/.cache/pypoetry
COPY --from=builder /root/.venv /root/.venv
COPY src ./src

ENV PATH="/root/.venv/bin:$PATH"
EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile (Frontend)

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY src/web ./
RUN npm run build

# Runtime stage
FROM node:20-alpine

WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY public ./public
COPY package.json ./

EXPOSE 3000
CMD ["npm", "start"]
```

### Build Images

```bash
# Backend
docker build -t lumina-care-api:latest -f Dockerfile.api .
docker tag lumina-care-api:latest gcr.io/project/lumina-care-api:latest
docker push gcr.io/project/lumina-care-api:latest

# Frontend
docker build -t lumina-care-web:latest -f Dockerfile.web .
docker tag lumina-care-web:latest gcr.io/project/lumina-care-web:latest
docker push gcr.io/project/lumina-care-web:latest
```

---

## ☁️ Cloud Deployment

### Google Cloud Platform (Recommended)

**1. Setup Project**

```bash
gcloud projects create lumina-care
gcloud config set project lumina-care
```

**2. Deploy Backend**

```bash
# Push to Artifact Registry
docker push gcr.io/lumina-care/lumina-api:latest

# Deploy to Cloud Run
gcloud run deploy lumina-api \
  --image gcr.io/lumina-care/lumina-api:latest \
  --platform managed \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 100 \
  --set-env-vars ANTHROPIC_API_KEY=xxx,DATABASE_URL=xxx
```

**3. Deploy Frontend**

```bash
gcloud run deploy lumina-web \
  --image gcr.io/lumina-care/lumina-web:latest \
  --platform managed \
  --memory 1Gi \
  --max-instances 100
```

### AWS Deployment

**1. ECR Setup**

```bash
aws ecr create-repository --repository-name lumina-api
aws ecr get-login-password | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/lumina-api:latest
```

**2. ECS Deployment**

```bash
# Create ECS task definition and service
aws ecs create-service \
  --cluster lumina-production \
  --service-name lumina-api \
  --task-definition lumina-api:1 \
  --desired-count 2 \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...
```

---

## 🌍 Environment Configuration

### Production .env

```bash
# API Configuration
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-with-secrets>

# Database
DATABASE_URL=postgresql://user:password@db.prod.example.com:5432/lumina_care
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# Cache
REDIS_URL=redis://cache.prod.example.com:6379/0
CACHE_TTL=3600

# AI Service
ANTHROPIC_API_KEY=<production-key>
AI_MODEL=claude-3-opus

# Security
CORS_ORIGINS=https://lumina-care.example.com
ALLOWED_HOSTS=api.lumina-care.example.com

# Logging
LOG_LEVEL=INFO
SENTRY_DSN=https://...@sentry.io/...

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-key>

# Monitoring
DATADOG_API_KEY=<datadog-key>
NEW_RELIC_LICENSE_KEY=<new-relic-key>
```

---

## 🔒 Security Hardening

### HTTPS/TLS

```bash
# AWS ACM Certificate
aws acm request-certificate \
  --domain-name lumina-care.example.com \
  --validation-method DNS

# Attach to load balancer
aws elbv2 create-listener \
  --load-balancer-arn arn:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:...
```

### DDoS Protection

- Enable CloudFlare or AWS Shield Standard (free)
- Consider AWS Shield Advanced for enterprise

### Secrets Management

```bash
# Store secrets in GitHub Secrets
# OR use cloud native:
gcloud secrets create ANTHROPIC_API_KEY --replication-policy="automatic"
gcloud secrets versions add ANTHROPIC_API_KEY --data-file=- < api_key.txt

# Access in cloud run
gcloud run deploy ... --update-secrets ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest
```

### Database Encryption

```sql
-- Enable encryption at rest (AWS RDS)
aws rds create-db-instance \
  --storage-encrypted \
  --kms-key-id arn:aws:kms:...
```

---

## 📊 Monitoring & Logging

### Application Metrics

```python
# Example: Datadog instrumentation
from datadog import initialize, api
import logging

dd_options = {
    'api_key': os.getenv('DATADOG_API_KEY'),
    'app_key': os.getenv('DATADOG_APP_KEY')
}
initialize(**dd_options)

# Track custom metrics
api.Metric.send(
    metric="lumina.triage.completed",
    points=1,
    tags=["env:production", "service:api"]
)
```

### Health Checks

```yaml
# Load balancer health check
health_check:
  enabled: true
  healthy_threshold: 2
  unhealthy_threshold: 3
  timeout: 5
  interval: 30
  path: /health
  expected_status: 200
```

### Log Aggregation

```bash
# ELK Stack or Cloud Logging
# Send logs to centralized system
# Query example:
# service:api AND level:ERROR AND timestamp:[NOW-1h TO NOW]
```

---

## 🔄 Continuous Deployment

### GitHub Actions Workflow

```yaml
name: Deploy to Production

on:
  push:
    branches: [master]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: make test

      - name: Build Docker image
        run: |
          docker build -t gcr.io/project/api:${{ github.sha }} .
          docker push gcr.io/project/api:${{ github.sha }}

      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v0
        with:
          service: lumina-api
          image: gcr.io/project/api:${{ github.sha }}

      - name: Smoke test
        run: |
          curl https://api.lumina-care.example.com/health
```

---

## 🚨 Incident Response

### Rollback Procedure

```bash
# If deployment fails:
# 1. Identify issue
# 2. Revert to previous version
gcloud run services update-traffic lumina-api \
  --to-revisions LATEST=0,PREVIOUS=100

# 3. Investigate and fix
# 4. Deploy again
```

### Incident Runbook

1. **Detect:** Monitoring alerts fire (error rate > 5%, latency > 2s)
2. **Alert:** PagerDuty notification to on-call engineer
3. **Respond:**
   - Check logs: `kubectl logs -f deployment/lumina-api`
   - Check metrics: DataDog dashboard
   - Check dependencies: database, cache, AI service
4. **Mitigate:**
   - Scale up if load issue
   - Rollback if code issue
   - Enable feature flags to disable problematic features
5. **Resolve:** Fix root cause and deploy
6. **Postmortem:** Document what happened and improvements

---

## 📈 Scaling

### Horizontal Scaling

```yaml
# Kubernetes HPA example
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: lumina-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: lumina-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### Database Scaling

```bash
# Read replicas (AWS RDS)
aws rds create-db-instance-read-replica \
  --db-instance-identifier lumina-care-replica \
  --source-db-instance-identifier lumina-care-primary

# Point reads to replica, writes to primary
DATABASE_READ_URL=postgresql://...replica...
DATABASE_WRITE_URL=postgresql://...primary...
```

---

## ✅ Pre-Deployment Checklist

- [ ] All tests passing (CI/CD green)
- [ ] Code reviewed and approved
- [ ] Environment variables configured
- [ ] Database migrations tested
- [ ] Secrets stored securely
- [ ] Monitoring/alerts configured
- [ ] Backup strategy in place
- [ ] Rollback plan documented
- [ ] SSL/TLS certificates valid
- [ ] Load test completed
- [ ] Stakeholders notified
- [ ] Runbook up to date

---

## 📞 Support

- **On-call:** Check PagerDuty for current engineer
- **Escalation:** Contact platform team lead
- **Post-incident:** File retro meeting in JIRA

---

**Status:** Phase 3 task  
**Owner:** Platform Engineering Team
