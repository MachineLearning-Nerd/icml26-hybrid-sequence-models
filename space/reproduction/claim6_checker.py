#!/usr/bin/env python3
"""Independently replay frozen Figure 6 evidence for the exact Claim 6 wording."""

from __future__ import annotations

import argparse
import copy
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reproduction.figure_training import count_parameters, make_model, make_tokenizer


RAW_PATH = (
    ROOT
    / ".openresearch"
    / "artifacts"
    / "claim_6"
    / "raw"
    / "figure6_full_evidence.json"
)
ACCEPTED_SHA = "133ddebd7a6888bde8abe4e511e09a966a506828"
ABSOLUTE_TOLERANCE = 1e-12
DIMENSIONS = (4, 8, 12, 16, 20, 24)
FAMILIES = {
    "tf_tf": (["TF", "TF"], 1),
    "ssm_ssm": (["SSM", "SSM"], 16),
    "tf_ssm": (["TF", "SSM"], 16),
    "ssm_tf": (["SSM", "TF"], 16),
}
PAPER_TABLE = {
    "1000": {
        "ssm_ssm": 0.158,
        "ssm_tf": 0.144,
        "tf_ssm": 0.131,
        "tf_tf": 0.124,
    },
    "2000": {
        "ssm_ssm": 0.173,
        "ssm_tf": 0.512,
        "tf_ssm": 0.183,
        "tf_tf": 0.159,
    },
    "6000": {
        "ssm_ssm": 0.356,
        "ssm_tf": 0.990,
        "tf_ssm": 0.286,
        "tf_tf": 0.230,
    },
    "12000": {
        "ssm_ssm": 0.517,
        "ssm_tf": 0.989,
        "tf_ssm": 0.524,
        "tf_tf": 0.668,
    },
}


class EvidenceError(RuntimeError):
    pass


def close(left: float, right: float) -> bool:
    return math.isclose(
        float(left), float(right), rel_tol=0.0, abs_tol=ABSOLUTE_TOLERANCE
    )


def check_evaluation(evaluation: dict) -> None:
    correct = int(evaluation["correct_tokens"])
    valid = int(evaluation["valid_tokens"])
    if valid <= 0 or not close(evaluation["accuracy"], correct / valid):
        raise EvidenceError("accuracy is not correct_tokens/valid_tokens")


def instantiate_counts() -> dict[str, int]:
    torch.set_num_threads(1)
    tokenizer = make_tokenizer("assoc-recall-mk", 8, 0)
    counts: dict[str, int] = {}
    for family, (layers, state_size) in FAMILIES.items():
        for hidden_size in DIMENSIONS:
            point_id = f"{family}_d{hidden_size}"
            model = make_model(
                layers=layers,
                hidden_size=hidden_size,
                vocabulary_size=len(tokenizer),
                state_size=state_size,
                expansion=2,
            )
            counts[point_id] = count_parameters(model)
    return counts


def aggregate(rows: list[dict]) -> dict:
    accuracies = [float(row["final_evaluation"]["accuracy"]) for row in rows]
    mean = statistics.fmean(accuracies)
    deviation = statistics.stdev(accuracies)
    half_width = 1.96 * deviation / math.sqrt(len(accuracies))
    return {
        "seeds": len(accuracies),
        "mean_accuracy": mean,
        "standard_deviation": deviation,
        "normal_95_interval_across_seeds": [
            max(0.0, mean - half_width),
            min(1.0, mean + half_width),
        ],
        "minimum": min(accuracies),
        "maximum": max(accuracies),
    }


def validate(document: dict) -> dict:
    if document["git_sha"] != ACCEPTED_SHA or document["overall"] != "PASS":
        raise EvidenceError("wrong accepted run or cumulative result")
    evidence = document["empirical_result"]
    if evidence["stage"] != "claim_6_mkar_parameter_frontier":
        raise EvidenceError("wrong empirical stage")
    source = evidence["source_contract"]
    if source != {
        "task": "multi-key associative recall",
        "sequence_length": 100,
        "vocabulary_size": 8,
        "key_length": 2,
        "paper_runs": 11,
        "paper_threshold_accuracy": 0.6,
        "paper_parameter_ratio": 6.0,
        "paper_table": PAPER_TABLE,
    }:
        raise EvidenceError("source contract changed")

    runtime = evidence["runtime"]
    if (
        runtime["calibration_jobs"] != 192
        or runtime["final_jobs"] != 264
        or runtime["negative_control_jobs"] != 1
        or runtime["max_workers"] != 6
        or runtime["torch_threads_per_worker"] != 1
        or runtime["estimated_scientific_cores"] != 6
        or runtime["cgroup_cpu_quota"] != 8.0
    ):
        raise EvidenceError("runtime or CPU contract changed")

    calibration = evidence["calibration"]["raw_runs"]
    final = evidence["final_runs"]
    if len(calibration) != 192 or len(final) != 264:
        raise EvidenceError("raw job counts changed")
    all_rows = calibration + final
    if len({row["job_id"] for row in all_rows}) != len(all_rows):
        raise EvidenceError("job ids are not unique")
    if any(int(row["torch_threads"]) != 1 for row in all_rows):
        raise EvidenceError("a training job used more than one Torch thread")

    instantiated = instantiate_counts()
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in final:
        check_evaluation(row["final_evaluation"])
        point_id = row["point_id"]
        if point_id not in instantiated:
            raise EvidenceError(f"unknown point {point_id}")
        if int(row["parameters"]) != instantiated[point_id]:
            raise EvidenceError(f"parameter count changed for {point_id}")
        if int(row["steps"]) != 4000:
            raise EvidenceError("final training horizon changed")
        grouped[point_id].append(row)
    if set(grouped) != set(instantiated) or any(
        len(rows) != 11 for rows in grouped.values()
    ):
        raise EvidenceError("24-point by 11-seed grid is incomplete")

    summaries = {point: aggregate(rows) for point, rows in grouped.items()}
    for point_id, observed in summaries.items():
        expected = evidence["point_summaries"][point_id]["statistics"]
        for key in (
            "mean_accuracy",
            "standard_deviation",
            "minimum",
            "maximum",
        ):
            if not close(observed[key], expected[key]):
                raise EvidenceError(f"aggregate changed for {point_id}: {key}")
        if any(
            not close(left, right)
            for left, right in zip(
                observed["normal_95_interval_across_seeds"],
                expected["normal_95_interval_across_seeds"],
                strict=True,
            )
        ):
            raise EvidenceError(f"interval changed for {point_id}")

    hits: dict[str, dict | None] = {}
    for family in FAMILIES:
        eligible = [
            (instantiated[point_id], point_id)
            for point_id, summary in summaries.items()
            if point_id.startswith(f"{family}_")
            and summary["mean_accuracy"] >= 0.60
        ]
        if eligible:
            parameters, point_id = min(eligible)
            hits[family] = {
                "point_id": point_id,
                "parameters": parameters,
                "mean_accuracy": summaries[point_id]["mean_accuracy"],
                "normal_95_interval_across_seeds": summaries[point_id][
                    "normal_95_interval_across_seeds"
                ],
            }
        else:
            hits[family] = None

    if hits["ssm_tf"] is None or hits["tf_tf"] is None:
        raise EvidenceError("required first hit is absent")
    ratio = hits["tf_tf"]["parameters"] / hits["ssm_tf"]["parameters"]
    if not close(ratio, evidence["pure_tf_to_ssm_tf_first_hit_parameter_ratio"]):
        raise EvidenceError("first-hit ratio changed")
    if ratio >= 3.0 or close(ratio, source["paper_parameter_ratio"]):
        raise EvidenceError("evidence no longer contradicts the exact 6x wording")

    control = evidence["negative_control"]
    check_evaluation(control["final_evaluation"])
    if (
        not control["random_targets"]
        or int(control["steps"]) != 4000
        or float(control["final_evaluation"]["accuracy"]) >= 0.25
    ):
        raise EvidenceError("random-target control failed")

    return {
        "verdict": "FALSIFIED",
        "confidence": "HIGH",
        "accepted_run_git_sha": ACCEPTED_SHA,
        "raw_calibration_jobs": len(calibration),
        "raw_final_jobs": len(final),
        "independently_instantiated_parameter_counts": instantiated,
        "first_mean_accuracy_0_60_hits": hits,
        "pure_tf_to_ssm_tf_first_hit_parameter_ratio": ratio,
        "paper_parameter_ratio": source["paper_parameter_ratio"],
        "ratio_difference": ratio - source["paper_parameter_ratio"],
        "random_target_control_accuracy": control["final_evaluation"]["accuracy"],
        "figure_5_source_correction": (
            "Figure 5 is associative recall with a five-bit decoded control "
            "variable, not single-key associative recall."
        ),
        "figure_5_full_scale_status": (
            "Not rerun on CPU through dimensions 384/768; not used as the "
            "basis for the FALSIFIED composite verdict."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-control", action="store_true")
    args = parser.parse_args()
    document = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    if args.negative_control:
        mutated = copy.deepcopy(document)
        mutated["empirical_result"][
            "pure_tf_to_ssm_tf_first_hit_parameter_ratio"
        ] = 6.0
        try:
            validate(mutated)
        except EvidenceError as exc:
            print(
                json.dumps(
                    {
                        "status": "EXPECTED_FAILURE",
                        "mutation": "reported first-hit ratio changed to 6.0",
                        "reason": str(exc),
                    },
                    sort_keys=True,
                )
            )
            return 4
        print(json.dumps({"status": "UNEXPECTED_PASS"}, sort_keys=True))
        return 0
    try:
        print(json.dumps(validate(document), indent=2, sort_keys=True))
    except EvidenceError as exc:
        print(f"EVIDENCE_ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
