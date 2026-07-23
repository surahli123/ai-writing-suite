#!/usr/bin/env python3
"""Run the provenance-gated known-human-negative false-positive evaluation."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

# Support both `python3 -m known_human.run_known_human` from evals/ and direct
# script execution while keeping the detector import identical in both modes.
EVALS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EVALS_DIR))
from detector.detector import analyze  # noqa: E402


HERE = Path(__file__).resolve().parent
DEFAULT_MANIFEST = HERE / "manifest.json"
THRESHOLD_SOURCE = EVALS_DIR / "fixtures" / "false_positives.json"
SUPPLEMENTAL_LABEL = "SUPPLEMENTAL PUBLIC SET — NOT A REAL-WRITER BENCHMARK"
EVIDENCE_ROLES = {"supplemental_public", "owner_gated_real_writer"}
REQUIRED_SAMPLE_FIELDS = (
    "author",
    "title",
    "publication_date",
    "source_url",
    "retrieval_date",
    "rights_basis",
    "attribution",
    "excerpt_boundary",
    "genre_proxy",
    "language",
    "sha256",
    "path",
)


def load_threshold():
    """Read the shipped detector flag threshold from its existing contract."""
    data = json.loads(THRESHOLD_SOURCE.read_text(encoding="utf-8"))
    threshold = data["flag_threshold"]
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise ValueError(
            f"{THRESHOLD_SOURCE}: flag_threshold must be a number"
        )
    return threshold


def wilson_interval(false_positives, eligible, z=1.96):
    """Return the two-sided Wilson score interval for a binomial proportion."""
    if eligible <= 0:
        raise ValueError("eligible must be greater than zero")
    if not 0 <= false_positives <= eligible:
        raise ValueError("false_positives must be between zero and eligible")

    proportion = false_positives / eligible
    z_squared = z * z
    denominator = 1 + z_squared / eligible
    center = (proportion + z_squared / (2 * eligible)) / denominator
    margin = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / eligible
            + z_squared / (4 * eligible * eligible)
        )
        / denominator
    )
    return max(0.0, center - margin), min(1.0, center + margin)


def _nonempty_text(value):
    return isinstance(value, str) and bool(value.strip())


def _record_shape_errors(record, declared_genres):
    errors = []
    if not isinstance(record, dict):
        return ["record must be a JSON object"]

    for field in REQUIRED_SAMPLE_FIELDS:
        if field not in record:
            errors.append(f"missing provenance field '{field}'")
            continue
        value = record[field]
        if field == "attribution":
            if value is not None and not _nonempty_text(value):
                errors.append(
                    "provenance field 'attribution' must be non-empty text or null"
                )
        elif not _nonempty_text(value):
            errors.append(f"provenance field '{field}' must be non-empty text")

    rights_basis = record.get("rights_basis")
    if _nonempty_text(rights_basis):
        rights_text = rights_basis.strip()
        if (
            rights_text.lower().startswith(("http://", "https://"))
            and len(rights_text.split()) == 1
        ):
            errors.append(
                "rights_basis must be item-level prose with a jurisdiction note, "
                "not a bare URL"
            )
        elif len(rights_text.split()) < 4:
            errors.append(
                "rights_basis must be item-level prose with a jurisdiction note"
            )

    genre = record.get("genre_proxy")
    if _nonempty_text(genre) and genre not in declared_genres:
        errors.append(
            f"genre_proxy is not one of the manifest's declared strata"
        )

    checksum = record.get("sha256")
    if _nonempty_text(checksum):
        normalized = checksum.strip().lower()
        if len(normalized) != 64 or any(
            character not in "0123456789abcdef" for character in normalized
        ):
            errors.append("sha256 must be exactly 64 hexadecimal characters")

    return errors


def _sample_path(manifest_path, relative_path):
    path = Path(relative_path)
    if path.is_absolute():
        raise ValueError("path must be relative under the manifest's samples/")

    samples_root = (manifest_path.parent / "samples").resolve()
    if path.parts and path.parts[0] == "samples":
        resolved = (manifest_path.parent / path).resolve()
    else:
        resolved = (samples_root / path).resolve()
    if resolved == samples_root or samples_root not in resolved.parents:
        raise ValueError("path must be relative under the manifest's samples/")
    return resolved


def validate_and_score(manifest, manifest_path):
    """Return eligible scored records and validation errors."""
    declared_genres = manifest["genre_proxies"]
    eligible = []
    errors = []

    for index, record in enumerate(manifest["samples"]):
        record_errors = _record_shape_errors(record, declared_genres)
        if record_errors:
            for error in record_errors:
                errors.append(f"INELIGIBLE sample[{index}]: {error}")
            continue

        try:
            sample_path = _sample_path(manifest_path, record["path"])
            sample_bytes = sample_path.read_bytes()
        except (OSError, ValueError) as exc:
            errors.append(f"INELIGIBLE sample[{index}]: sample file error: {exc}")
            continue

        actual_checksum = hashlib.sha256(sample_bytes).hexdigest()
        expected_checksum = record["sha256"].strip().lower()
        if actual_checksum != expected_checksum:
            errors.append(f"INELIGIBLE sample[{index}]: checksum mismatch")
            continue

        try:
            text = sample_bytes.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(
                f"INELIGIBLE sample[{index}]: sample is not valid UTF-8"
            )
            continue

        score = analyze(text).get("score")
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            errors.append(
                f"INELIGIBLE sample[{index}]: detector returned no numeric score"
            )
            continue

        eligible.append(
            {
                "sample_index": index,
                "genre_proxy": record["genre_proxy"],
                "score": score,
            }
        )

    return eligible, errors


def _manifest_errors(manifest):
    errors = []
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]

    evidence_role = manifest.get("evidence_role")
    if evidence_role not in EVIDENCE_ROLES:
        errors.append(
            "evidence_role must be 'supplemental_public' or "
            "'owner_gated_real_writer'"
        )

    genres = manifest.get("genre_proxies")
    if (
        not isinstance(genres, list)
        or not genres
        or any(not _nonempty_text(genre) for genre in genres)
    ):
        errors.append("genre_proxies must be a non-empty list of non-empty text")
    elif len(genres) != len(set(genres)):
        errors.append("genre_proxies must not contain duplicates")

    if not isinstance(manifest.get("samples"), list):
        errors.append("samples must be a JSON list")
    return errors


def _display_number(value):
    return f"{value:g}"


def print_cohort_report(label, cohort, threshold):
    false_positives = sum(1 for sample in cohort if sample["score"] >= threshold)
    eligible = len(cohort)
    print(f"\n[{label}]")
    print(f"false positives: {false_positives}")
    print(f"eligible samples: {eligible}")
    if not eligible:
        print("FP rate: 0/0 = n/a")
        print("score distribution (min/median/max): n/a")
        print("95% Wilson interval: n/a")
        return false_positives

    rate = false_positives / eligible
    scores = [sample["score"] for sample in cohort]
    low, high = wilson_interval(false_positives, eligible)
    print(f"FP rate: {false_positives}/{eligible} = {rate:.2%}")
    print(
        "score distribution (min/median/max): "
        f"{_display_number(min(scores))}/"
        f"{_display_number(statistics.median(scores))}/"
        f"{_display_number(max(scores))}"
    )
    print(f"95% Wilson interval: [{low:.4f}, {high:.4f}]")
    return false_positives


def _nonnegative_integer(value):
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Score provenance-validated known-human negatives at the shipped "
            "detector threshold."
        )
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help=(
            "manifest to evaluate; owner-gated manifests and samples remain "
            "local and uncommitted"
        ),
    )
    parser.add_argument(
        "--max-fp",
        type=_nonnegative_integer,
        help="fail if the overall false-positive count exceeds this ceiling",
    )
    return parser


def main(argv=None):
    print(SUPPLEMENTAL_LABEL, flush=True)
    args = build_parser().parse_args(argv)
    manifest_path = args.manifest.resolve()

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read manifest {manifest_path}: {exc}")
        return 1

    top_level_errors = _manifest_errors(manifest)
    if top_level_errors:
        for error in top_level_errors:
            print(f"ERROR: malformed manifest: {error}")
        return 1

    try:
        threshold = load_threshold()
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read detector threshold contract: {exc}")
        return 1

    print(f"evidence role: {manifest['evidence_role']}")
    print(
        "threshold: "
        f"{_display_number(threshold)} "
        "(source: fixtures/false_positives.json flag_threshold)"
    )

    eligible, errors = validate_and_score(manifest, manifest_path)
    for error in errors:
        print(f"ERROR: {error}")

    if eligible:
        print("\n[sample scores; text and direct identifiers withheld]")
        for sample in eligible:
            print(
                f"sample[{sample['sample_index']}] "
                f"genre_proxy={sample['genre_proxy']} "
                f"score={_display_number(sample['score'])}"
            )

    empty_cohorts = []
    for genre in manifest["genre_proxies"]:
        cohort = [
            sample for sample in eligible if sample["genre_proxy"] == genre
        ]
        if not cohort:
            message = (
                f"EMPTY REQUIRED COHORT: genre_proxy '{genre}' has 0 eligible "
                "samples"
            )
            empty_cohorts.append(message)
            print(f"ERROR: {message}")
        print_cohort_report(f"genre_proxy={genre}", cohort, threshold)

    overall_false_positives = print_cohort_report(
        f"overall evidence_role={manifest['evidence_role']}",
        eligible,
        threshold,
    )

    ceiling_exceeded = False
    if (
        args.max_fp is not None
        and overall_false_positives > args.max_fp
    ):
        ceiling_exceeded = True
        print(
            "ERROR: false-positive ceiling exceeded: "
            f"{overall_false_positives} > {args.max_fp}"
        )

    return 1 if errors or empty_cohorts or ceiling_exceeded else 0


if __name__ == "__main__":
    raise SystemExit(main())
