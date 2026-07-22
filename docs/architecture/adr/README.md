# Architecture Decision Records

| ID | Decision | Status |
|---|---|---|
| ADR-001 | Use a modular asynchronous pipeline with a synchronous control plane | Accepted |
| ADR-002 | Keep raw PII/biometrics out of queues, logs, and experiment trackers | Accepted |
| ADR-003 | Separate deterministic decision policy from model inference | Accepted |
| ADR-004 | Use PostgreSQL, S3-compatible object storage, Redis, and RabbitMQ by responsibility | Accepted |
| ADR-005 | Treat model registry promotion as a release artifact with offline evaluation gates | Accepted |

Each future consequential choice must be recorded as an ADR before implementation changes the interface, privacy boundary, or operational model.

