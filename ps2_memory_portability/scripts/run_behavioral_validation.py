"""Generate non-participant scenario and validation artifacts for Phase 4B."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys

import gradio


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPACE_DIR = PROJECT_ROOT / "behavioral_space"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
sys.path.insert(0, str(SPACE_DIR))

from core import scenario_rows, validate_scenario_catalog  # noqa: E402


CATALOG_FIELDS = [
    "scenario_id",
    "portability_condition",
    "condition_description_short",
    "normalized_benefit",
    "normalized_hurdle",
    "benchmark_net_advantage",
    "benchmark_prediction",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke-status",
        choices=("passed", "failed", "not_run"),
        required=True,
    )
    parser.add_argument(
        "--deployment-status",
        choices=("not_attempted", "not_authenticated", "failed", "deployed_verified"),
        required=True,
    )
    parser.add_argument("--space-url")
    parser.add_argument("--deployed-revision")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.deployment_status == "deployed_verified" and not args.space_url:
        raise ValueError("A verified deployment requires --space-url.")
    if args.deployment_status != "deployed_verified" and args.space_url:
        raise ValueError("Do not record a Space URL before verified deployment.")

    validation = validate_scenario_catalog()
    rows = scenario_rows()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    catalog_path = OUTPUT_DIR / "behavioral_scenario_catalog.csv"
    with catalog_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=CATALOG_FIELDS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        "artifact_title": "Stay or Switch?",
        **validation,
        "benchmark_rule": "Switch iff g > r; Stay iff g < r; no equality cases",
        "privacy_storage_policy": (
            "Thread-safe process-memory aggregate only; no persistent participant-data backend"
        ),
        "free_text_policy": (
            "Optional, maximum 300 characters, session-only, never aggregated or persisted"
        ),
        "peer_aggregation_policy": (
            "Same-condition and overall summaries use prior anonymous plays only; "
            "current play is added after the snapshot; raw rows are never displayed"
        ),
        "python_version": platform.python_version(),
        "gradio_version": gradio.__version__,
        "validation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "local_smoke_test_status": args.smoke_status,
        "deployment_status": args.deployment_status,
        "hugging_face_space_url": args.space_url,
        "deployed_revision": args.deployed_revision,
        "contains_participant_data": False,
    }
    validation_path = OUTPUT_DIR / "behavioral_validation.json"
    validation_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"Wrote {catalog_path}")
    print(f"Wrote {validation_path}")
    print(json.dumps(validation, sort_keys=True))


if __name__ == "__main__":
    main()
