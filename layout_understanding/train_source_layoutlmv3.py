#!/usr/bin/env python3
"""Train LayoutLMv3 on one governed external source without label-space mixing."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from seqeval.metrics import f1_score, precision_score, recall_score
from torch.utils.data import Dataset
from transformers import LayoutLMv3ForTokenClassification, LayoutLMv3Processor, Trainer, TrainingArguments, default_data_collator


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalize_bbox(box, width, height, bbox_space):
    if bbox_space == "pixel":
        box = [round(box[0] * 1000 / width), round(box[1] * 1000 / height), round(box[2] * 1000 / width), round(box[3] * 1000 / height)]
    x0, y0, x1, y1 = (max(0, min(1000, int(value))) for value in box)
    return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]


class SourceDataset(Dataset):
    def __init__(self, rows, processor, label_to_id, bbox_space):
        self.rows, self.processor, self.label_to_id, self.bbox_space = rows, processor, label_to_id, bbox_space

    def __len__(self): return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        image = Image.open(Path(row["media_uri"].replace("file://", ""))).convert("RGB")
        words = [token["text"] for token in row["tokens"]]
        boxes = [normalize_bbox(token["bbox"], image.width, image.height, self.bbox_space) for token in row["tokens"]]
        if any(not (0 <= x0 <= x1 <= 1000 and 0 <= y0 <= y1 <= 1000) for x0, y0, x1, y1 in boxes):
            raise ValueError(f"invalid normalized bounding box in {row['sample_id']}")
        labels = [self.label_to_id[token["source_label"]] for token in row["tokens"]]
        encoded = self.processor(image, text=words, boxes=boxes, word_labels=labels, truncation=True, padding="max_length", max_length=512, return_tensors="pt")
        return {name: value.squeeze(0) for name, value in encoded.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["funsd", "cord_v2"], required=True)
    parser.add_argument("--manifest-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--epochs", type=float, default=3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    prefix = args.source
    train_rows = read_jsonl(args.manifest_dir / f"{prefix}_train.jsonl")
    test_rows = read_jsonl(args.manifest_dir / f"{prefix}_test.jsonl")
    validation_path = args.manifest_dir / f"{prefix}_validation.jsonl"
    if validation_path.exists():
        validation_rows = read_jsonl(validation_path)
    else:
        random.Random(args.seed).shuffle(train_rows)
        validation_rows, train_rows = train_rows[:max(1, round(len(train_rows) * 0.1))], train_rows[max(1, round(len(train_rows) * 0.1)):]
    labels = sorted({token["source_label"] for row in train_rows for token in row["tokens"]})
    label_to_id, id_to_label = {label: index for index, label in enumerate(labels)}, dict(enumerate(labels))
    bbox_space = "normalized_1000" if args.source == "funsd" else "pixel"
    processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
    model = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base", num_labels=len(labels), id2label=id_to_label, label2id=label_to_id, ignore_mismatched_sizes=True)
    def metrics(prediction):
        logits, expected = prediction
        actual = np.argmax(logits, axis=-1)
        true_sequences, predicted_sequences = [], []
        for truth, pred in zip(expected, actual):
            keep = truth != -100
            true_sequences.append([id_to_label[int(v)] for v in truth[keep]])
            predicted_sequences.append([id_to_label[int(v)] for v in pred[keep]])
        return {"entity_precision": precision_score(true_sequences, predicted_sequences), "entity_recall": recall_score(true_sequences, predicted_sequences), "entity_f1": f1_score(true_sequences, predicted_sequences)}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    metadata = {"source": args.source, "license_class": "research_only", "bbox_space": bbox_space, "splits": {"train": len(train_rows), "validation": len(validation_rows), "test": len(test_rows)}, "label_count": len(labels), "labels": labels}
    (args.output_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    training = TrainingArguments(output_dir=str(args.output_dir), learning_rate=1e-5, per_device_train_batch_size=1, per_device_eval_batch_size=1, gradient_accumulation_steps=8, num_train_epochs=args.epochs, fp16=torch.cuda.is_available(), eval_strategy="epoch", save_strategy="epoch", load_best_model_at_end=True, metric_for_best_model="eval_entity_f1", save_total_limit=2, logging_steps=10, report_to="none", seed=args.seed)
    trainer = Trainer(model=model, args=training, train_dataset=SourceDataset(train_rows, processor, label_to_id, bbox_space), eval_dataset=SourceDataset(validation_rows, processor, label_to_id, bbox_space), data_collator=default_data_collator, processing_class=processor, compute_metrics=metrics)
    trainer.train()
    result = trainer.evaluate(SourceDataset(test_rows, processor, label_to_id, bbox_space), metric_key_prefix="test")
    trainer.save_model(); processor.save_pretrained(args.output_dir)
    (args.output_dir / "test_metrics.json").write_text(json.dumps(result, indent=2, default=float) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, default=float))


if __name__ == "__main__": main()
