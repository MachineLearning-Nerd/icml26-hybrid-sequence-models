#!/usr/bin/env python3
"""Verify the exact Claim 1 contract and counterexample certificate."""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAIM_DIR = ROOT / ".openresearch" / "artifacts" / "claim_1"
CHECKER = Path(__file__).with_name("claim1_checker.py")


def binary_entropy(error: float) -> float:
    if error in {0.0, 1.0}:
        return 0.0
    return -error * math.log2(error) - (1 - error) * math.log2(1 - error)


def fano_lower_bound(m: int, alphabet_bits: int, q: int, error: float) -> float:
    return m * alphabet_bits - q * (binary_entropy(error) + error)


def run_checker(m: int, bits: int, negative: bool = False) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(CHECKER),
        "--m",
        str(m),
        "--alphabet-bits",
        str(bits),
    ]
    if negative:
        command.append("--drop-last-control")
    return subprocess.run(command, check=False, text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-control", action="store_true")
    args = parser.parse_args()
    if args.negative_control:
        control = run_checker(m=4, bits=2, negative=True)
        print(control.stdout.strip())
        print(control.stderr.strip(), file=sys.stderr)
        return control.returncode

    contract = json.loads((CLAIM_DIR / "claim_contract.json").read_text(encoding="utf-8"))
    certificate = json.loads(
        (CLAIM_DIR / "raw" / "counterexample_family.json").read_text(encoding="utf-8")
    )
    if contract["verdict"] != "FALSIFIED":
        raise RuntimeError("Claim 1 contract must retain the FALSIFIED verdict")
    if contract["tested_component"] != "linear_in_m_consequence":
        raise RuntimeError("contract does not identify the exact falsified component")

    rows: list[dict] = []
    with (CLAIM_DIR / "raw" / "cardinality_grid.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        for row in csv.DictReader(handle):
            m = int(row["m"])
            bits = int(row["alphabet_bits"])
            expected_q = int(row["q"])
            expected_domain_size = int(row["expected_domain_size"])
            expected_rhs = float(row["expected_printed_rhs_bits"])
            result = run_checker(m, bits)
            if result.returncode != 0:
                raise RuntimeError(f"independent checker failed for m={m}, bits={bits}")
            checked = json.loads(result.stdout)
            if checked["q"] != expected_q or not checked["injective"]:
                raise RuntimeError(f"certificate mismatch for m={m}, bits={bits}")
            if checked["domain_size"] != expected_domain_size:
                raise RuntimeError(f"domain-size mismatch for m={m}, bits={bits}")
            if abs(checked["printed_rhs_bits"] - expected_rhs) > 1e-12:
                raise RuntimeError("injective family did not make printed RHS exactly zero")
            if abs(checked["best_uniform_constant_success"] - 0.5) > 1e-12:
                raise RuntimeError("balanced control distribution was not exactly 1/2")
            rows.append(checked)

    # Cardinality route: injectivity G: V^m -> Y^q forces |Y|^q >= |V|^m.
    # Therefore m log|V| - q log|Y| <= 0 for every in-assumption function.
    general_cardinality_conclusion = certificate["cardinality_lemma"]
    if general_cardinality_conclusion != "q_log_Y_ge_m_log_V":
        raise RuntimeError("cardinality lemma missing from certificate")

    # Probability route: for binary Y and any theorem-chosen D, one constant
    # output is correct with probability at least 1/2. A singleton-state SSM
    # implements that predictor. This rules out a positive linear state lower
    # bound at the theorem's exact threshold.
    arbitrary_distribution_constant_success_lower_bound = 0.5
    singleton_state_log_bits = math.log2(1)

    # Proof-reconstruction route: the appendix obtains a positive bound only
    # after replacing the theorem threshold by error < 1/8.
    proof_rows = []
    for m in range(1, 9):
        q = 2 * m
        proof_rows.append(
            {
                "m": m,
                "q": q,
                "printed_rhs_bits": 2 * m - q,
                "fano_bound_error_1_2_bits": fano_lower_bound(m, 2, q, 0.5),
                "fano_bound_error_1_8_bits": fano_lower_bound(m, 2, q, 0.125),
            }
        )
    if not all(row["fano_bound_error_1_2_bits"] < 0 for row in proof_rows):
        raise RuntimeError("Fano reconstruction at error 1/2 was unexpectedly positive")
    if not all(row["fano_bound_error_1_8_bits"] > 0 for row in proof_rows):
        raise RuntimeError("Fano reconstruction at error 1/8 was not positive")

    control = run_checker(m=4, bits=2, negative=True)
    if control.returncode == 0:
        raise RuntimeError("negative control unexpectedly remained injective")
    control_output = json.loads(control.stdout)
    if control_output["injective"]:
        raise RuntimeError("negative control output contradicts its exit code")
    expected_checker = json.loads(
        (CLAIM_DIR / "checker_output.json").read_text(encoding="utf-8")
    )
    representative = run_checker(m=4, bits=2)
    representative_output = json.loads(representative.stdout)
    if representative.returncode != expected_checker.pop("returncode"):
        raise RuntimeError("representative checker return code changed")
    if representative_output != expected_checker:
        raise RuntimeError("representative independent-checker output changed")
    expected_control = json.loads(
        (CLAIM_DIR / "negative_control_output.json").read_text(encoding="utf-8")
    )
    expected_control.pop("control")
    if control.returncode != expected_control.pop("returncode"):
        raise RuntimeError("negative-control return code changed")
    if control_output != expected_control:
        raise RuntimeError("negative-control output changed")

    output = {
        "claim": 1,
        "verdict": "FALSIFIED",
        "scope": (
            "The imported claim that Theorem 3.3 establishes a state lower bound "
            "linear in m at success probability 1/2."
        ),
        "formal_inequality_note": (
            "The displayed Omega(m log|V|-q log|Y|) inequality is not contradicted; "
            "injectivity makes its argument non-positive, so it is vacuous."
        ),
        "routes": {
            "cardinality": {
                "result": "q log|Y| >= m log|V| for every injective G",
                "rows": rows,
            },
            "counterexample_family": {
                "V": 4,
                "Y": 2,
                "q": "2m",
                "G": "concatenated two-bit encodings of the m payload symbols",
                "singleton_state_log_bits": singleton_state_log_bits,
                "any_D_constant_success_at_least": (
                    arbitrary_distribution_constant_success_lower_bound
                ),
            },
            "proof_reconstruction": proof_rows,
        },
        "independent_checker": "PASS",
        "negative_control": {
            "returncode": control.returncode,
            "injective": control_output["injective"],
            "expected": "nonzero and non-injective",
        },
        "confidence": "HIGH",
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
