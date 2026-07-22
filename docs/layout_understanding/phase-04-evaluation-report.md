# Phase 4 — Evaluation Report and Release Decision

## Decision

**Research pipeline: pass. Production identity-field release: no-go.**

The project has demonstrated reproducible LayoutLMv3 training, source-isolated label spaces, synthetic renderer/template/geometry robustness, and two external Document AI baselines. It has not evaluated document identity fields against approved identity-document data. Therefore, no model may be represented as ready for identity extraction or promotion to the decision service.

## Reproducible evidence

| Experiment | Data / split | Primary result | Interpretation |
|---|---|---:|---|
| Synthetic v1 pipeline validation | 400/50/50 one-template fictitious credential | test loss 0.0437 | validates training path only |
| Synthetic v2 template holdout | 600/200/200; held-out template | entity F1 1.000 | controlled transfer only |
| Synthetic v3 renderer + box jitter | 800/100/100; held-out renderer/template; 12 px eval jitter | entity F1 1.000 | robustness plumbing works; renderer remains shared codebase |
| FUNSD external baseline | 134/15/50; native form labels | entity F1 0.278 | realistic small-data transfer baseline |
| CORD v2 external baseline | 800/100/100; native receipt labels | entity F1 0.668 | receipt extraction baseline; separate label space |

Canonical experiment records are in `experiments/phase-04/`. Scores are not comparable across the synthetic, FUNSD, and CORD tasks because they have different domains, labels, distributions, and split protocols.

## Required identity-evaluation manifest

An identity-document source must provide, per sample:

- immutable source/sample ID, source terms snapshot, license class, and retention/deletion reference;
- image or video-frame URI and SHA-256; document/template/issuer family; capture-session/device ID where permitted;
- document quadrilateral plus field annotations for the in-scope workflow (for example name, document number, DOB, issue/expiry date), with source geometry and annotation provenance;
- OCR tokens/word quadrilaterals or permission to run and retain a versioned OCR pass;
- quality/capture slices: scan/mobile, blur, glare, perspective, resolution, low light, crop/occlusion, and reprint/screenshot where available;
- split assignment that is template-, issuer-, and capture-session-disjoint; no random image-level split;
- explicit prohibition/approval metadata for training, evaluation, model publication, and redistribution.

For a first external identity evaluation, target at least 500 examples across five or more held-out template/capture families. Do not tune on its locked test partition.

## Release gates before Phase 5

- [x] Synthetic multi-renderer/template and OCR-box-jitter test executed.
- [x] External form and receipt LayoutLMv3 baselines executed on native labels.
- [x] Per-source manifests preserve source ID, terms class, and task boundaries.
- [ ] Approved identity-document manifest acquired and schema-validated.
- [ ] Identity-field entity F1, literal/normalized exact match, calibration, latency, and failure slices reported on locked data.
- [ ] Error taxonomy and human-review thresholds approved.
- [ ] Signed LayoutLMv3 model bundle with pinned OCR release and reproducible environment created.

Only the unfinished gates block Phase 5. The external acquisition requires an authorized terms acceptance or a consented internal collection; do not replace it with scraped government documents.
