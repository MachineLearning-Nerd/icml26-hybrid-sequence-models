#!/usr/bin/env python3
"""Independent checker for Theorem 3.7's two-witness certificate."""

from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--length", type=int, required=True)
    parser.add_argument("--range", dest="dependency_range", type=int, required=True)
    parser.add_argument("--windows", required=True)
    parser.add_argument("--over-budget-control", action="store_true")
    args = parser.parse_args()

    windows = [int(value) for value in args.windows.split(",") if value]
    if (
        args.length < 2
        or not 1 <= args.dependency_range < args.length
        or not windows
        or any(window < 0 for window in windows)
    ):
        raise SystemExit(2)

    effective_window = sum(windows)
    if args.over_budget_control:
        windows = [args.dependency_range + 1]
        effective_window = sum(windows)

    # The two target witnesses differ just before their shared R-token suffix.
    differing_position = args.length - args.dependency_range - 1
    left = [0] * args.length
    right = [0] * args.length
    right[differing_position] = 1
    target_labels = [0, 1]
    shared_r_suffix = left[-args.dependency_range :] == right[-args.dependency_range :]

    # This is the precise dependency premise asserted in the paper's proof:
    # a stack with total window W has final output determined by its last W
    # inputs. Empty W is represented by an empty suffix.
    if effective_window == 0:
        left_observation: list[int] = []
        right_observation: list[int] = []
    else:
        left_observation = left[-effective_window:]
        right_observation = right[-effective_window:]
    indistinguishable = left_observation == right_observation

    # Exhaust all binary deterministic outputs on the common observation.
    deterministic_accuracies = [
        sum(int(prediction == label) for label in target_labels) / 2
        for prediction in (0, 1)
    ]
    output = {
        "length": args.length,
        "dependency_range": args.dependency_range,
        "windows": windows,
        "total_window": effective_window,
        "differing_position_zero_based": differing_position,
        "shared_r_suffix": shared_r_suffix,
        "observations_equal": indistinguishable,
        "target_labels_differ": target_labels[0] != target_labels[1],
        "deterministic_predictor_accuracies": deterministic_accuracies,
        "max_accuracy_on_uniform_pair": max(deterministic_accuracies),
        "target_threshold": 2 / 3,
        "premise_total_window_below_r": effective_window < args.dependency_range,
    }
    print(json.dumps(output, sort_keys=True))

    if not shared_r_suffix or target_labels[0] == target_labels[1]:
        return 4
    if not effective_window < args.dependency_range:
        return 5
    if not indistinguishable or max(deterministic_accuracies) != 0.5:
        return 6
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
