# VeriVision AI — Boundary Contracts

## API versioning

All externally visible REST endpoints are namespaced under `/v1`. Backward-compatible fields may be added; breaking changes require a new version. OpenAPI is the source of truth and generated from FastAPI Pydantic models.

## Verification state machine

`RECEIVED → VALIDATING → PREPROCESSING → EXTRACTING → ANALYZING → DECIDING → COMPLETED`

Terminal alternatives are `REJECTED`, `FAILED_RETRYABLE`, `FAILED_FINAL`, and `EXPIRED`. Only the orchestration service may transition state. Workers publish evidence and never set a final decision.

## Canonical request

```json
{
  "tenant_id": "uuid",
  "subject_reference": "opaque-client-reference",
  "workflow": "india_kyc_v1",
  "artifacts": [{"artifact_id": "uuid", "kind": "document_front", "sha256": "hex"}],
  "idempotency_key": "uuid"
}
```

Raw bytes are uploaded directly to object storage using a short-lived, single-use presigned URL. The API never places image bytes on RabbitMQ, Redis, application logs, MLflow, or W&B.

## Evidence event envelope

```json
{
  "event_id": "uuid",
  "event_type": "ocr.completed",
  "schema_version": 1,
  "verification_id": "uuid",
  "artifact_id": "uuid",
  "producer": "ocr-worker",
  "occurred_at": "RFC3339 UTC",
  "trace_id": "W3C traceparent trace id",
  "model": {"name": "paddleocr-det-rec", "version": "registry-stage@digest"},
  "payload_uri": "s3://restricted/evidence/...",
  "payload_sha256": "hex"
}
```

Events contain references to encrypted evidence, not PII. Consumers validate JSON Schema, event type, version, checksum, and idempotency key.

## Decision contract

The policy service returns `APPROVE`, `REVIEW`, or `REJECT`, plus a calibrated confidence, applicable policy/model versions, and machine-readable reason codes. `REJECT` is reserved for deterministic invalidity or explicitly approved high-confidence policy rules; uncertain ML signals route to `REVIEW`. Never expose biometric embeddings, document numbers, or internal fraud heuristics to clients.

## Model input/output contracts

- Preprocessing emits an immutable derivative manifest: source digest, transforms, geometric transform matrix, quality metrics, and output URI.
- OCR emits token text, normalized text, confidence, quadrilateral geometry, language/script, and recognizer version.
- Layout extraction emits fields with source spans, normalized values, confidence, and provenance. It must not overwrite raw OCR.
- Face verification emits only similarity score, calibrated probability, threshold version, quality/liveness gates, and optional encrypted embedding URI restricted to the biometric service.
- Forgery analysis emits a calibrated image-level score, attack taxonomy probabilities, heatmap URI, and model version. A heatmap is explanatory evidence, not proof of manipulation.

