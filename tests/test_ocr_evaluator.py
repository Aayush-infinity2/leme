from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class OcrEvaluatorTest(unittest.TestCase):
    def test_evaluator_generates_slice_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.json"
            environment = {**os.environ, "PYTHONPATH": str(ROOT / "ocr" / "src")}
            result = subprocess.run(
                [
                    sys.executable, "-m", "verivision_ocr.evaluate",
                    str(ROOT / "tests" / "fixtures" / "ocr" / "predictions.jsonl"),
                    "--model-name", "test-engine", "--model-version", "test-digest",
                    "--output", str(output),
                ],
                cwd=ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["overall"]["samples"], 2)
            self.assertEqual(report["overall"]["cer"], 0.0)
            self.assertIn("document_number", report["by_field_type"])


if __name__ == "__main__":
    unittest.main()
