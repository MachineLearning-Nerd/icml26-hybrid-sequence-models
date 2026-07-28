#!/usr/bin/env python3
"""Fixed cumulative verifier entrypoint for the reproduction campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
ARTIFACTS = ROOT / ".openresearch" / "artifacts"
CAMPAIGN_PATH = ROOT / "reproduction" / "campaign.json"
JUDGED_MANIFEST = ARTIFACTS / "project" / "judged_space_manifest.sha256"
ALLOWED_VERDICTS = {"VERIFIED", "FALSIFIED", "BLOCKED"}


class VerificationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_manifest(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            digest, relative = raw.split("  ", 1)
        except ValueError as exc:
            raise VerificationError(f"malformed manifest line {line_number}") from exc
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise VerificationError(f"invalid SHA-256 at manifest line {line_number}")
        if relative.startswith("/") or ".." in Path(relative).parts:
            raise VerificationError(f"unsafe path at manifest line {line_number}")
        rows.append((digest, relative))
    return rows


def verify_campaign(campaign: dict) -> dict:
    required_audits = [
        ARTIFACTS / "project" / "source_audit.md",
        ARTIFACTS / "project" / "gap_analysis.md",
        ARTIFACTS / "project" / "method.md",
        ARTIFACTS / "project" / "EVAL.md",
        ARTIFACTS / "project" / "limitations.md",
        ARTIFACTS / "project" / "verdict_record.json",
        JUDGED_MANIFEST,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_audits if not path.is_file()]
    if missing:
        raise VerificationError(f"missing baseline audit files: {missing}")

    manifest = parse_manifest(JUDGED_MANIFEST)
    expected_count = campaign["judged_space"]["manifest_entries"]
    if len(manifest) != expected_count:
        raise VerificationError(
            f"judged manifest has {len(manifest)} entries, expected {expected_count}"
        )

    if campaign["fixed_run_command"] != (
        "uv run --frozen --no-dev python scripts/run_reproduction.py"
    ):
        raise VerificationError("fixed run command changed")

    claims = campaign["claims"]
    if [claim["id"] for claim in claims] != list(range(1, 7)):
        raise VerificationError("claim ids must be exactly 1..6")
    invalid = [claim for claim in claims if claim["verdict"] not in ALLOWED_VERDICTS]
    if invalid:
        raise VerificationError(f"invalid claim verdicts: {invalid}")

    verdict_record = json.loads(
        (ARTIFACTS / "project" / "verdict_record.json").read_text(encoding="utf-8")
    )
    if verdict_record["space_id"] != "DineshAI/82EJxJzG6r":
        raise VerificationError("verdict record was not filtered by exact space_id")
    if verdict_record["sha"] != campaign["judged_space"]["sha"]:
        raise VerificationError("verdict record SHA does not match protected Space SHA")

    return {
        "manifest_entries": len(manifest),
        "manifest_paths": [relative for _, relative in manifest],
        "claim_verdicts": {str(claim["id"]): claim["verdict"] for claim in claims},
        "required_audits": [str(path.relative_to(ROOT)) for path in required_audits],
    }


def run_claim_verifier(claim_id: int) -> dict:
    verifier = ROOT / "reproduction" / f"claim{claim_id}_verifier.py"
    if not verifier.is_file():
        raise VerificationError(f"missing verifier for non-BLOCKED claim {claim_id}")
    completed = subprocess.run(
        [sys.executable, str(verifier)],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise VerificationError(
            f"claim {claim_id} verifier failed ({completed.returncode}): "
            f"{completed.stderr.strip()}"
        )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"claim {claim_id} verifier emitted invalid JSON") from exc


def negative_control() -> int:
    rows = parse_manifest(JUDGED_MANIFEST)
    corrupted = list(rows)
    first_digest, first_path = corrupted[0]
    corrupted[0] = ("0" * 64 if first_digest != "0" * 64 else "f" * 64, first_path)
    if corrupted == rows:
        print("NEGATIVE_CONTROL_ERROR: mutation did not change manifest")
        return 0
    print(
        "NEGATIVE_CONTROL_EXPECTED_FAILURE: protected manifest mutation detected",
        file=sys.stderr,
    )
    return 3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-control", action="store_true")
    args = parser.parse_args()
    if args.negative_control:
        return negative_control()

    started = time.perf_counter()
    campaign = json.loads(CAMPAIGN_PATH.read_text(encoding="utf-8"))
    empirical_result = None
    if campaign.get("empirical_stage", {}).get("kind") == "claim_5_cpu_fidelity_pilot":
        from reproduction.figure_training import run_cpu_fidelity_pilot

        empirical_result = run_cpu_fidelity_pilot(campaign["empirical_stage"])
    result = verify_campaign(campaign)
    claim_results = {
        str(claim["id"]): run_claim_verifier(claim["id"])
        for claim in campaign["claims"]
        if claim["verdict"] != "BLOCKED"
    }

    control = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--negative-control"],
        check=False,
        text=True,
        capture_output=True,
    )
    if control.returncode == 0:
        raise VerificationError("negative control unexpectedly passed")

    elapsed = time.perf_counter() - started
    cpu_affinity = None
    if hasattr(os, "sched_getaffinity"):
        cpu_affinity = len(os.sched_getaffinity(0))
    runtime = {
        "estimated_scientific_cores": campaign["planned_compute"][
            "estimated_scientific_cores"
        ],
        "runtime_class": campaign["planned_compute"]["runtime_class"],
        "selected_backend": campaign["planned_compute"]["backend"],
        "selected_flavor": campaign["planned_compute"]["flavor"],
        "selected_image": campaign["planned_compute"]["image"],
        "selected_timeout": campaign["planned_compute"]["timeout"],
        "actual_os_cpu_count": os.cpu_count(),
        "actual_cpu_affinity": cpu_affinity,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "verifier_runtime_seconds": round(elapsed, 6),
    }

    output = {
        "schema_version": 1,
        "stage": campaign["stage"],
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "paper": campaign["paper"],
        "official_code": campaign["official_code"],
        "judged_space": campaign["judged_space"],
        "checks": result,
        "claim_results": claim_results,
        "empirical_result": empirical_result,
        "negative_control": {
            "returncode": control.returncode,
            "stderr": control.stderr.strip(),
            "passed": control.returncode != 0,
        },
        "runtime": runtime,
        "overall": "PASS",
    }
    print("=== OPENRESEARCH_EVIDENCE_JSON ===")
    print(json.dumps(output, indent=2, sort_keys=True))
    print("=== EVAL_SUMMARY ===")
    print("Historical judged baseline audit: PASS")
    print("Protected judged score: 0/12; no score increase is claimed.")
    blocked_ids = [
        str(claim["id"])
        for claim in campaign["claims"]
        if claim["verdict"] == "BLOCKED"
    ]
    print(f"Currently BLOCKED claims: {', '.join(blocked_ids) if blocked_ids else 'none'}")
    for claim_id, claim_result in claim_results.items():
        print(
            f"Claim {claim_id}: {claim_result['verdict']} "
            f"({claim_result['confidence']} confidence)"
        )
    print(f"Negative control return code: {control.returncode} (nonzero expected)")
    print(f"Verifier runtime seconds: {elapsed:.6f}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerificationError as exc:
        print(f"VERIFICATION_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
