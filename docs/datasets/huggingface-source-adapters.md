# Hugging Face Source Adapters

The adapters export approved public source data into source-preserving JSONL manifests. They do not combine label spaces, claim production eligibility, or upload data to Git.

## FUNSD

`nielsr/funsd` includes images, words, bounding boxes, and NER tags. It may be used for research-only LayoutLM token-classification transfer/evaluation after terms review. Its noisy forms are not identity documents.

## CORD v2

`naver-clova-ix/cord-v2` supplies receipt images, JSON ground-truth structures, and `valid_line` word quadrilaterals with hierarchical categories. The adapter exports BIO-tagged receipt tokens for LayoutLM token classification while retaining the full JSON target for schema-supervision and Donut comparison. Its receipt label space remains separate from FUNSD and identity fields.

## Export

```text
python datasets/adapters/hf_document_sources.py --source funsd --output-dir /content/verivision-external --acknowledge-source-terms
python datasets/adapters/hf_document_sources.py --source cord_v2 --output-dir /content/verivision-external --acknowledge-source-terms
```
