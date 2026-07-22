#!/usr/bin/env python3
"""Validate safety-critical structural invariants in a JSONL dataset manifest.

This standard-library tool complements, rather than replaces, full JSON Schema
validation in CI. It intentionally rejects production manifests that contain
unknown consent or pending license status.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REQUIRED = {
    "sample_id", "source_id", "source_sample_id", "media_uri", "sha256",
    "split", "license_class", "consent_class", "annotation_version",
}
SPLITS = {"train", "validation", "test_locked", "challenge_locked", "holdout_domain"}
LICENSES = {"production_approved", "research_only", "benchmark_only", "first_party", "pending"}
CONSENTS = {"no_personal_data", "mock_or_synthetic", "consented", "restricted_research", "unknown"}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{2,127}$")
SHA256_PATTERN = re.compile(r"^[A-Fa-f0-9]{64}$")
URI_PATTERN = re.compile(r"^(s3|file|gs)://")


def validate(record: object, production: bool) -> list[str]:
    if not isinstance(record, dict):
        return ["record is not an object"]
    errors = [f"missing {name}" for name in sorted(REQUIRED - record.keys())]
    if errors:
        return errors
    if not isinstance(record["sample_id"], str) or not ID_PATTERN.fullmatch(record["sample_id"]):
        errors.append("invalid sample_id")
    if not isinstance(record["source_id"], str) or not ID_PATTERN.fullmatch(record["source_id"]):
        errors.append("invalid source_id")
    if not isinstance(record["sha256"], str) or not SHA256_PATTERN.fullmatch(record["sha256"]):
        errors.append("invalid sha256")
    if not isinstance(record["media_uri"], str) or not URI_PATTERN.match(record["media_uri"]):
        errors.append("media_uri must be a file://, s3://, or gs:// URI")
    if record["split"] not in SPLITS:
        errors.append("invalid split")
    if record["license_class"] not in LICENSES:
        errors.append("invalid license_class")
    if record["consent_class"] not in CONSENTS:
        errors.append("invalid consent_class")
    if production and record["license_class"] not in {"production_approved", "first_party"}:
        errors.append("production manifest includes non-production license_class")
    if production and record["consent_class"] in {"unknown", "restricted_research"}:
        errors.append("production manifest includes prohibited consent_class")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--production", action="store_true", help="enforce production-use restrictions")
    args = parser.parse_args()
    seen: set[str] = set()
    errors: list[str] = []
    digest = hashlib.sha256()
    with args.manifest.open("rb") as handle:
        for number, raw in enumerate(handle, start=1):
            digest.update(raw)
            if not raw.strip():
                continue
            try:
                record = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"line {number}: invalid JSON ({exc.msg})")
                continue
            for error in validate(record, args.production):
                errors.append(f"line {number}: {error}")
            if isinstance(record, dict) and isinstance(record.get("sample_id"), str):
                if record["sample_id"] in seen:
                    errors.append(f"line {number}: duplicate sample_id {record['sample_id']}")
                seen.add(record["sample_id"])
    if errors:
        print("MANIFEST INVALID", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"MANIFEST VALID records={len(seen)} sha256={digest.hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
