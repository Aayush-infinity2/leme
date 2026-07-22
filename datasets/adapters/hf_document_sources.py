#!/usr/bin/env python3
"""Export approved Hugging Face document sources into VeriVision manifests.

The exporter preserves source task boundaries: FUNSD provides token geometry for
LayoutLM-style experiments; CORD v2's Hub representation provides image/JSON
schema targets but no OCR token boxes, so it is excluded from OCR-dependent
LayoutLM training.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from datasets import load_dataset


def write_jsonl(path: Path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def export_funsd(output: Path) -> None:
    dataset = load_dataset("nielsr/funsd")
    tag_names = dataset["train"].features["ner_tags"].feature.names
    for split in dataset.keys():
        records = []
        image_dir = output / "images" / "funsd" / split
        image_dir.mkdir(parents=True, exist_ok=True)
        for row in dataset[split]:
            image_path = image_dir / f"{row['id']}.png"
            row["image"].convert("RGB").save(image_path)
            tokens = [{"text": word, "bbox": bbox, "source_label": tag_names[tag]} for word, bbox, tag in zip(row["words"], row["bboxes"], row["ner_tags"])]
            records.append({"sample_id": f"funsd-{split}-{row['id']}", "source_id": "nielsr_funsd", "source_sample_id": row["id"], "media_uri": image_path.resolve().as_uri(), "document_family": "noisy_form", "task_eligibility": ["layoutlm_token_classification", "key_value_extraction_evaluation"], "tokens": tokens, "split": split, "license_class": "research_only", "consent_class": "restricted_research", "annotation_version": "hf-nielsr-funsd"})
        write_jsonl(output / "manifests" / f"funsd_{split}.jsonl", records)


def export_cord(output: Path) -> None:
    dataset = load_dataset("naver-clova-ix/cord-v2")
    for split in dataset.keys():
        records = []
        image_dir = output / "images" / "cord_v2" / split
        image_dir.mkdir(parents=True, exist_ok=True)
        for index, row in enumerate(dataset[split]):
            sample_id = f"cord-v2-{split}-{index:05d}"
            image_path = image_dir / f"{sample_id}.png"
            row["image"].convert("RGB").save(image_path)
            records.append({"sample_id": sample_id, "source_id": "naver_clova_ix_cord_v2", "source_sample_id": str(index), "media_uri": image_path.resolve().as_uri(), "document_family": "receipt", "task_eligibility": ["schema_supervision", "donut_comparator", "receipt_extraction_evaluation"], "ground_truth": row["ground_truth"], "excluded_from": ["layoutlm_token_classification"], "exclusion_reason": "Hub representation has no source OCR words or bounding boxes.", "split": split, "license_class": "research_only", "consent_class": "restricted_research", "annotation_version": "hf-naver-clova-ix-cord-v2"})
        write_jsonl(output / "manifests" / f"cord_v2_{split}.jsonl", records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["funsd", "cord_v2"], required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--acknowledge-source-terms", action="store_true")
    args = parser.parse_args()
    if not args.acknowledge_source_terms:
        raise SystemExit("Refusing export: review the official dataset terms and pass --acknowledge-source-terms.")
    if args.source == "funsd":
        export_funsd(args.output_dir)
    else:
        export_cord(args.output_dir)
    print(f"exported={args.source} output={args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
