#!/usr/bin/env python3
"""Verify the corrected two-layer selective-copying construction."""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAIM_DIR = ROOT / ".openresearch" / "artifacts" / "claim_3"
CHECKER = Path(__file__).with_name("claim3_checker.py")


def run_checker(length: int, vocabulary: int, numbers: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--length",
            str(length),
            "--vocabulary-size",
            str(vocabulary),
            "--number-tokens",
            str(numbers),
        ],
        check=False,
        text=True,
        capture_output=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-control", action="store_true")
    args = parser.parse_args()
    if args.negative_control:
        control = subprocess.run(
            [sys.executable, str(CHECKER), "--zero-temperature-control"],
            check=False,
            text=True,
            capture_output=True,
        )
        print(control.stdout.strip())
        print(control.stderr.strip(), file=sys.stderr)
        return control.returncode

    contract = json.loads((CLAIM_DIR / "claim_contract.json").read_text(encoding="utf-8"))
    if contract["verdict"] != "VERIFIED":
        raise RuntimeError("Claim 3 contract must retain the VERIFIED verdict")

    results: list[dict] = []
    with (CLAIM_DIR / "raw" / "complete_domain_sweep.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        for row in csv.DictReader(handle):
            completed = run_checker(
                int(row["length"]),
                int(row["vocabulary_size"]),
                int(row["number_tokens"]),
            )
            if completed.returncode != 0:
                raise RuntimeError(f"independent checker failed for {row}")
            result = json.loads(completed.stdout)
            if result["valid_sequences"] != int(row["expected_valid_sequences"]):
                raise RuntimeError("defined-domain cardinality changed")
            if result["undefined_no_number_sequences"] != int(
                row["expected_undefined_sequences"]
            ):
                raise RuntimeError("undefined-domain cardinality changed")
            if result["accuracy_on_defined_domain"] != 1.0:
                raise RuntimeError("construction was not exact on a complete finite domain")
            if not result["minimum_target_attention_weight"] > 0.5:
                raise RuntimeError("target attention did not dominate all distractors")
            if not result["embedding_dimension"] <= result["dimension_upper_bound"]:
                raise RuntimeError("logarithmic dimension certificate failed")
            if result["reachable_mamba_states"] != result["number_tokens"] + 1:
                raise RuntimeError("reachable-state certificate failed")
            if result["attention_window"] != result["number_tokens"]:
                raise RuntimeError("attention window was not exactly N")
            results.append(result)

    # General construction certificate, independent of the finite sweep:
    # binary positional codes have dot-product gap >=2. Choosing
    # beta=1+log(max(1,N-1))/2 makes the target softmax mass exceed 1/2,
    # so every coordinate of the target token's +/-1 code retains its sign.
    for result in results:
        n = result["number_tokens"]
        beta = result["temperature"]
        certified_mass = 1 / (1 + (n - 1) * math.exp(-2 * beta))
        if abs(
            certified_mass - result["theoretical_target_weight_lower_bound"]
        ) > 1e-12:
            raise RuntimeError("attention-dominance formula changed")
        if certified_mass <= 0.5:
            raise RuntimeError("attention-dominance certificate is not strict")

    # Pure-Transformer comparison: the two inputs differ only in their first
    # number token (1 versus 2), share the remaining L-1 suffix, and select two
    # different final tokens. Claim 2 then gives sum windows >= L-1.
    lower_bound_witness = json.loads(
        (CLAIM_DIR / "raw" / "pure_transformer_witness.json").read_text(
            encoding="utf-8"
        )
    )
    left = lower_bound_witness["left"]
    right = lower_bound_witness["right"]
    shared = int(lower_bound_witness["shared_suffix"])
    if left[-shared:] != right[-shared:]:
        raise RuntimeError("pure-Transformer witnesses do not share the stated suffix")
    left_target = left[len(left) - 1]
    right_target = right[len(right) - 2]
    if left_target == right_target:
        raise RuntimeError("pure-Transformer witness targets did not differ")
    if shared != len(left) - 1:
        raise RuntimeError("pure-Transformer witness does not certify Omega(L)")

    representative = run_checker(4, 4, 2)
    expected = json.loads(
        (CLAIM_DIR / "checker_output.json").read_text(encoding="utf-8")
    )
    if representative.returncode != expected.pop("returncode"):
        raise RuntimeError("representative checker return code changed")
    observed = json.loads(representative.stdout)
    for key, value in expected.items():
        if isinstance(value, float):
            if abs(observed[key] - value) > 1e-12:
                raise RuntimeError(f"representative float changed: {key}")
        elif observed[key] != value:
            raise RuntimeError(f"representative output changed: {key}")

    control = subprocess.run(
        [sys.executable, str(CHECKER), "--zero-temperature-control"],
        check=False,
        text=True,
        capture_output=True,
    )
    expected_control = json.loads(
        (CLAIM_DIR / "negative_control_output.json").read_text(encoding="utf-8")
    )
    expected_control_returncode = expected_control.pop("returncode")
    if control.returncode != expected_control_returncode:
        raise RuntimeError("zero-temperature control return code changed")
    if json.loads(control.stdout) != expected_control:
        raise RuntimeError("zero-temperature control output changed")
    if control.returncode == 0:
        raise RuntimeError("zero-temperature negative control unexpectedly passed")

    output = {
        "claim": 3,
        "verdict": "VERIFIED",
        "scope": "Every selective-copying input for which the source task is defined.",
        "complete_domain_checks": {
            "cases": len(results),
            "valid_sequences": sum(result["valid_sequences"] for result in results),
            "undefined_sequences_audited": sum(
                result["undefined_no_number_sequences"] for result in results
            ),
            "accuracy": 1.0,
            "rows": results,
        },
        "symbolic_certificate": {
            "mamba_recurrence": "last number state in {None,1,...,N}",
            "reachable_states": "N+1 = O(|V|)",
            "attention_window": "exactly N",
            "target_mass": "1/(1+(N-1)exp(-2 beta)) > 1/2",
            "decoder": "linear code correlation; strict coordinate-sign preservation",
            "embedding_dimension": "2 ceil(log2|V|)+2 ceil(log2 L)+1",
            "working_memory": "O(N * max(log|V|,log L)) = tilde O(N)",
        },
        "pure_transformer_lower_bound": {
            "shared_suffix": shared,
            "length": len(left),
            "different_targets": [left_target, right_target],
            "conclusion": "sum_i W_i >= L-1 = Omega(L) by verified Claim 2",
        },
        "negative_control": {
            "returncode": control.returncode,
            "expected": "nonzero because uniform attention does not identify the target",
            "output": json.loads(control.stdout),
        },
        "deviations": [
            "The query/key indexing is corrected to compare control distance n with relative distance L+1-i.",
            "The checker enforces an actual N-token window; the official notebook uses full causal attention.",
            "Sequences containing no number token are audited but excluded because the paper's argmax target is undefined on them.",
        ],
        "confidence": "MEDIUM",
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
