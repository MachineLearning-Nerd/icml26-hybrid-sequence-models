#!/usr/bin/env python3
"""Independently replay the frozen Figure 4 evidence."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reproduction.figure_training import (
    count_parameters,
    make_model,
    make_tokenizer,
)


RAW_PATH = (
    ROOT
    / ".openresearch"
    / "artifacts"
    / "claim_5"
    / "raw"
    / "frontier_results.json"
)
ABSOLUTE_TOLERANCE = 1e-12
POINTS = {
    "ssm_tf_d4": (["SSM", "TF"], 4, 16, 872, False),
    "ssm_tf_d8": (["SSM", "TF"], 8, 16, 2192, True),
    "ssm_tf_d12": (["SSM", "TF"], 12, 16, 3960, False),
    "tf_ssm_d8": (["TF", "SSM"], 8, 16, 2192, True),
    "tf_tf_d16": (["TF", "TF"], 16, 1, 5024, False),
    "tf_tf_d20": (["TF", "TF"], 20, 1, 7560, False),
    "tf_tf_d24": (["TF", "TF"], 24, 1, 10608, True),
    "tf_tf_d32": (["TF", "TF"], 32, 1, 18240, False),
    "ssm_ssm_d16": (["SSM", "SSM"], 16, 16, 7328, False),
    "ssm_ssm_d20": (["SSM", "SSM"], 20, 16, 10280, False),
    "ssm_ssm_d24": (["SSM", "SSM"], 24, 16, 13488, True),
    "ssm_ssm_d32": (["SSM", "SSM"], 32, 16, 21056, False),
}
CALIBRATION_SEEDS = {260350001, 260350002}
FRONTIER_SEEDS = {260351001, 260351002, 260351003}
HEADLINE_SEEDS = set(range(260352001, 260352012))


class EvidenceError(RuntimeError):
    pass


def close(observed: float, expected: float) -> bool:
    return math.isclose(
        float(observed),
        float(expected),
        rel_tol=0.0,
        abs_tol=ABSOLUTE_TOLERANCE,
    )


def check_evaluation(evaluation: dict) -> None:
    correct = int(evaluation["correct_tokens"])
    valid = int(evaluation["valid_tokens"])
    if valid <= 0 or not close(evaluation["accuracy"], correct / valid):
        raise EvidenceError("accuracy does not equal correct_tokens/valid_tokens")
    exact = int(evaluation["exact_sequences"])
    defined = int(evaluation["defined_sequences"])
    if defined <= 0 or not close(
        evaluation["exact_sequence_accuracy"], exact / defined
    ):
        raise EvidenceError("exact sequence accuracy is not independently reproducible")


def aggregate(rows: list[dict]) -> dict:
    accuracies = [float(row["final_evaluation"]["accuracy"]) for row in rows]
    mean = statistics.fmean(accuracies)
    standard_deviation = statistics.stdev(accuracies) if len(accuracies) > 1 else 0.0
    half_width = 1.96 * standard_deviation / math.sqrt(len(accuracies))
    return {
        "seeds": len(accuracies),
        "accuracies": accuracies,
        "mean_accuracy": mean,
        "standard_deviation": standard_deviation,
        "normal_95_interval_across_seeds": [
            max(0.0, mean - half_width),
            min(1.0, mean + half_width),
        ],
        "quantile_10": float(np.quantile(accuracies, 0.1)),
        "quantile_90": float(np.quantile(accuracies, 0.9)),
        "minimum": min(accuracies),
        "maximum": max(accuracies),
        "total_valid_tokens": sum(
            int(row["final_evaluation"]["valid_tokens"]) for row in rows
        ),
    }


def compare_statistics(observed: dict, expected: dict) -> None:
    for key in (
        "mean_accuracy",
        "standard_deviation",
        "quantile_10",
        "quantile_90",
        "minimum",
        "maximum",
    ):
        if not close(observed[key], expected[key]):
            raise EvidenceError(f"aggregate changed: {key}")
    for observed_value, expected_value in zip(
        observed["normal_95_interval_across_seeds"],
        expected["normal_95_interval_across_seeds"],
        strict=True,
    ):
        if not close(observed_value, expected_value):
            raise EvidenceError("aggregate interval changed")
    for key in ("seeds", "accuracies", "total_valid_tokens"):
        if observed[key] != expected[key]:
            raise EvidenceError(f"aggregate changed: {key}")


def one_sided_sign_test(wins: int, losses: int) -> float:
    trials = wins + losses
    return sum(
        math.comb(trials, successes) for successes in range(wins, trials + 1)
    ) / (2**trials)


def paired_route(final_rows: list[dict], pure_point: str) -> dict:
    def by_seed(point: str) -> dict[int, float]:
        return {
            int(row["seed"]): float(row["final_evaluation"]["accuracy"])
            for row in final_rows
            if row["point_id"] == point
        }

    hybrid = by_seed("ssm_tf_d8")
    pure = by_seed(pure_point)
    if set(hybrid) != HEADLINE_SEEDS or set(pure) != HEADLINE_SEEDS:
        raise EvidenceError("paired route does not contain the 11 fixed seeds")
    differences = [hybrid[seed] - pure[seed] for seed in sorted(HEADLINE_SEEDS)]
    wins = sum(value > ABSOLUTE_TOLERANCE for value in differences)
    losses = sum(value < -ABSOLUTE_TOLERANCE for value in differences)
    ties = len(differences) - wins - losses
    return {
        "pure_point": pure_point,
        "paired_seeds": sorted(HEADLINE_SEEDS),
        "hybrid_minus_pure": differences,
        "mean_difference": statistics.fmean(differences),
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "one_sided_exact_sign_p": one_sided_sign_test(wins, losses),
    }


def instantiated_parameter_counts() -> dict[str, int]:
    torch.set_num_threads(1)
    tokenizer = make_tokenizer("var-copy", 26, 5)
    counts: dict[str, int] = {}
    for point_id, (layers, hidden, state, expected, _) in POINTS.items():
        model = make_model(
            layers=layers,
            hidden_size=hidden,
            vocabulary_size=len(tokenizer),
            state_size=state,
            expansion=2,
        )
        observed = count_parameters(model)
        if observed != expected:
            raise EvidenceError(
                f"instantiated count for {point_id} is {observed}, expected {expected}"
            )
        counts[point_id] = observed
    return counts


def validate(data: dict) -> dict:
    if data["stage"] != "claim_5_selective_copy_parameter_frontier":
        raise EvidenceError("wrong scientific stage")
    runtime = data["runtime"]
    if (
        runtime["calibration_jobs"] != 72
        or runtime["final_jobs"] != 68
        or runtime["negative_control_jobs"] != 1
        or runtime["max_workers"] != 8
        or runtime["torch_threads_per_worker"] != 1
        or runtime["estimated_scientific_cores"] != 8
        or runtime["cgroup_cpu_quota"] != 8.0
    ):
        raise EvidenceError("CPU allocation or job-count contract changed")

    calibration = data["calibration"]
    calibration_rows = calibration["raw_runs"]
    final_rows = data["final_runs"]
    if len(calibration_rows) != 72 or len(final_rows) != 68:
        raise EvidenceError("raw job counts changed")
    if len({row["job_id"] for row in calibration_rows + final_rows}) != 140:
        raise EvidenceError("job ids are not unique")

    learning_rates = {float(value) for value in calibration["learning_rates"]}
    if learning_rates != {
        0.0031622776601683794,
        0.01,
        0.03162277660168379,
    }:
        raise EvidenceError("learning-rate calibration grid changed")

    for row in calibration_rows:
        if (
            row["point_id"] not in POINTS
            or int(row["seed"]) not in CALIBRATION_SEEDS
            or int(row["steps"]) != 1000
            or int(row["torch_threads"]) != 1
            or float(row["cgroup_cpu_quota"]) != 8.0
        ):
            raise EvidenceError("calibration job contract changed")
        check_evaluation(row["final_evaluation"])

    selected: dict[str, float] = {}
    for point_id in POINTS:
        candidates = []
        for learning_rate in sorted(learning_rates):
            rows = [
                row
                for row in calibration_rows
                if row["point_id"] == point_id
                and close(row["learning_rate"], learning_rate)
            ]
            if len(rows) != 2:
                raise EvidenceError("calibration replicate count changed")
            candidates.append(
                (
                    statistics.fmean(
                        float(row["mean_training_loss"]) for row in rows
                    ),
                    learning_rate,
                )
            )
        selected[point_id] = min(candidates)[1]
        if not close(selected[point_id], calibration["selected"][point_id]):
            raise EvidenceError("learning-rate selection is not reproducible")

    summaries: dict[str, dict] = {}
    for row in final_rows:
        point_id = row["point_id"]
        if point_id not in POINTS:
            raise EvidenceError("unknown final point")
        layers, hidden, state, parameters, headline = POINTS[point_id]
        expected_seeds = HEADLINE_SEEDS if headline else FRONTIER_SEEDS
        if (
            list(row["layers"]) != layers
            or int(row["hidden_size"]) != hidden
            or int(row["effective_state_size"]) != state
            or int(row["parameters"]) != parameters
            or int(row["seed"]) not in expected_seeds
            or int(row["steps"]) != 4000
            or int(row["torch_threads"]) != 1
            or float(row["cgroup_cpu_quota"]) != 8.0
            or not close(row["learning_rate"], selected[point_id])
        ):
            raise EvidenceError(f"final job contract changed for {point_id}")
        check_evaluation(row["final_evaluation"])

    for point_id, (_, _, _, _, headline) in POINTS.items():
        rows = [row for row in final_rows if row["point_id"] == point_id]
        expected_seed_set = HEADLINE_SEEDS if headline else FRONTIER_SEEDS
        if {int(row["seed"]) for row in rows} != expected_seed_set:
            raise EvidenceError(f"final seed set changed for {point_id}")
        summaries[point_id] = aggregate(rows)
        compare_statistics(
            summaries[point_id],
            data["point_summaries"][point_id]["statistics"],
        )

    control = data["negative_control"]
    check_evaluation(control["final_evaluation"])
    if (
        not control["random_targets"]
        or int(control["steps"]) != 4000
        or float(control["final_evaluation"]["accuracy"]) >= 0.2
        or int(control["final_evaluation"]["exact_sequences"]) != 0
    ):
        raise EvidenceError("random-target negative control did not fail as intended")

    first_hits = {}
    for prefix in ("ssm_tf", "tf_tf", "ssm_ssm"):
        eligible = [
            (POINTS[point_id][3], point_id)
            for point_id, summary in summaries.items()
            if point_id.startswith(prefix + "_")
            and summary["mean_accuracy"] >= 0.9
        ]
        if not eligible:
            raise EvidenceError(f"no 90% first hit for {prefix}")
        first_hits[prefix] = min(eligible)
    expected_first_hits = {
        "ssm_tf": (2192, "ssm_tf_d8"),
        "tf_tf": (18240, "tf_tf_d32"),
        "ssm_ssm": (21056, "ssm_ssm_d32"),
    }
    if first_hits != expected_first_hits:
        raise EvidenceError("independent 90% first hits changed")

    parameter_counts = instantiated_parameter_counts()
    paired_tf = paired_route(final_rows, "tf_tf_d24")
    paired_ssm = paired_route(final_rows, "ssm_ssm_d24")
    if (
        paired_tf["one_sided_exact_sign_p"] >= 0.05
        or paired_ssm["one_sided_exact_sign_p"] >= 0.05
        or paired_tf["mean_difference"] <= 0
        or paired_ssm["mean_difference"] <= 0
    ):
        raise EvidenceError("paired-seed superiority route did not pass")

    source = data["source_contracts"]["paper_table"]
    if source != {
        "hybrid_approx_2000": 0.999,
        "pure_ssm_approx_12000": 0.931,
        "pure_tf_approx_12000": 0.923,
    }:
        raise EvidenceError("paper table transcription changed")

    return {
        "claim": 5,
        "verdict": "FALSIFIED",
        "confidence": "MEDIUM",
        "exact_imported_contract": (
            "Approximately-2k hybrid is perfect and approximately-12k pure "
            "models match it, constituting an exact 6x gap."
        ),
        "source_route": {
            "paper_table": source,
            "paper_caption": data["source_contracts"]["paper_caption"],
            "finding": (
                "The paper itself says the pure models attain around 0.9, not "
                "that they match the perfect hybrid."
            ),
        },
        "independent_replay_route": {
            "hybrid_2192": summaries["ssm_tf_d8"],
            "pure_tf_10608": summaries["tf_tf_d24"],
            "pure_ssm_13488": summaries["ssm_ssm_d24"],
            "random_target_accuracy": control["final_evaluation"]["accuracy"],
        },
        "paired_seed_route": {
            "hybrid_vs_pure_tf": paired_tf,
            "hybrid_vs_pure_ssm": paired_ssm,
        },
        "finite_frontier_route": {
            "threshold": 0.9,
            "first_hits": {
                key: {"parameters": value[0], "point_id": value[1]}
                for key, value in first_hits.items()
            },
            "ratios_relative_to_hybrid": {
                "pure_tf": first_hits["tf_tf"][0] / first_hits["ssm_tf"][0],
                "pure_ssm": first_hits["ssm_ssm"][0] / first_hits["ssm_tf"][0],
            },
            "scope": "first hits in the precommitted calibrated width grid",
        },
        "instantiated_parameter_counts": parameter_counts,
        "negative_control": {
            "random_targets": True,
            "accuracy": control["final_evaluation"]["accuracy"],
            "threshold": 0.2,
            "passed": True,
        },
        "strict_route_status": data["exact_imported_claim_verdict"],
        "strict_route_limitation": data["verdict_basis"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-control", action="store_true")
    args = parser.parse_args()
    data = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    if args.negative_control:
        data["point_summaries"]["ssm_tf_d8"]["statistics"]["mean_accuracy"] = 0.0
    try:
        output = validate(data)
    except EvidenceError as exc:
        print(
            json.dumps(
                {
                    "expected_failure": args.negative_control,
                    "error": str(exc),
                },
                sort_keys=True,
            )
        )
        return 4
    if args.negative_control:
        print("negative-control mutation unexpectedly passed", file=sys.stderr)
        return 5
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
