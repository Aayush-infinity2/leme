from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "layout_understanding" / "src"))
from verivision_layout.geometry import layoutlm_bbox


class LayoutUnderstandingTest(unittest.TestCase):
    def test_bbox_projection_preserves_bounds(self) -> None:
        self.assertEqual(layoutlm_bbox([0, 0, 200, 0, 200, 100, 0, 100], 200, 100), [0, 0, 1000, 1000])

    def test_evaluator_writes_entity_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.json"
            result = subprocess.run([sys.executable, "-m", "verivision_layout.evaluate", str(ROOT / "tests" / "fixtures" / "layout" / "predictions.jsonl"), "--model-name", "layout-test", "--model-version", "digest", "--output", str(output)], cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "layout_understanding" / "src")}, check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["entity_micro"]["f1"], 1.0)
            self.assertEqual(report["document_class_accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
