#!/usr/bin/env python3
"""Independent calibration and construction checker for decoded recall."""

from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction


TARGET = Fraction(99, 100)


def bits_needed(cardinality: int) -> int:
    return max(1, math.ceil(math.log2(cardinality)))


def code(value: int, width: int) -> tuple[int, ...]:
    return tuple(
        1 if (value >> shift) & 1 else -1 for shift in reversed(range(width))
    )


def dot(left: tuple[float, ...], right: tuple[int, ...]) -> float:
    return sum(a * b for a, b in zip(left, right))


def success_fraction(words: int, context_window: int) -> Fraction:
    return 1 - Fraction(words - 1, words) ** context_window


def first_hit(words: int) -> tuple[int, list[int]]:
    visited: list[int] = []
    high = 1
    while success_fraction(words, high) < TARGET:
        visited.append(high)
        high *= 2
    low = high // 2 + 1
    while low < high:
        midpoint = (low + high) // 2
        visited.append(midpoint)
        if success_fraction(words, midpoint) >= TARGET:
            high = midpoint
        else:
            low = midpoint + 1
    visited.append(low)
    return low, visited


def query_bits(query: int, width: int) -> tuple[int, ...]:
    return tuple(
        (query >> shift) & 1 for shift in reversed(range(width))
    )


def decode_query(bits: tuple[int, ...]) -> int:
    state = 0
    for bit in bits:
        state = (state << 1) | bit
    return state


def oracle(context: tuple[int, ...], query: int, words: int) -> int | None:
    sequence = context + tuple(words + bit for bit in query_bits(query, bits_needed(words)))
    matches = [position for position, token in enumerate(context) if token == query]
    if not matches:
        return None
    return sequence[matches[-1] + 1]


def hybrid_output(context: tuple[int, ...], query: int, words: int) -> tuple[int, float]:
    word_bits = bits_needed(words)
    bit_suffix = query_bits(query, word_bits)
    decoded_query = decode_query(bit_suffix)
    if decoded_query != query:
        raise RuntimeError("Mamba prefix-state decoder changed")
    sequence = context + tuple(words + bit for bit in bit_suffix)
    target = oracle(context, query, words)
    if target is None:
        raise ValueError("recall target is undefined when the query word is absent")

    # First attention: deterministic previous/current pairing. Second
    # attention: word-code match plus a small recency bias, all multiplied by
    # a finite temperature that gives the last match more than half the mass.
    candidates = [(sequence[index - 1], sequence[index], index) for index in range(1, len(sequence))]
    relative_bias_step = 1.0 / (len(sequence) + 1)
    temperature = (len(sequence) + 1) * (
        1.0 + math.log(max(1, len(candidates) - 1))
    )
    query_code = code(query, word_bits)
    raw_scores = []
    for previous, _, position in candidates:
        similarity = (
            dot(query_code, code(previous, word_bits))
            if previous < words
            else -word_bits
        )
        raw_scores.append(similarity + position * relative_bias_step)
    scores = [temperature * score for score in raw_scores]
    maximum = max(scores)
    unnormalized = [math.exp(score - maximum) for score in scores]
    denominator = sum(unnormalized)
    weights = [weight / denominator for weight in unnormalized]
    match_indices = [
        index for index, (previous, _, _) in enumerate(candidates) if previous == query
    ]
    selected = match_indices[-1]
    target_weight = weights[selected]

    vocabulary_size = words + 2
    value_width = bits_needed(vocabulary_size)
    attended = tuple(
        sum(
            weight * code(current, value_width)[coordinate]
            for weight, (_, current, _) in zip(weights, candidates)
        )
        for coordinate in range(value_width)
    )
    logits = [
        dot(attended, code(token, value_width))
        for token in range(vocabulary_size)
    ]
    prediction = max(range(vocabulary_size), key=lambda token: logits[token])
    return prediction, target_weight


def construction_checks(words: int, window: int) -> dict:
    word_bits = bits_needed(words)
    direct_cases = 0
    direct_correct = 0
    minimum_target_weight = 1.0

    if words == 2:
        contexts = itertools.product(range(words), repeat=window)
        for context in contexts:
            for query in range(words):
                direct_cases += 1
                expected = oracle(context, query, words)
                if expected is None:
                    continue
                predicted, weight = hybrid_output(context, query, words)
                direct_correct += int(predicted == expected)
                minimum_target_weight = min(minimum_target_weight, weight)
    else:
        for query in range(words):
            other = (query + 1) % words
            contexts = [
                (query,) + (other,) * (window - 1),
                (other,) * (window - 1) + (query,),
                (query,) * window,
            ]
            for context in contexts:
                direct_cases += 1
                expected = oracle(context, query, words)
                predicted, weight = hybrid_output(context, query, words)
                direct_correct += int(predicted == expected)
                minimum_target_weight = min(minimum_target_weight, weight)

    return {
        "direct_cases": direct_cases,
        "direct_correct_when_defined": direct_correct,
        "minimum_target_attention_weight": minimum_target_weight,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--word-vocabulary", type=int, default=2)
    parser.add_argument("--below-threshold-control", action="store_true")
    args = parser.parse_args()
    words = args.word_vocabulary
    if words < 2 or words & (words - 1):
        raise SystemExit(2)

    calibrated_window, visited = first_hit(words)
    if args.below_threshold_control:
        tested_window = calibrated_window - 1
        probability = success_fraction(words, tested_window)
        output = {
            "control": "one word slot below the calibrated first hit",
            "word_vocabulary": words,
            "tested_context_window": tested_window,
            "success_numerator": probability.numerator,
            "success_denominator": probability.denominator,
            "success_probability": float(probability),
            "target_probability": float(TARGET),
            "meets_target": probability >= TARGET,
        }
        print(json.dumps(output, sort_keys=True))
        return 0 if probability >= TARGET else 9

    probability = success_fraction(words, calibrated_window)
    previous = success_fraction(words, calibrated_window - 1)
    checks = construction_checks(words, calibrated_window)
    word_bits = bits_needed(words)
    vocabulary_size = words + 2
    sequence_length = calibrated_window + word_bits
    token_bits = bits_needed(vocabulary_size)
    position_bits = bits_needed(sequence_length)
    embedding_dimension = 3 * token_bits + 2 * position_bits + 2
    total_joint_inputs = words ** (calibrated_window + 1)
    successful_joint_inputs = words * (
        words**calibrated_window - (words - 1) ** calibrated_window
    )
    output = {
        "word_vocabulary": words,
        "full_vocabulary": vocabulary_size,
        "query_bits": word_bits,
        "calibration_method": "monotone doubling plus exact binary search",
        "calibration_visited_windows": visited,
        "minimum_context_window": calibrated_window,
        "previous_window": calibrated_window - 1,
        "success_numerator": probability.numerator,
        "success_denominator": probability.denominator,
        "success_probability": float(probability),
        "previous_success_probability": float(previous),
        "target_probability": float(TARGET),
        "total_joint_inputs": total_joint_inputs,
        "successful_joint_inputs": successful_joint_inputs,
        "attention_window": calibrated_window + word_bits + 1,
        "mamba_reachable_prefix_states": 2 * words - 1,
        "embedding_dimension": embedding_dimension,
        "dimension_upper_bound": 5 * max(token_bits, position_bits) + 2,
        "calibrated_window_linear_bound": math.ceil(words * math.log(100)) + 1,
        **checks,
    }
    print(json.dumps(output, sort_keys=True))
    direct_expected = successful_joint_inputs if words == 2 else checks["direct_cases"]
    direct_ok = (
        checks["direct_correct_when_defined"] == direct_expected
        if words == 2
        else checks["direct_correct_when_defined"] == checks["direct_cases"]
    )
    return 0 if probability >= TARGET and previous < TARGET and direct_ok else 10


if __name__ == "__main__":
    raise SystemExit(main())
