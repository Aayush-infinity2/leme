from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ocr" / "src"))

from verivision_ocr.metrics import character_error_rate, field_normalize, word_error_rate


class OcrMetricsTest(unittest.TestCase):
    def test_perfect_unicode_normalized_match(self) -> None:
        self.assertEqual(character_error_rate("café", "cafe\u0301"), 0.0)
        self.assertEqual(word_error_rate("first second", "first second"), 0.0)

    def test_literal_metric_does_not_hide_character_confusion(self) -> None:
        self.assertGreater(character_error_rate("ABO1", "AB01"), 0.0)

    def test_declared_field_normalization_is_separate(self) -> None:
        self.assertEqual(field_normalize("ab- 01", "document_number"), "AB01")


if __name__ == "__main__":
    unittest.main()
