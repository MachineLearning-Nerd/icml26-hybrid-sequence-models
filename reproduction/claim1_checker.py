#!/usr/bin/env python3
"""Independent exhaustive checker for the Claim 1 counterexample family."""

from __future__ import annotations

import argparse
import itertools
import json
import math


def symbol_bits(symbol: int, width: int) -> tuple[int, ...]:
    return tuple((symbol >> shift) & 1 for shift in reversed(range(width)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m", type=int, required=True)
    parser.add_argument("--alphabet-bits", type=int, default=2)
    parser.add_argument("--drop-last-control", action="store_true")
    args = parser.parse_args()

    if args.m < 1 or args.alphabet_bits < 1:
        raise SystemExit(2)
    vocabulary_size = 2**args.alphabet_bits
    q = args.m * args.alphabet_bits - int(args.drop_last_control)
    domain = itertools.product(range(vocabulary_size), repeat=args.m)
    images: set[tuple[int, ...]] = set()
    labels = [0, 0]
    domain_size = vocabulary_size**args.m

    for payload in domain:
        full_code = tuple(bit for symbol in payload for bit in symbol_bits(symbol, args.alphabet_bits))
        image = full_code[:q]
        images.add(image)
        for label in full_code:
            labels[label] += 1

    injective = len(images) == domain_size
    cardinality_rhs = args.m * math.log2(vocabulary_size) - q * math.log2(2)
    uniform_constant_success = max(labels) / sum(labels)
    output = {
        "m": args.m,
        "alphabet_bits": args.alphabet_bits,
        "vocabulary_size": vocabulary_size,
        "output_size": 2,
        "q": q,
        "domain_size": domain_size,
        "image_size": len(images),
        "injective": injective,
        "printed_rhs_bits": cardinality_rhs,
        "uniform_label_counts": labels,
        "best_uniform_constant_success": uniform_constant_success,
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if injective else 4


if __name__ == "__main__":
    raise SystemExit(main())
