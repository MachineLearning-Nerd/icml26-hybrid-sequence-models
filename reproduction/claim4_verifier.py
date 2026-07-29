#!/usr/bin/env python3
"""Verify the three-layer associative-recall construction and 99% window."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAIM_DIR = ROOT / ".openresearch" / "artifacts" / "claim_4"
CHECKER = Path(__file__).with_name("claim4_checker.py")


def run_checker(words: int, control: bool = False) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(CHECKER),
        "--word-vocabulary",
        str(words),
    ]
    if control:
        command.append("--below-threshold-control")
    return subprocess.run(command, check=False, text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-control", action="store_true")
    args = parser.parse_args()
    if args.negative_control:
        control = run_checker(2, control=True)
        print(control.stdout.strip())
        print(control.stderr.strip(), file=sys.stderr)
        return control.returncode

    contract = json.loads((CLAIM_DIR / "claim_contract.json").read_text(encoding="utf-8"))
    if contract["verdict"] != "VERIFIED":
        raise RuntimeError("Claim 4 contract must retain the VERIFIED verdict")

    rows: list[dict] = []
    with (CLAIM_DIR / "raw" / "window_calibration_spec.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        for row in csv.DictReader(handle):
            words = int(row["word_vocabulary"])
            completed = run_checker(words)
            if completed.returncode != 0:
                raise RuntimeError(f"independent checker failed for W={words}")
            result = json.loads(completed.stdout)
            if not result["success_probability"] >= result["target_probability"]:
                raise RuntimeError("calibrated window did not reach 99%")
            if not result["previous_success_probability"] < result["target_probability"]:
                raise RuntimeError("window was not the independently calibrated first hit")
            if not result["minimum_context_window"] <= result[
                "calibrated_window_linear_bound"
            ]:
                raise RuntimeError("calibrated context window was not O(W)")
            if not result["minimum_target_attention_weight"] > 0.5:
                raise RuntimeError("finite attention did not preserve the target code")
            if result["mamba_reachable_prefix_states"] != 2 * words - 1:
                raise RuntimeError("Mamba prefix-state count changed")
            if not result["embedding_dimension"] <= result["dimension_upper_bound"]:
                raise RuntimeError("embedding dimension certificate failed")
            if result["direct_correct_when_defined"] != (
                result["successful_joint_inputs"]
                if words == 2
                else result["direct_cases"]
            ):
                raise RuntimeError("direct construction checks failed")
            rows.append(result)

    # Independent analytic certificate. For each fixed query word, the last K
    # iid uniform word slots omit it with probability ((W-1)/W)^K. The binary
    # search above—not the formula—selects the smallest K reaching 0.99.
    symbolic_certificate = {
        "distribution": (
            "K iid uniform word tokens followed by log2(W) bits encoding a "
            "uniform query word; absence is conservatively counted as failure"
        ),
        "success_probability": "1 - ((W-1)/W)^K",
        "window_bound": "K <= ceil(W ln 100)+1, hence K=O(W)",
        "mamba_states": "all binary prefixes through length log2(W): 2W-1",
        "attention_1": "masked previous/current pairing",
        "attention_2": (
            "word-code matching with strict recency bias and finite temperature; "
            "last matching pair has mass >1/2"
        ),
        "dimension": "3 ceil(log2(W+2))+2 ceil(log2 L)+2",
    }

    representative = run_checker(2)
    expected = json.loads(
        (CLAIM_DIR / "checker_output.json").read_text(encoding="utf-8")
    )
    if representative.returncode != expected.pop("returncode"):
        raise RuntimeError("representative checker return code changed")
    observed = json.loads(representative.stdout)
    for key, value in expected.items():
        if observed[key] != value:
            raise RuntimeError(f"representative output changed: {key}")

    control = run_checker(2, control=True)
    expected_control = json.loads(
        (CLAIM_DIR / "negative_control_output.json").read_text(encoding="utf-8")
    )
    expected_returncode = expected_control.pop("returncode")
    if control.returncode != expected_returncode:
        raise RuntimeError("below-threshold control return code changed")
    if json.loads(control.stdout) != expected_control:
        raise RuntimeError("below-threshold control output changed")
    if control.returncode == 0:
        raise RuntimeError("below-threshold negative control unexpectedly passed")

    output = {
        "claim": 4,
        "verdict": "VERIFIED",
        "scope": (
            "The associative-recall restatement under an explicit iid-uniform "
            "word context followed by the fixed-length query-bit suffix."
        ),
        "calibrated_sweep": {
            "rows": rows,
            "all_first_hits": True,
            "minimum_success_probability": min(
                row["success_probability"] for row in rows
            ),
        },
        "symbolic_certificate": symbolic_certificate,
        "negative_control": {
            "returncode": control.returncode,
            "expected": "nonzero because K-1 is strictly below 99%",
            "output": json.loads(control.stdout),
        },
        "source_caveats": [
            "The main theorem accidentally says selective copying; the task, heading, and appendix restatement say associative recall with decoding.",
            "The source alternates between uniform non-bit tokens and a uniform full sequence; this verifier uses the former, matching the imported claim.",
            "A power-of-two word vocabulary and exactly log2(W) query bits are required for the stated binary decoder.",
            "Absent query words are counted as failures, although the source's last-occurrence target is undefined there.",
        ],
        "confidence": "MEDIUM",
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
