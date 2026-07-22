# VeriVision AI

Production-oriented multimodal identity-verification and document-intelligence research platform.

## Status

**Active gate: Phase 1 — System Design.** The implemented baseline is the architecture, data contracts, threat model, and reproducible repository layout. Training data, model weights, and inference services are deliberately not included until their respective gated phases begin.

Read the Phase 1 design before running or extending this repository:

- [System architecture](docs/architecture/phase-01-system-design.md)
- [API and event contracts](docs/architecture/contracts.md)
- [Architecture decision records](docs/architecture/adr/README.md)

## Principles

- No real identity document or biometric is committed to the repository.
- Raw PII and biometric media are isolated, encrypted, access-controlled, and deletion-aware.
- Deterministic policy checks remain distinct from probabilistic ML signals.
- Every inference is model-versioned, traceable, and reproducible.

