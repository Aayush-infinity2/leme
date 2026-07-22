from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_dataset_manifest.py"
FIXTURES = ROOT / "tests" / "fixtures" / "datasets"


class DatasetManifestValidatorTest(unittest.TestCase):
    def run_validator(self, fixture: str, *flags: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(FIXTURES / fixture), *flags],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_first_party_synthetic_record_is_allowed_for_production(self) -> None:
        result = self.run_validator("valid_production.jsonl", "--production")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MANIFEST VALID records=1", result.stdout)

    def test_research_only_biometric_record_is_blocked_from_production(self) -> None:
        result = self.run_validator("research_only.jsonl", "--production")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("non-production license_class", result.stderr)
        self.assertIn("prohibited consent_class", result.stderr)


if __name__ == "__main__":
    unittest.main()
