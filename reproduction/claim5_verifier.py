#!/usr/bin/env python3
"""Verify Claim 5 from frozen raw evidence and an independent checker."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAIM_DIR = ROOT / ".openresearch" / "artifacts" / "claim_5"
CHECKER = Path(__file__).with_name("claim5_checker.py")


def run_checker(negative_control: bool = False) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(CHECKER)]
    if negative_control:
        command.append("--negative-control")
    return subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-control", action="store_true")
    args = parser.parse_args()
    if args.negative_control:
        completed = run_checker(negative_control=True)
        print(completed.stdout.strip())
        print(completed.stderr.strip(), file=sys.stderr)
        return completed.returncode

    contract = json.loads((CLAIM_DIR / "claim_contract.json").read_text("utf-8"))
    if contract["verdict"] != "FALSIFIED":
        raise RuntimeError("Claim 5 contract must retain FALSIFIED")

    completed = run_checker()
    if completed.returncode != 0:
        raise RuntimeError(
            f"independent checker failed ({completed.returncode}): "
            f"{completed.stderr.strip()}"
        )
    observed = json.loads(completed.stdout)
    expected = json.loads((CLAIM_DIR / "checker_output.json").read_text("utf-8"))
    if observed != expected:
        raise RuntimeError("independent checker output changed")

    control = run_checker(negative_control=True)
    if control.returncode == 0:
        raise RuntimeError("mutated-evidence negative control unexpectedly passed")
    expected_control = json.loads(
        (CLAIM_DIR / "negative_control_output.json").read_text("utf-8")
    )
    if {
        "returncode": control.returncode,
        "output": json.loads(control.stdout),
    } != expected_control:
        raise RuntimeError("negative-control output changed")

    output = {
        **observed,
        "claim_contract": contract,
        "checker_negative_control": expected_control,
        "fixed_command": (
            "uv run --frozen --no-dev python scripts/run_reproduction.py"
        ),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
