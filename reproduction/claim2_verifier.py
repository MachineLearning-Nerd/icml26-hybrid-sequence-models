#!/usr/bin/env python3
"""Verify the exact sliding-window lower-bound contract for Claim 2."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAIM_DIR = ROOT / ".openresearch" / "artifacts" / "claim_2"
CHECKER = Path(__file__).with_name("claim2_checker.py")


def run_checker(
    length: int, dependency_range: int, windows: list[int], control: bool = False
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(CHECKER),
        "--length",
        str(length),
        "--range",
        str(dependency_range),
        "--windows",
        ",".join(map(str, windows)),
    ]
    if control:
        command.append("--over-budget-control")
    return subprocess.run(command, check=False, text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-control", action="store_true")
    args = parser.parse_args()
    if args.negative_control:
        control = run_checker(17, 8, [2, 2, 3], control=True)
        print(control.stdout.strip())
        print(control.stderr.strip(), file=sys.stderr)
        return control.returncode

    contract = json.loads((CLAIM_DIR / "claim_contract.json").read_text(encoding="utf-8"))
    if contract["verdict"] != "VERIFIED":
        raise RuntimeError("Claim 2 contract must retain the VERIFIED verdict")

    checked_rows: list[dict] = []
    with (CLAIM_DIR / "raw" / "witness_grid.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        for row in csv.DictReader(handle):
            windows = [int(value) for value in row["windows"].split("+")]
            result = run_checker(
                int(row["length"]), int(row["dependency_range"]), windows
            )
            if result.returncode != 0:
                raise RuntimeError(f"checker failed on row {row}")
            checked = json.loads(result.stdout)
            if checked["total_window"] != int(row["total_window"]):
                raise RuntimeError("total-window arithmetic changed")
            if not (
                checked["shared_r_suffix"]
                and checked["observations_equal"]
                and checked["target_labels_differ"]
            ):
                raise RuntimeError("local-sensitivity witness certificate failed")
            if checked["max_accuracy_on_uniform_pair"] != 0.5:
                raise RuntimeError("uniform witness-pair accuracy was not exactly 1/2")
            if not checked["max_accuracy_on_uniform_pair"] < checked["target_threshold"]:
                raise RuntimeError("1/2 no longer contradicts the 2/3 target")
            checked_rows.append(checked)

    # General symbolic route. If W=sum_i W_i < R, equality of the last R
    # coordinates implies equality of the last W coordinates. Every
    # deterministic function of that common observation gives the same output
    # on the two witnesses. Under their uniform mixture, one of the two
    # differing labels is wrong, so accuracy <= 1/2 < 2/3.
    symbolic_certificate = {
        "premises": [
            "W = sum_i W_i",
            "W < R",
            "x[-R:] = x_prime[-R:]",
            "F(x) != F(x_prime)",
            "M(x) is a function only of x[-W:]",
        ],
        "derived": [
            "x[-W:] = x_prime[-W:]",
            "M(x) = M(x_prime)",
            "accuracy under Uniform({x,x_prime}) <= 1/2",
            "1/2 < 2/3",
            "therefore any model reaching 2/3 has sum_i W_i >= R",
        ],
    }

    representative = run_checker(17, 8, [2, 2, 3])
    expected_checker = json.loads(
        (CLAIM_DIR / "checker_output.json").read_text(encoding="utf-8")
    )
    if representative.returncode != expected_checker.pop("returncode"):
        raise RuntimeError("representative checker return code changed")
    if json.loads(representative.stdout) != expected_checker:
        raise RuntimeError("representative checker output changed")

    control = run_checker(17, 8, [2, 2, 3], control=True)
    expected_control = json.loads(
        (CLAIM_DIR / "negative_control_output.json").read_text(encoding="utf-8")
    )
    expected_control.pop("control")
    if control.returncode != expected_control.pop("returncode"):
        raise RuntimeError("over-budget control return code changed")
    if json.loads(control.stdout) != expected_control:
        raise RuntimeError("over-budget control output changed")
    if control.returncode == 0:
        raise RuntimeError("over-budget control unexpectedly certified the lower-bound premise")

    output = {
        "claim": 2,
        "verdict": "VERIFIED",
        "scope": "Theorem 3.7 under the final-suffix dependency premise stated in its proof.",
        "symbolic_certificate": symbolic_certificate,
        "independent_checker": {
            "result": "PASS",
            "cases": len(checked_rows),
            "rows": checked_rows,
        },
        "negative_control": {
            "returncode": control.returncode,
            "total_window": json.loads(control.stdout)["total_window"],
            "observations_equal": json.loads(control.stdout)["observations_equal"],
            "expected": "nonzero because W >= R and the proof premise is unavailable",
        },
        "definition_caveat": (
            "The paper does not formally define sliding-window masking in its "
            "preliminaries; verification conditions on the exact dependency "
            "premise used at Appendix proof lines 93-94."
        ),
        "confidence": "MEDIUM",
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
