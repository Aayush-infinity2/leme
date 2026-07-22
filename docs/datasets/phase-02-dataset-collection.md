# Phase 2 — Dataset Collection, Governance, and Synthetic Data Plan

**Status:** Collection design complete. Acquisition is blocked per dataset until its recorded terms, consent basis, checksum, and retention controls are approved.

## 1. Why this component exists

Model quality is bounded by the legal provenance, capture diversity, annotation accuracy, and split discipline of its data. Identity media is biometric and high-risk PII. Therefore, VeriVision does not treat a public URL as permission to train a production model, does not commit data to Git, and does not merge datasets before preserving their source-level identity and rights.

The goal is a governed, reproducible research corpus that supports the pipeline's distinct tasks: document detection/rectification, OCR, layout extraction, bounded document QA, document-authenticity analysis, and one-to-one face verification. It is not a person-identification or surveillance corpus.

## 2. Recommended source portfolio

### Tier A — start after license capture: synthetic or mock identity documents

| Dataset | Reported scale / modality | Tasks | Access and license posture | Recommendation |
|---|---|---|---|---|
| [MIDV-2020](https://l3i-share.univ-lr.fr/MIDV2020/midv2020.html) | 1,000 annotated videos, 1,000 scans, 1,000 photos; 72,409 annotated images; mock documents with generated faces | detection, type classification, rectification, field OCR, face detection | Obtain from official hosts; capture the exact terms at download time | **Primary identity-document benchmark.** Keep official splits immutable. |
| [MIDV-500](https://arxiv.org/abs/1807.05786) / [MIDV-2019](https://arxiv.org/abs/1910.04009) | 500 clips/50 document types; 2019 stress captures | detection, OCR robustness, mobile capture | Public research data; confirm current file-level terms and attribution | Use only as a held-out domain/capture benchmark where possible. |
| Internal synthetic ID families | Generated non-government, non-deceptive templates | field extraction, document type, capture degradation, fraud simulation | First-party provenance; no personal data | **Primary PAN/Aadhaar-like/DL/passport-like training source.** Never copy official security artwork, serial formats, logos, or machine-readable zones without explicit authorization. |

There is no recommended public corpus of real Aadhaar, PAN, passport, or driving-licence images. A dataset advertised as such often has unclear consent, unlawful provenance, or redistribution risk. For production coverage, commission an opt-in collection under a data-processing agreement, use non-production test credentials/documents, and collect only the attributes required by the approved workflow.

### Tier B — document understanding and receipts

| Dataset | Reported scope | Tasks | Terms/access action | Use in VeriVision |
|---|---|---|---|---|
| [FUNSD](https://guillaumejaume.github.io/FUNSD/) | 199 noisy scanned forms with word boxes, labels, and links | KIE, relation extraction, layout | Review the distribution terms in its release; preserve attribution | Small validation/ablation set; not a production-scale training source. |
| [CORD](https://github.com/clovaai/cord) | 1,000 Korean receipts with hierarchical labels | receipt parsing, OCR-free extraction | CC BY 4.0 listed by the official repository | Train/evaluate receipt schema handling; record Korean-language scope. |
| [SROIE](https://rrc.cvc.uab.es/?ch=13) | ICDAR receipt challenge data | OCR and key information extraction | Registration/competition terms; do not mirror | Independent receipt KIE evaluation. |
| [XFUND](https://github.com/doc-analysis/XFUND) | Multilingual form-understanding benchmark | cross-lingual layout/KIE | Read the repository/dataset-card terms before acquisition | Transfer-learning analysis, not identity-document ground truth. |
| [DocVQA](https://rrc.cvc.uab.es/?ch=17&com=downloads) | document VQA; registration required | visual document QA | Registration required; capture terms/version | QA evaluation; avoid training final decision logic on it. |
| [DUDE](https://rrc.cvc.uab.es/?ch=23&com=tasks) | 5K PDFs and 18.7K train/validation QA pairs reported by organizers | long-document QA and abstention | Competition terms; record exact release | Selective QA and out-of-domain abstention evaluation. |

### Tier C — OCR pretraining and robustness

| Dataset | Reported scope | Role | Production caveat |
|---|---|---|---|
| [SynthText](https://github.com/ankush-me/SynthText) | large synthetic scene-text corpus | detector/recognizer warm-start | Scene text differs from security-document typography; use only pretraining. |
| [MJSynth / Synth90k](https://www.robots.ox.ac.uk/~vgg/data/text/) | synthetic word recognition corpus | recognizer warm-start | Validate release terms and language/character coverage. |
| [ICDAR Robust Reading](https://rrc.cvc.uab.es/) | challenge-specific real text benchmarks | robustness evaluation | Each challenge has distinct terms/splits; do not pool test data. |
| First-party synthetic field text | controlled scripts/fonts/noise | Indian-language and field-specific coverage | Track every font license and corpus source. |

### Tier D — manipulation and presentation-attack research

| Dataset | Scope | Access posture | Use |
|---|---|---|---|
| [FaceForensics++](https://github.com/ondyari/FaceForensics) | facial manipulation benchmark | application and Terms of Use; research/educational only, not commercial production data | Deepfake/presentation-attack transfer benchmark, not document-tampering ground truth. |
| [DF40](https://github.com/YZY-stack/DF40) | 40 deepfake techniques | CC BY-NC 4.0 according to official repository | Research-only robustness benchmark; never use to train a commercial release. |
| [CASIA image tampering datasets](https://github.com/namtpham/casia-image-tampering-detection) | copy-move/splicing image manipulation | access/license must be verified against original host | Classical image-tampering ablation only. |
| First-party synthetic document attacks | copy-paste, inpainting, reprint/screenshot, crop, resample, text replacement | first-party and scenario controlled | **Primary document-forgery training set**, with provenance masks. |

Do not label any pixel manipulation benchmark as an identity-document fraud dataset without evidence. Document fraud includes issuance/template/context signals that generic image datasets lack.

### Tier E — one-to-one face verification

| Dataset | Reported scope | Access posture | Role |
|---|---|---|---|
| [LFW](http://vis-www.cs.umass.edu/lfw/) | 13,233 images of 5,749 people | research dataset; record usage terms | legacy verification sanity check only. |
| [IJB-C](https://www.nist.gov/programs-projects/face-challenges) | unconstrained template/media benchmark | NIST access terms and protocol | benchmark verification/calibration if access allows. |
| Consented internal pairs | selfie-to-document portrait pairs plus capture metadata | explicit consent, DPA, deletion/revocation path | required for production calibration and demographic/capture slices. |

Never use face-recognition benchmark identities for open-set identification, cross-dataset identity linking, or training outside the source terms. Store embeddings only in the isolated biometric boundary defined in Phase 1.

## 3. Acquisition workflow and license gate

1. Create a source record in `datasets/registry.yaml`; use a stable source ID, official URL, intended task, and owner.
2. Compliance owner saves the terms snapshot, license identifier, allowed use, redistribution rule, attribution, geographic limits, consent/biometric basis, retention, and access approver in a private evidence vault. The public repository holds only the non-sensitive digest/reference.
3. Security owner approves the acquisition method. Only official hosts and authenticated download clients are permitted. Kaggle mirrors, scraped document examples, and rehosted archives are not sources of record.
4. Download into a quarantined encrypted volume outside Git. Verify archive hash/signature, malware-scan, inventory, and image/PDF decompression limits.
5. Generate a source-level immutable manifest. Normalize into a derived dataset only after schema validation and PII/provenance checks. Preserve original files read-only.
6. Create leakage-safe split assignments before augmentation. Face splits are identity-disjoint; document splits are template/issuer/capture-session disjoint; synthetic template styles are held out by family.
7. Run a deletion/revocation test. A source must be removable from training and derived artifacts through source IDs and lineage.

**Hard block:** no dataset is usable for a commercial or public deployment merely because it is downloadable. Non-commercial, research-only, benchmark-only, or unclear licenses are isolated to `research_only` and cannot enter a production training manifest.

## 4. Canonical annotation and merge architecture

Do not physically merge source archives. Store source-specific adapters and map outputs to a canonical manifest. Every row retains `source_id`, `source_sample_id`, `license_class`, `consent_class`, `split`, and content hashes.

```text
source archive (read-only) → source adapter → quarantine validation
  → canonical manifest (Parquet/JSONL) → task views
  → immutable split map → training/evaluation manifests
```

Canonical document record fields: `sample_id`, `source_id`, `media_uri`, `sha256`, `document_family`, `template_family`, `capture_channel`, `language_scripts`, `document_quad`, `fields`, `ocr_tokens`, `entities`, `table_cells`, `quality_labels`, `tamper_labels`, `mask_uri`, `face_region`, `split`, `license_class`, `consent_class`, `annotation_version`, and `lineage`.

Field values have `raw_value` (restricted), `normalized_value`, `field_type`, `geometry`, `confidence`, `annotation_source`, and `verification_status`. The restricted raw field path is excluded from standard training logs and all public artifacts.

## 5. Synthetic document generation — recommended implementation

Generate first-party, fictitious document families rather than realistic replicas of government credentials. The renderer composes approved backgrounds, synthetic portraits, fonts with recorded licenses, bilingual field generators, barcodes/QR payloads that encode only test data, optional non-official hologram-like textures, and deterministic template specifications. It must visibly mark all outputs as `SAMPLE / NOT VALID` outside the crop area used by models.

For each source scene, save a JSON provenance graph: seed, generator Git digest, template version, field values, font assets/hashes, layer geometry, document quad, text masks, face box, barcode geometry, and tamper mask. Use SynthDoG concepts as a reference, but retain a custom schema suited to identity fields.

Capture simulation is a differentiable or deterministic augmentation stage: camera perspective, rolling-shutter blur, defocus, motion blur, JPEG/WebP recompression, low light, glare, shadow, moiré, reprint, screen subpixel pattern, partial occlusion, and background clutter. Parameter distributions must be fitted from approved non-PII capture telemetry, not guessed indefinitely.

Forgery examples derive from pristine generated documents using paired transforms: field replacement, portrait substitution, copy-move, stamp/signature insertion, local inpainting, QR replacement, crop/reframe, screenshot/reprint, and composite attacks. Store image-level class, operation graph, source/target regions, and exact binary/soft masks. Include benign edits and hard negatives to prevent a model from learning compression or renderer artifacts.

## 6. Split strategy, data quality, and target composition

Maintain `train`, `validation`, `test_locked`, `challenge_locked`, and `holdout_domain` split roles. The locked sets are write-protected and never appear in hyperparameter selection. Deduplicate with perceptual hashes, OCR-normalized field similarity, face-identity clusters (inside the biometric enclave), and template fingerprints. Resolve duplicate clusters before split assignment.

Initial research target composition (not a claim of acquired data): 50–60% synthetic ID/capture/attack data, 15–25% MIDV-derived benchmark data, 10–15% generic OCR/layout transfer data, 10–15% consented real capture data once governance permits. Every experiment reports source mixture and per-source metrics; aggregate accuracy is insufficient.

Sample-level quality gates: readable resolution, valid image decoding, correct orientation, no forbidden PII class, annotation geometry within bounds, schema-valid fields, non-empty license source, source checksum, and split assignment. Review annotator agreement on field labels and tamper masks; use adjudication rather than majority vote for security-sensitive labels.

## 7. Evaluation metrics and dataset acceptance

| Task | Core measure | Required slices |
|---|---|---|
| Document detection | quad IoU, corner error, recall | blur, glare, perspective, screen/reprint, template family |
| OCR | CER, WER, normalized exact match | script, field type, resolution, capture channel |
| Field extraction | entity micro/macro F1, exact field match | template, language, absent fields, unseen issuer |
| Document QA | ANLS, exact match, abstention risk-coverage | answerability, document domain, OCR quality |
| Forgery | image/pixel AUROC, AUPRC, EER, IoU/F1 mask | attack type, postprocessing, unseen generator |
| Face verification | TAR at fixed FAR, ROC/AUC, EER, calibration | capture device, pose, illumination, quality/demographic slices where lawful |

Dataset release is accepted only if it has a source audit, reproducible manifest, leakage report, annotation QA report, split report, baseline metrics, data card, and deletion lineage test. A model may not be compared on different source mixtures or leaked templates.

## 8. Expected challenges and mitigation

| Challenge | Mitigation |
|---|---|
| PII/biometric legal constraints | synthetic-first design; explicit consent; private lineage vault; deletion workflow |
| Scarce Indian-document ground truth | fictitious first-party families; contracted opt-in collection; no web scraping |
| Synthetic-to-real domain gap | held-out real consented evaluation, capture simulation calibration, test-time robustness suite |
| Template leakage | family-level holdouts and visual near-duplicate detection |
| Forgery dataset shortcuts | paired attacks + benign controls + cross-generator/cross-compression tests |
| Demographic imbalance | lawful, consented slice monitoring; do not infer protected attributes without an approved basis |
| License drift | terms snapshots, quarterly revalidation, manifest-level `license_class` enforcement |

## 9. Implementation deliverables produced in this phase

- `datasets/registry.yaml`: versioned source inventory and intended-use firewall.
- `datasets/manifest.schema.json`: canonical manifest schema.
- `scripts/validate_dataset_manifest.py`: dependency-free structural validator for JSONL manifests.
- `docs/datasets/data-card-template.md`: mandatory data-card template.

## 10. Papers and repositories

- [MIDV-2020](https://arxiv.org/abs/2107.00396), [MIDV-500](https://arxiv.org/abs/1807.05786), and [MIDV-2019](https://arxiv.org/abs/1910.04009) for mobile identity-document benchmarks.
- [SynthDoG / Donut](https://github.com/clovaai/donut) for synthetic document generation patterns.
- [LayoutLMv3](https://arxiv.org/abs/2204.08387) and [XFUND](https://arxiv.org/abs/2206.06439) for multilingual form understanding.
- [FaceForensics++](https://arxiv.org/abs/1901.08971) and [DeepfakeBench](https://arxiv.org/abs/2307.01426) for forgery benchmark protocols.
- [ArcFace](https://arxiv.org/abs/1801.07698) and [NIST FRVT](https://pages.nist.gov/frvt/html/frvt_facerecognition.html) for face verification methodology.

## 11. Phase 2 exit criteria

- [x] Source portfolio, intended-use firewall, synthetic-first strategy, and canonical schema defined.
- [x] Acquisition, license, split, lineage, deletion, and quality-gate procedures defined.
- [x] Dataset registry, data-card template, and manifest validation tooling added.
- [ ] Each selected source has a legal terms snapshot and approved use class.
- [ ] At least one source manifest validates in quarantine and passes checksum/scan/inventory checks.
- [ ] Synthetic renderer threat-model and template review are approved before generation.
- [ ] Leakage-safe split and baseline data-quality reports are produced.

Phase 3 starts only after the four operational collection gates are complete.
