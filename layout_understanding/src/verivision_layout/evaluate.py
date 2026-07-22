"""Entity and document-classification evaluator for JSONL predictions."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def entity_key(entity: dict[str, Any]) -> tuple[str, str]:
    if not isinstance(entity.get("label"), str) or not isinstance(entity.get("normalized_value"), str):
        raise ValueError("entities require string label and normalized_value")
    return entity["label"], entity["normalized_value"]


def f1(tp: int, fp: int, fn: int) -> dict[str, float | int]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"precision": precision, "recall": recall, "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0, "tp": tp, "fp": fp, "fn": fn}


def evaluate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = Counter()
    per_label: dict[str, Counter[str]] = defaultdict(Counter)
    correct_classification = 0
    for row in rows:
        expected = Counter(entity_key(item) for item in row["reference_entities"])
        predicted = Counter(entity_key(item) for item in row["predicted_entities"])
        for key in expected.keys() | predicted.keys():
            matched = min(expected[key], predicted[key])
            label = key[0]
            total.update(tp=matched, fp=predicted[key] - matched, fn=expected[key] - matched)
            per_label[label].update(tp=matched, fp=predicted[key] - matched, fn=expected[key] - matched)
        if row.get("reference_document_class") is not None:
            if row.get("reference_document_class") == row.get("predicted_document_class"):
                correct_classification += 1
    report = {"entity_micro": f1(total["tp"], total["fp"], total["fn"]), "by_entity_label": {label: f1(values["tp"], values["fp"], values["fn"]) for label, values in sorted(per_label.items())}}
    classified = [row for row in rows if row.get("reference_document_class") is not None]
    if classified:
        report["document_class_accuracy"] = correct_classification / len(classified)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--model-version", required=True)
    args = parser.parse_args()
    rows = []
    seen: set[str] = set()
    for line_number, line in enumerate(args.predictions.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        missing = {"sample_id", "reference_entities", "predicted_entities"} - row.keys()
        if missing:
            raise ValueError(f"line {line_number}: missing {sorted(missing)}")
        if row["sample_id"] in seen:
            raise ValueError(f"line {line_number}: duplicate sample_id")
        seen.add(row["sample_id"])
        rows.append(row)
    report = {"model": {"name": args.model_name, "version": args.model_version}, "samples": len(rows), **evaluate(rows)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
