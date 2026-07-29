#!/usr/bin/env python3
"""Independent exhaustive checker for the selective-copying hybrid."""

from __future__ import annotations

import argparse
import itertools
import json
import math


def bits_needed(cardinality: int) -> int:
    return max(1, math.ceil(math.log2(cardinality)))


def binary_code(value: int, width: int) -> tuple[int, ...]:
    return tuple(
        1 if (value >> shift) & 1 else -1 for shift in reversed(range(width))
    )


def dot(left: tuple[float, ...], right: tuple[int, ...]) -> float:
    return sum(a * b for a, b in zip(left, right))


def target(sequence: tuple[int, ...], number_tokens: int) -> tuple[int, int] | None:
    control = None
    for token in sequence:
        if 1 <= token <= number_tokens:
            control = token
    if control is None:
        return None
    return sequence[len(sequence) - control], control


def hybrid_output(
    sequence: tuple[int, ...],
    vocabulary_size: int,
    number_tokens: int,
    temperature: float,
) -> tuple[int, float, int]:
    # Mamba recurrence: Delta=1 on number tokens replaces the state; Delta=0
    # carries it. The reachable state is {None,1,...,N}.
    state = None
    for token in sequence:
        if 1 <= token <= number_tokens:
            state = token
    if state is None:
        raise ValueError("selective copying is undefined without a number token")

    token_width = bits_needed(vocabulary_size)
    position_width = bits_needed(len(sequence))
    query = binary_code(state - 1, position_width)
    window = sequence[-number_tokens:]
    distances = list(range(number_tokens, 0, -1))
    scores = [
        temperature * dot(query, binary_code(distance - 1, position_width))
        for distance in distances
    ]
    maximum = max(scores)
    unnormalized = [math.exp(score - maximum) for score in scores]
    denominator = sum(unnormalized)
    weights = [weight / denominator for weight in unnormalized]
    target_slot = distances.index(state)
    target_weight = weights[target_slot]

    value_codes = [binary_code(token, token_width) for token in window]
    attended = tuple(
        sum(weight * code[coordinate] for weight, code in zip(weights, value_codes))
        for coordinate in range(token_width)
    )
    logits = [
        dot(attended, binary_code(token, token_width))
        for token in range(vocabulary_size)
    ]
    prediction = max(range(vocabulary_size), key=lambda token: logits[token])
    return prediction, target_weight, target_slot


def run_control() -> int:
    sequence = (0, 2, 3, 0)
    expected, control = target(sequence, 2) or (-1, -1)
    prediction, target_weight, target_slot = hybrid_output(sequence, 4, 2, 0.0)
    output = {
        "control": "zero attention temperature",
        "sequence": list(sequence),
        "number_tokens": 2,
        "control_value": control,
        "target_slot_in_window": target_slot,
        "expected_token": expected,
        "predicted_token": prediction,
        "target_attention_weight": target_weight,
        "correct": prediction == expected,
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if prediction == expected else 7


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--length", type=int)
    parser.add_argument("--vocabulary-size", type=int)
    parser.add_argument("--number-tokens", type=int)
    parser.add_argument("--zero-temperature-control", action="store_true")
    args = parser.parse_args()
    if args.zero_temperature_control:
        return run_control()
    if (
        args.length is None
        or args.vocabulary_size is None
        or args.number_tokens is None
        or args.length < 1
        or not 1 <= args.number_tokens < args.vocabulary_size
        or args.number_tokens > args.length
    ):
        raise SystemExit(2)

    temperature = 1.0 + 0.5 * math.log(max(1, args.number_tokens - 1))
    theoretical_target_weight_lower_bound = 1.0 / (
        1.0 + (args.number_tokens - 1) * math.exp(-2.0 * temperature)
    )
    total_sequences = args.vocabulary_size**args.length
    undefined_sequences = (args.vocabulary_size - args.number_tokens) ** args.length
    valid_sequences = 0
    correct_sequences = 0
    minimum_target_weight = 1.0

    for sequence in itertools.product(
        range(args.vocabulary_size), repeat=args.length
    ):
        oracle = target(sequence, args.number_tokens)
        if oracle is None:
            continue
        expected, _ = oracle
        prediction, target_weight, _ = hybrid_output(
            sequence,
            args.vocabulary_size,
            args.number_tokens,
            temperature,
        )
        valid_sequences += 1
        correct_sequences += int(prediction == expected)
        minimum_target_weight = min(minimum_target_weight, target_weight)

    token_width = bits_needed(args.vocabulary_size)
    position_width = bits_needed(args.length)
    embedding_dimension = 2 * token_width + 2 * position_width + 1
    output = {
        "length": args.length,
        "vocabulary_size": args.vocabulary_size,
        "number_tokens": args.number_tokens,
        "total_sequences": total_sequences,
        "undefined_no_number_sequences": undefined_sequences,
        "valid_sequences": valid_sequences,
        "correct_sequences": correct_sequences,
        "accuracy_on_defined_domain": correct_sequences / valid_sequences,
        "temperature": temperature,
        "minimum_target_attention_weight": minimum_target_weight,
        "theoretical_target_weight_lower_bound": (
            theoretical_target_weight_lower_bound
        ),
        "token_code_bits": token_width,
        "position_code_bits": position_width,
        "embedding_dimension": embedding_dimension,
        "dimension_upper_bound": 4 * max(token_width, position_width) + 1,
        "reachable_mamba_states": args.number_tokens + 1,
        "attention_window": args.number_tokens,
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if correct_sequences == valid_sequences else 8


if __name__ == "__main__":
    raise SystemExit(main())
