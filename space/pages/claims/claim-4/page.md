# Claim 4 — Theorem 4.6 decoded associative recall

**Verdict: VERIFIED. Confidence: MEDIUM.**

## Exact claim, distribution, and assumptions

Imported claim: “Theorem 4.6 constructs a three-layer hybrid achieving 99%
associative-recall accuracy with embedding dimension
O(max(log|V|,log L)) and window Õ(|V|).”

Source anchors: `sections/tasks.tex:37-40`, theorem lines 59–61, and
`appendix/constructions.tex:199-201,238-327`. Source SHA-256:
`e8d22bfd259aaa60385841d8643109ecb66f7eb1081dd76429f5215f05a032e8`.

Audited distribution:

- word vocabulary W is a power of two;
- context words are iid uniform over W;
- exactly log2(W) suffix bits encode an independent uniform query;
- the target follows the query word's last context occurrence;
- absent-query contexts are conservatively counted as failures.

## Exact calibration and construction

The success probability for a K-word context is exactly
1−(1−1/W)^K. Monotone doubling plus integer binary search finds the first K
at or above 0.99 for W=2,4,8,16,32,64; K−1 is below 0.99 in every case. For
W=2, K=7:

| Window | Exact probability | Decimal | Meets 0.99 |
|---:|---:|---:|---|
| K−1=6 | 63/64 | 0.984375 | no |
| K=7 | 127/128 | 0.9921875 | yes |

The three layers decode the bit suffix into one of 2W−1 reachable prefix
states, pair each token with its successor, and retrieve the last matching
pair with finite-temperature attention. All 254 defined joint cases at W=2
are correct; all 256 cases are included in probability accounting.

## Executable evidence

```text
uv run --frozen --no-dev python reproduction/claim4_verifier.py
```

- [Verifier](../../../reproduction/claim4_verifier.py)
- [Independent checker](../../../reproduction/claim4_checker.py)
- [Contract](../../../.openresearch/artifacts/claim_4/claim_contract.json)
- [Calibration grid](../../../.openresearch/artifacts/claim_4/raw/window_calibration_spec.csv)
- [Construction specification](../../../.openresearch/artifacts/claim_4/raw/construction_spec.json)
- [Checker output](../../../.openresearch/artifacts/claim_4/checker_output.json)
- [Source audit](../../../.openresearch/artifacts/claim_4/source_audit.md)

Negative control: run one context slot below the exact first hit. It remains
below 0.99 and exits **9**:
[control output](../../../.openresearch/artifacts/claim_4/negative_control_output.json).

## Environment, provenance, and limits

Fixed command:
`uv run --frozen --no-dev python scripts/run_reproduction.py`.
Python 3.12, frozen `uv.lock`, one `.venv`, deterministic/no seeds. Git SHA
`efd023d8da4425517961e18d2c7656ff2994ad0a`; local CPU, one-core estimate,
5 seconds end-to-end, 1.689328-second verifier.

Confidence is MEDIUM because the theorem body has a task-name typo, the source
alternates between two distribution descriptions, the bit construction
implicitly needs power-of-two W, and the absent-query target is undefined.
