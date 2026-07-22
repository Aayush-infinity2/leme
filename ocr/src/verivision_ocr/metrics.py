"""Deterministic OCR metrics with explicit Unicode normalization."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence


def normalize(text: str) -> str:
    """Normalize OCR comparison text without making field-specific substitutions.

    Confusions such as O↔0 must be evaluated separately per field policy rather
    than silently corrected here; doing otherwise hides OCR failures.
    """
    return " ".join(unicodedata.normalize("NFKC", text).strip().split())


def levenshtein(reference: Sequence[str], prediction: Sequence[str]) -> int:
    if len(reference) < len(prediction):
        reference, prediction = prediction, reference
    previous = list(range(len(prediction) + 1))
    for i, source in enumerate(reference, start=1):
        current = [i]
        for j, target in enumerate(prediction, start=1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (source != target)))
        previous = current
    return previous[-1]


def character_error_rate(reference: str, prediction: str) -> float:
    reference, prediction = normalize(reference), normalize(prediction)
    if not reference:
        return 0.0 if not prediction else 1.0
    return levenshtein(list(reference), list(prediction)) / len(reference)


def word_error_rate(reference: str, prediction: str) -> float:
    reference_words, prediction_words = normalize(reference).split(), normalize(prediction).split()
    if not reference_words:
        return 0.0 if not prediction_words else 1.0
    return levenshtein(reference_words, prediction_words) / len(reference_words)


def field_normalize(text: str, field_type: str | None) -> str:
    """Apply declared, conservative evaluation normalization for selected fields."""
    value = normalize(text)
    if field_type in {"document_number", "date", "account_number"}:
        return re.sub(r"[\s-]", "", value).upper()
    return value
