#!/usr/bin/env python3
"""Generate fictitious, visibly non-valid identity-style documents for research.

Outputs PNGs and JSONL with word geometry and BIOES entity labels. The generator
never reproduces a government credential, logo, number format, or real person.
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

NAMES = [("ALEX", "RIVERA"), ("MORGAN", "LEE"), ("TAYLOR", "PARK"), ("JORDAN", "SINGH")]


def font_path() -> str:
    return subprocess.check_output(["fc-match", "-f", "%{file}", "sans-serif"], text=True).strip()


def add_field(draw, font, label_font, x, y, label, value, entity, tokens):
    draw.text((x, y), label, font=label_font, fill="#4a5568")
    value_y = y + 35
    draw.text((x, value_y), value, font=font, fill="#111827")
    cursor = x
    words = value.split()
    for index, word in enumerate(words):
        left, top, right, bottom = draw.textbbox((cursor, value_y), word, font=font)
        prefix = "S" if len(words) == 1 else ("B" if index == 0 else "E" if index == len(words) - 1 else "I")
        tokens.append({"text": word, "quad": [left, top, right, top, right, bottom, left, bottom], "label": f"{prefix}-{entity}"})
        cursor = right + draw.textlength(" ", font=font)


TEMPLATES = [
    {"name": "blue_left", "accent": "#1d4ed8", "positions": [(80, 210), (80, 330), (80, 450)]},
    {"name": "green_compact", "accent": "#047857", "positions": [(80, 195), (80, 305), (80, 415)]},
    {"name": "violet_right", "accent": "#6d28d9", "positions": [(480, 210), (480, 330), (480, 450)]},
    {"name": "amber_spread", "accent": "#b45309", "positions": [(80, 205), (80, 365), (480, 365)]},
    {"name": "slate_bottom", "accent": "#334155", "positions": [(80, 205), (470, 205), (80, 435)]},
]
CAPTURES = [("clean", 1.0), ("low_contrast", 0.72), ("high_contrast", 1.25)]


def render(index: int, output: Path, font_file: str, rng: random.Random) -> dict:
    name = " ".join(rng.choice(NAMES))
    document_number = f"VV-{rng.randrange(1000, 9999)}-{rng.randrange(1000, 9999)}"
    template = TEMPLATES[index % len(TEMPLATES)]
    capture_name, contrast = CAPTURES[(index // len(TEMPLATES)) % len(CAPTURES)]
    image = Image.new("RGB", (1024, 640), "#f8fafc")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype(font_file, 42)
    font = ImageFont.truetype(font_file, 29)
    label_font = ImageFont.truetype(font_file, 20)
    draw.rounded_rectangle((40, 40, 984, 600), radius=28, fill="white", outline=template["accent"], width=4)
    draw.text((80, 75), "VERIVISION RESEARCH CREDENTIAL", font=title_font, fill=template["accent"])
    draw.text((80, 135), "SAMPLE / NOT VALID FOR IDENTIFICATION", font=label_font, fill="#b91c1c")
    draw.ellipse((730, 180, 900, 350), fill="#dbeafe", outline="#60a5fa", width=4)
    draw.ellipse((790, 215, 840, 265), fill="#93c5fd")
    draw.rounded_rectangle((760, 275, 870, 335), radius=20, fill="#93c5fd")
    tokens = []
    fields = [("FULL NAME", name, "PERSON_NAME"), ("RESEARCH DOCUMENT NUMBER", document_number, "DOCUMENT_NUMBER"), ("DATE OF BIRTH", "1994-06-15", "DATE_OF_BIRTH")]
    for (label, value, entity), (x, y) in zip(fields, template["positions"]):
        add_field(draw, font, label_font, x, y, label, value, entity, tokens)
    if contrast != 1.0:
        from PIL import ImageEnhance
        image = ImageEnhance.Contrast(image).enhance(contrast)
    path = output / f"synthetic_id_{index:05d}.png"
    image.save(path)
    return {"sample_id": f"synthetic-id-{index:05d}", "image_path": str(path), "document_class": "verivision_research_credential", "template_family": template["name"], "capture_condition": capture_name, "tokens": tokens, "license_class": "first_party", "consent_class": "no_personal_data"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.count <= 0:
        raise ValueError("count must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = args.output_dir / "manifest.jsonl"
    rng = random.Random(args.seed)
    font_file = font_path()
    with manifest.open("w", encoding="utf-8") as handle:
        for index in range(args.count):
            handle.write(json.dumps(render(index, args.output_dir, font_file, rng)) + "\n")
    print(f"generated={args.count} manifest={manifest}")


if __name__ == "__main__":
    main()
