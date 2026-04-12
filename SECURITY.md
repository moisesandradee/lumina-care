# Security Policy

## 🔒 Reporting Security Vulnerabilities

**IMPORTANT:** Please do NOT publicly disclose security vulnerabilities through GitHub issues, discussions, or pull requests.

### How to Report

If you discover a security vulnerability in Lumina, please:

1. **Email the maintainers privately:**
   - Send to: [security@lumina-care.dev](mailto:security@lumina-care.dev)
   - Subject: `[SECURITY] Vulnerability in Lumina`

2. **Include the following information:**
   - Description of the vulnerability
   - Affected component(s) or file(s)
   - Severity (Critical, High, Medium, Low)
   - Steps to reproduce (if possible)
   - Potential impact
   - Suggested fix (if available)
   - Your name and contact information

3. **Expected response:**
   - Acknowledgment within 48 hours
   - Initial assessment within 1 week
   - Regular updates on remediation progress
   - Credit in security advisory (if desired)

### Responsible Disclosure Timeline

We follow responsible disclosure practices:

- **Day 0:** Vulnerability reported to maintainers
- **Days 1-2:** Initial triage and severity assessment
- **Days 3-7:** Development of fix and testing
- **Day 14:** Public disclosure and patch release
- **Day 30:** Mandatory patch deadline for installations

---

## 🛡️ Security Best Practices

### For Developers

#### Code Security

```python
# ✅ GOOD: Input validation
from pydantic import BaseModel, validator

class PatientInput(BaseModel):
    phq9_score: int
    
    @validator('phq9_score')
    def validate_score(cls, v):
        if not 0 <= v <= 27:
            raise ValueError('Score must be 0-27')
        return v

# ❌ BAD: No validation
def analyze_patient(phq9_score):
    return db.query(f"SELECT * FROM patients WHERE score={phq9_score}")
```

#### Authentication & Authorization

```python
# ✅ GOOD: Token-based auth with role checks
from fastapi import Depends
from jose import jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("sub")
    return get_user(user_id)

async def get_current_clinician(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "clinician":
        raise HTTPException(status_code=403)
    return current_user
```

#### Data Protection

```typescript
// ✅ GOOD: Redact PII before logging
const redactPII = (text: string): string => {
  return text
    .replace(/\b\d{3}-\d{2}-\d{4}\b/g, 'XXX-XX-XXXX')  // SSN
    .replace(/\b\d{10}\b/g, 'XXXXXXXXXX')              // Phone
    .replace(/[\w\.-]+@[\w\.-]+\.\w+/g, '[EMAIL]');    // Email
};

// ❌ BAD: Logging PHI unencrypted
console.log(`Patient ${patientData.ssn} has score ${score}`);
```

### For DevOps

#### Environment Management

```bash
# ✅ GOOD: Use .env.example (no secrets)
DATABASE_URL=postgresql://user:pass@localhost/lumina
ANTHROPIC_API_KEY=sk-...

# ❌ BAD: Committed secrets
# .env with actual keys in git history
```

#### Secrets in CI/CD

```yaml
# ✅ GOOD: Use GitHub Secrets
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  DATABASE_URL: ${{ secrets.DATABASE_URL }}

# ❌ BAD: Hardcoded secrets in workflow
env:
  API_KEY: sk-1234567890...
```

---

## 🔐 Security Requirements

### Application Security

- ✅ HTTPS/TLS encryption in transit
- ✅ Input validation on all endpoints
- ✅ SQL injection prevention (Pydantic, asyncpg)
- ✅ CSRF protection for state-changing operations
- ✅ Rate limiting on public endpoints
- ✅ Authentication & authorization enforced
- ✅ Password hashing (bcryptjs with salt rounds ≥ 12)
- ✅ JWT token expiration (default: 1 hour)
- ✅ CORS restrictions (allow specific origins)
- ✅ No hardcoded secrets in code

### Data Protection

- ✅ PHI encrypted at rest (AES-256)
- ✅ Patient data access logging
- ✅ Data retention policies enforced
- ✅ GDPR right-to-be-forgotten implementation
- ✅ Regular audit trails
- ✅ Data anonymization for analytics

### Infrastructure

- ✅ Least privilege IAM policies
- ✅ Network segmentation
- ✅ Firewall rules configured
- ✅ DDoS protection enabled
- ✅ Vulnerability scanning (Dependabot)
- ✅ Security headers (CSP, X-Frame-Options, etc.)
- ✅ SSL/TLS certificate monitoring

### Dependency Management

- ✅ `npm audit` / `pip audit` in CI
- ✅ Dependabot or Renovate enabled
- ✅ Regular dependency updates
- ✅ Known vulnerability scanning
- ✅ Lock files committed and up-to-date

---

## 🧪 Security Testing

### Before Deployment

```bash
# Frontend
npm run security:audit      # npm audit
npm run type-check          # Type safety
npm run test:security       # Security-focused tests

# Backend
pip install bandit
bandit -r src/api/          # Python security scanner
mypy src/api/               # Type checking
pytest -m security          # Security tests

# Both
npm run security:headers    # Check security headers
npm run security:dependencies  # Check supply chain
```

### Continuous Monitoring

- ✅ Dependabot alerts enabled
- ✅ GitHub security scanning activated
- ✅ OWASP dependency check in CI
- ✅ Regular penetration testing (scheduled)
- ✅ Security incident response plan

---

## 🚨 Incident Response

### If a Vulnerability is Discovered in the Wild

1. **Immediate Actions (first hour)**
   - Assess severity and impact scope
   - Document the vulnerability
   - Notify security team

2. **Investigation (first 24 hours)**
   - Root cause analysis
   - Determine all affected versions
   - Check exploit availability
   - Review logs for exploitation

3. **Remediation (within 7 days)**
   - Develop fix
   - Thorough testing
   - Prepare patch release
   - Write security advisory

4. **Disclosure (within 14 days)**
   - GitHub Security Advisory published
   - Patch release issued
   - Affected users notified
   - Media/community notification

---

## 📋 Security Checklist for Contributors

Before submitting a PR, verify:

- [ ] No secrets (API keys, tokens, passwords) in code
- [ ] All inputs are validated
- [ ] No hardcoded credentials
- [ ] Dependencies are up-to-date
- [ ] No SQL injection vectors
- [ ] No XSS vulnerabilities
- [ ] No CSRF vulnerabilities
- [ ] Authentication/authorization checks in place
- [ ] Error messages don't leak sensitive info
- [ ] Logging doesn't capture PHI unencrypted

---

## 🔗 Related Documents

- [CONTRIBUTING.md](CONTRIBUTING.md) — Development guidelines
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Community standards
- [ethics/ETHICS_AND_SAFETY.md](ethics/ETHICS_AND_SAFETY.md) — AI safety framework
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — Secure deployment guide

---

## 📞 Contact

**Security Team:** [security@lumina-care.dev](mailto:security@lumina-care.dev)

**Report Security Vulnerability:** See [Reporting Security Vulnerabilities](#-reporting-security-vulnerabilities) above

---

**We take security seriously. Thank you for helping keep Lumina safe. 🔒**
