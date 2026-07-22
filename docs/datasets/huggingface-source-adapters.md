# Hugging Face Source Adapters

The adapters export approved public source data into source-preserving JSONL manifests. They do not combine label spaces, claim production eligibility, or upload data to Git.

## FUNSD

`nielsr/funsd` includes images, words, bounding boxes, and NER tags. It may be used for research-only LayoutLM token-classification transfer/evaluation after terms review. Its noisy forms are not identity documents.

## CORD v2

`naver-clova-ix/cord-v2` supplies receipt images and JSON ground-truth structures. Its Hub form does not expose OCR word boxes, so it is not eligible for OCR-dependent LayoutLM training. Use it for schema-supervision, Donut comparison, and receipt extraction evaluation.

## Export

```text
python datasets/adapters/hf_document_sources.py --source funsd --output-dir /content/verivision-external --acknowledge-source-terms
python datasets/adapters/hf_document_sources.py --source cord_v2 --output-dir /content/verivision-external --acknowledge-source-terms
```
