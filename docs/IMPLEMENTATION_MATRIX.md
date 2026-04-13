# IMPLEMENTATION_MATRIX

## Purpose

This document clarifies what is conceptual, what is partially implemented, and what is operational inside the `lumina-care` repository.

It exists to prevent ambiguity.

Lumina combines:
- a product thesis,
- a proposed clinical intelligence architecture,
- partial illustrative code,
- and an operational trust component currently under validation.

---

## Implementation Matrix

| Component | Nature | Status | Execution Level | Notes |
|---|---|---|---|---|
| `README.md` | Product thesis | Strong | Non-executable | Defines the product vision, architecture, use cases, and ethical framing |
| `docs/` strategy files | Conceptual documentation | Strong | Non-executable | Core product, safety, roadmap, and positioning artifacts |
| `pitch/` | Executive narrative | Partial | Non-executable | Supports presentation and strategic communication |
| `demo/` | Demo narrative | Partial | Non-executable | Intended for walkthroughs and product storytelling |
| `research/` | Research support | Partial | Non-executable | Literature and conceptual reference base |
| `prompts/` | AI prompt architecture | Partial | Semi-structured | Useful for design intent, not proof of validated clinical performance |
| `src/api/` | Backend reference architecture | Partial | Illustrative / partial | Represents intended FastAPI structure, not a production-ready service |
| `src/web/` | Frontend reference architecture | Partial | Illustrative / partial | Represents intended Next.js interface structure, not a validated application |
| `phantom-seal/` | Trust and auditability module | Active | Executable / under validation | Main operational proof track in the repository today |
| `.github/workflows/` | Operational governance | Active | Executable | Primary short-term signal of technical discipline and reliability |
| `docker-compose.yml` | Reference infrastructure | Partial | Reference only | Describes intended local stack, not proof of full integrated execution |
| `.env.example` | Setup scaffold | Partial | Reference only | Supports implementation intent, not deployment readiness |

---

## Execution Levels

### 1. Non-executable
Documentation, positioning, and design artifacts.
These define what Lumina is trying to become.

### 2. Reference only
Files that describe the intended implementation path, but do not by themselves prove the system works end to end.

### 3. Illustrative / partial
Code or structures that represent architectural intent, but should not be interpreted as production-grade validated software.

### 4. Executable / under validation
Components that already run in a meaningful way and can be checked through workflows, scripts, or explicit local execution.

### 5. Production-ready
Not currently applicable to the repository as a whole.

---

## Current Interpretation

The correct reading of `lumina-care` today is:

- **Lumina** is a rigorously documented mental health intelligence thesis;
- **PhantomSeal** is the repository’s clearest operational proof component;
- the rest of the stack is best understood as proposed architecture, partial scaffolding, or illustrative implementation.

This is not a weakness.
It is a governance clarification.

The value of the repository comes from being explicit about what is real today, what is being validated, and what is still proposed.

---

## What Is Real Today

What can be defended with the highest confidence today:

- the product thesis;
- the ethical positioning;
- the proposed architecture;
- the existence of an operational trust module (`phantom-seal/`);
- the use of CI as a discipline mechanism.

What should **not** yet be overstated:

- full end-to-end clinical platform execution;
- validated clinical performance of the AI layer;
- production-grade frontend/backend integration;
- deployment readiness.

---

## Recommended Reading Order

For external readers:

1. `README.md`
2. `docs/REPO_STATUS.md`
3. `docs/IMPLEMENTATION_MATRIX.md`
4. `phantom-seal/README.md` *(when available)*
5. architecture and roadmap documents

This order helps readers understand the repository with the right expectations.
