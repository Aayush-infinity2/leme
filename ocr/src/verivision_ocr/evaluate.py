"""JSONL evaluator for OCR predictions.

Input records require sample_id, reference, prediction and may include
field_type. The command computes corpus-weighted CER/WER (not a misleading
mean of per-sample rates), exact match, and per-field slices.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .metrics import field_normalize, levenshtein, normalize


def aggregate(rows: list[dict[str, Any]]) -> dict[str, float | int]:
    char_errors = char_total = word_errors = word_total = exact = 0
    for row in rows:
        reference = normalize(row["reference"])
        prediction = normalize(row["prediction"])
        char_errors += levenshtein(list(reference), list(prediction))
        char_total += len(reference)
        reference_words, prediction_words = reference.split(), prediction.split()
        word_errors += levenshtein(reference_words, prediction_words)
        word_total += len(reference_words)
        exact += field_normalize(reference, row.get("field_type")) == field_normalize(prediction, row.get("field_type"))
    return {
        "samples": len(rows),
        "cer": char_errors / char_total if char_total else 0.0,
        "wer": word_errors / word_total if word_total else 0.0,
        "field_exact_match": exact / len(rows) if rows else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate OCR prediction JSONL")
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--model-version", required=True)
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    with args.predictions.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            missing = {"sample_id", "reference", "prediction"} - row.keys()
            if missing:
                raise ValueError(f"line {line_number}: missing {sorted(missing)}")
            if row["sample_id"] in seen:
                raise ValueError(f"line {line_number}: duplicate sample_id {row['sample_id']}")
            seen.add(row["sample_id"])
            rows.append(row)
    slices: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        slices[row.get("field_type", "unspecified")].append(row)
    report = {
        "model": {"name": args.model_name, "version": args.model_version},
        "overall": aggregate(rows),
        "by_field_type": {name: aggregate(values) for name, values in sorted(slices.items())},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
