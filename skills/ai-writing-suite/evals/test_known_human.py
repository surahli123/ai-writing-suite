"""Machinery tests for the known-human-negative false-positive evaluation."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from known_human.run_known_human import load_threshold, wilson_interval


EVALS_DIR = Path(__file__).resolve().parent
RUNNER_MODULE = "known_human.run_known_human"
THRESHOLD_SOURCE = EVALS_DIR / "fixtures" / "false_positives.json"
PUBLIC_MANIFEST = EVALS_DIR / "known_human" / "manifest.json"
SUPPLEMENTAL_LABEL = "SUPPLEMENTAL PUBLIC SET — NOT A REAL-WRITER BENCHMARK"


class KnownHumanMachinery(unittest.TestCase):
    def make_manifest(self, root, genre_proxies=("letter",), omit=None, sha256=None):
        sample_dir = root / "samples"
        sample_dir.mkdir()
        sample_path = sample_dir / "sample.txt"
        sample_bytes = b"A plain synthetic sentence written for a machinery test.\n"
        sample_path.write_bytes(sample_bytes)

        record = {
            "author": "Synthetic Test Author",
            "title": "Synthetic Machinery Sample",
            "publication_date": "1900",
            "source_url": "https://example.test/synthetic",
            "retrieval_date": "2026-07-22",
            "rights_basis": (
                "Public domain in the United States jurisdiction; synthetic "
                "test text created solely for this temporary fixture."
            ),
            "attribution": None,
            "excerpt_boundary": "Entire temporary sample, bytes 0-56.",
            "genre_proxy": genre_proxies[0],
            "language": "en",
            "sha256": sha256 or hashlib.sha256(sample_bytes).hexdigest(),
            "path": "samples/sample.txt",
        }
        if omit:
            record.pop(omit)

        manifest = {
            "evidence_role": "supplemental_public",
            "genre_proxies": list(genre_proxies),
            "samples": [record],
        }
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest_path

    def run_manifest(self, manifest_path, *extra_args):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                RUNNER_MODULE,
                "--manifest",
                str(manifest_path),
                *extra_args,
            ],
            cwd=EVALS_DIR,
            text=True,
            capture_output=True,
        )

    def test_fully_valid_synthetic_record_passes_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_manifest(self.make_manifest(Path(tmp)))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("false positives: 0", result.stdout)
        self.assertIn("eligible samples: 1", result.stdout)

    def test_missing_provenance_field_is_ineligible_and_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_manifest(
                self.make_manifest(Path(tmp), omit="author")
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("INELIGIBLE", result.stdout)
        self.assertIn("author", result.stdout)

    def test_sha256_drift_is_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_manifest(
                self.make_manifest(Path(tmp), sha256="0" * 64)
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checksum mismatch", result.stdout)

    def test_empty_required_cohort_is_loud_and_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_manifest(
                self.make_manifest(Path(tmp), genre_proxies=("letter", "essay"))
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "EMPTY REQUIRED COHORT: genre_proxy 'essay' has 0 eligible samples",
            result.stdout,
        )

    def test_supplemental_label_is_always_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_manifest(
                self.make_manifest(Path(tmp), omit="rights_basis")
            )
        self.assertIn(SUPPLEMENTAL_LABEL, result.stdout)

    def test_threshold_is_read_from_existing_contract_source(self):
        contract = json.loads(THRESHOLD_SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(load_threshold(), contract["flag_threshold"])

    def test_wilson_interval_zero_of_eight(self):
        low, high = wilson_interval(0, 8)
        self.assertEqual(round(low, 4), 0.0000)
        self.assertEqual(round(high, 4), 0.3244)

    def test_committed_manifest_is_empty_and_declares_public_strata(self):
        manifest = json.loads(PUBLIC_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["evidence_role"], "supplemental_public")
        self.assertEqual(
            manifest["genre_proxies"],
            ["letter", "essay", "technical", "report"],
        )
        self.assertEqual(manifest["samples"], [])


if __name__ == "__main__":
    unittest.main()
