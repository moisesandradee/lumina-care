# CI_GOVERNANCE

## Purpose

This document defines how CI should be interpreted and evolved inside the `lumina-care` repository.

Its purpose is to prevent mixed signals.
A hybrid repository cannot be governed well if conceptual files, partial application code, and executable trust modules all fail under the same undifferentiated validation logic.

---

## Core principle

CI must reflect repository reality.

Today, `lumina-care` contains three distinct layers:

1. **Concept layer** — product thesis, strategy, architecture, ethics
2. **Partial application layer** — illustrative or incomplete frontend/backend structures
3. **Operational proof layer** — executable trust and verification components, especially `phantom-seal/`

A mature CI strategy must treat these layers differently.

---

## Governance rule

**Do not mix unrelated execution domains in the same validation track.**

In practical terms:
- a PhantomSeal failure should not be caused by unrelated frontend issues;
- a documentation formatting issue should not weaken confidence in the operational proof layer;
- an illustrative application scaffold should not be mistaken for production-readiness signals.

---

## Recommended CI domains

### 1. PhantomSeal CI

Scope:
- `phantom-seal/`
- Python dependencies specific to signing and verification
- trust artifact generation
- verification flow

Goal:
- prove that the operational trust module is stable on its own terms

### 2. Validate / Application Quality

Scope:
- `src/web/`
- `src/api/`
- Next.js / TypeScript checks
- Python linting for future backend code

Goal:
- improve code quality in the application layer without overstating platform maturity

### 3. Docs / Format

Scope:
- markdown consistency
- formatting rules
- documentation hygiene

Goal:
- preserve repository readability and professionalism

---

## Interpretation rule for external readers

CI must communicate discipline, not illusion.

A passing workflow should mean one of the following:
- a real executable component passed;
- a code-quality domain passed;
- a documentation hygiene check passed.

It should never imply that the entire Lumina platform is operational if only one domain succeeded.

---

## Recommended naming convention

Suggested workflow names:

- `phantomseal-ci.yml`
- `app-validate.yml`
- `docs-format.yml`

These names make repository maturity legible at a glance.

---

## Pull request discipline

Each PR should state which domain it touches:

- `concept`
- `docs`
- `proof`
- `ci`
- `app`

This makes reviews more reliable and prevents governance drift.

---

## Final principle

The role of CI in `lumina-care` is not to perform theater.
It is to create proportion between what is claimed and what is actually validated.

That proportion is what gives the repository technical credibility.
