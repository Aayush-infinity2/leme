#!/usr/bin/env python3
"""Fine-tune LayoutLMv3 from a first-party manifest with OCR/token geometry.

Designed for the Colab T4 validation run. The synthetic one-template dataset
validates the pipeline only; it cannot establish real-world generalization.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset
from transformers import LayoutLMv3ForTokenClassification, LayoutLMv3Processor, Trainer, TrainingArguments, default_data_collator
from seqeval.metrics import f1_score, precision_score, recall_score

LABELS = ["O", "B-PERSON_NAME", "I-PERSON_NAME", "E-PERSON_NAME", "S-PERSON_NAME", "B-DOCUMENT_NUMBER", "I-DOCUMENT_NUMBER", "E-DOCUMENT_NUMBER", "S-DOCUMENT_NUMBER", "B-DATE_OF_BIRTH", "I-DATE_OF_BIRTH", "E-DATE_OF_BIRTH", "S-DATE_OF_BIRTH"]
LABEL_TO_ID = {label: index for index, label in enumerate(LABELS)}


def to_bbox(quad: list[int], width: int, height: int) -> list[int]:
    xs, ys = quad[0::2], quad[1::2]
    return [round(min(xs) * 1000 / width), round(min(ys) * 1000 / height), round(max(xs) * 1000 / width), round(max(ys) * 1000 / height)]


class ManifestDataset(Dataset):
    def __init__(self, rows, processor, box_jitter: int = 0, seed: int = 42):
        self.rows, self.processor, self.box_jitter, self.seed = rows, processor, box_jitter, seed

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        image = Image.open(row["image_path"]).convert("RGB")
        words = [token["text"] for token in row["tokens"]]
        boxes = [to_bbox(token["quad"], image.width, image.height) for token in row["tokens"]]
        if self.box_jitter:
            rng = random.Random(f"{self.seed}:{row['sample_id']}")
            boxes = [[max(0, min(1000, value + rng.randint(-self.box_jitter, self.box_jitter))) for value in box] for box in boxes]
        labels = [LABEL_TO_ID[token["label"]] for token in row["tokens"]]
        encoded = self.processor(image, text=words, boxes=boxes, word_labels=labels, truncation=True, padding="max_length", max_length=512, return_tensors="pt")
        return {name: value.squeeze(0) for name, value in encoded.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--epochs", type=float, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-box-jitter", type=int, default=0)
    parser.add_argument("--eval-box-jitter", type=int, default=0)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) < 20:
        raise ValueError("at least 20 samples are required for deterministic train/validation/test splits")
    families = sorted({row.get("template_family", "unknown") for row in rows})
    if len(families) < 3:
        raise ValueError("at least three template families are required for template-disjoint evaluation")
    train_families, validation_family, test_family = families[:-2], families[-2], families[-1]
    train_rows = [row for row in rows if row.get("template_family") in train_families]
    validation_rows = [row for row in rows if row.get("template_family") == validation_family]
    test_rows = [row for row in rows if row.get("template_family") == test_family]
    processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
    model = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base", num_labels=len(LABELS), id2label=dict(enumerate(LABELS)), label2id=LABEL_TO_ID, ignore_mismatched_sizes=True)
    run_metadata = {"manifest": str(args.manifest), "samples": len(rows), "splits": {"train": len(train_rows), "validation": len(validation_rows), "test": len(test_rows)}, "template_split": {"train": train_families, "validation": validation_family, "test": test_family}, "box_jitter": {"train": args.train_box_jitter, "evaluation": args.eval_box_jitter}, "seed": args.seed, "labels": LABELS, "scope_warning": "Synthetic multi-template transfer experiment only; not a real-document benchmark."}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "run_metadata.json").write_text(json.dumps(run_metadata, indent=2) + "\n", encoding="utf-8")
    # LayoutLMv3ForTokenClassification does not implement gradient checkpointing
    # in the installed Transformers runtime. Batch size 1 plus accumulation keeps
    # the T4 run memory-safe without enabling an unsupported model feature.
    training_args = TrainingArguments(output_dir=str(args.output_dir), learning_rate=1e-5, per_device_train_batch_size=1, per_device_eval_batch_size=1, gradient_accumulation_steps=8, num_train_epochs=args.epochs, fp16=torch.cuda.is_available(), eval_strategy="epoch", save_strategy="epoch", load_best_model_at_end=True, metric_for_best_model="eval_loss", greater_is_better=False, save_total_limit=2, logging_steps=10, report_to="none", seed=args.seed)
    def compute_metrics(prediction):
        logits, labels = prediction
        predicted = np.argmax(logits, axis=-1)
        true_sequences, predicted_sequences = [], []
        for expected, actual in zip(labels, predicted):
            keep = expected != -100
            true_sequences.append([LABELS[index] for index in expected[keep]])
            predicted_sequences.append([LABELS[index] for index in actual[keep]])
        return {"entity_precision": precision_score(true_sequences, predicted_sequences), "entity_recall": recall_score(true_sequences, predicted_sequences), "entity_f1": f1_score(true_sequences, predicted_sequences)}
    trainer = Trainer(model=model, args=training_args, train_dataset=ManifestDataset(train_rows, processor, args.train_box_jitter, args.seed), eval_dataset=ManifestDataset(validation_rows, processor, args.eval_box_jitter, args.seed), data_collator=default_data_collator, processing_class=processor, compute_metrics=compute_metrics)
    trainer.train()
    metrics = trainer.evaluate(ManifestDataset(test_rows, processor, args.eval_box_jitter, args.seed), metric_key_prefix="test")
    trainer.save_model()
    processor.save_pretrained(args.output_dir)
    (args.output_dir / "test_metrics.json").write_text(json.dumps(metrics, indent=2, default=float) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2, default=float))


if __name__ == "__main__":
    main()
