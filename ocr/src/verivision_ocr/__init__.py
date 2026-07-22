"""Auditable OCR evaluation utilities."""

from .metrics import character_error_rate, word_error_rate

__all__ = ["character_error_rate", "word_error_rate"]
