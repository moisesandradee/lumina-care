# Data Governance — Lumina

## Data Classification

| Data class              | Examples                     | Storage                   | AI access                  | Third-party access         |
| ----------------------- | ---------------------------- | ------------------------- | -------------------------- | -------------------------- |
| **Patient identity**    | Name, DOB, contact info      | Encrypted, isolated store | Never                      | Never                      |
| **Clinical signals**    | Assessment scores, care gaps | Encrypted primary DB      | De-identified signals only | Never                      |
| **AI outputs**          | Risk scores, summaries       | Encrypted, audit-logged   | N/A                        | Never                      |
| **Operational data**    | Access logs, system events   | Separate log store        | Never                      | Authorized processors only |
| **Aggregate analytics** | Team-level trends, counts    | Reporting DB              | N/A                        | Clinical leadership only   |

---

## Data Flow

```
Patient interaction
       ↓
Clinical team entry / EHR integration
       ↓
Ingestion layer (validation + normalization)
       ↓
Internal data store (encrypted, access-controlled)
       ↓
Risk analysis engine (structured signals only)
       ↓
AI service (de-identified signals only — no PII)
       ↓
AI output (structured JSON, stored in audit log)
       ↓
Clinical interface (role-filtered views)
       ↓
Clinical action + outcome logging
```

---

## Data Retention

| Data type                    | Retention period                                | Basis                |
| ---------------------------- | ----------------------------------------------- | -------------------- |
| Patient clinical data        | Duration of care + jurisdiction-mandated period | Legal requirement    |
| AI audit logs                | 7 years                                         | Clinical governance  |
| Access logs                  | 2 years                                         | Security audit       |
| De-identified aggregate data | Indefinite                                      | Research/improvement |
| Deleted patient data         | Purged within 30 days of request                | LGPD/GDPR compliance |

---

## Access Control Matrix

| Role              | Patient records         | AI outputs        | Team analytics | System admin |
| ----------------- | ----------------------- | ----------------- | -------------- | ------------ |
| Clinician         | Own patients only       | Own patients only | No             | No           |
| Coordinator       | Assigned panel          | Assigned panel    | No             | No           |
| Clinical Director | De-identified aggregate | Team summary      | Yes            | No           |
| System Admin      | Audit logs only         | Audit logs only   | No             | Yes          |

---

## Third-Party Data Processors

| Processor                     | Data shared                      | Purpose       | Agreement    |
| ----------------------------- | -------------------------------- | ------------- | ------------ |
| Anthropic (Claude API)        | De-identified clinical signals   | AI analysis   | DPA required |
| Cloud infrastructure provider | Encrypted data at rest           | Hosting       | DPA required |
| Monitoring provider           | System metrics (no patient data) | Observability | DPA required |

No patient data is shared with parties not listed above.

---

## Incident Response

Data breach response procedure:

1. Contain — isolate affected system within 1 hour of detection
2. Assess — determine scope of exposed data within 4 hours
3. Notify — inform affected patients and regulators within timeframes required by applicable law (LGPD: 72 hours to ANPD for significant breaches)
4. Remediate — implement fix and post-incident review within 7 days
5. Document — full incident report within 30 days
