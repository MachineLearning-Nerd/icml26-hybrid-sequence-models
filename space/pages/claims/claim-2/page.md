# Claim 2 — Theorem 3.7 sliding-window lower bound

**Verdict: VERIFIED. Confidence: MEDIUM.**

## Exact claim and source contract

Imported claim: “Theorem 3.7 proves that sliding-window Transformers solving
the same tasks under a local-sensitivity condition require total window size
scaling with the context-dependency range R.”

Exact formal implication: if two length-L inputs agree on their final R tokens
but have different targets, every k-layer Transformer reaching accuracy at
least 2/3 on the uniform witness pair must satisfy
sum_i W_i ≥ R.

Source anchors:
`sections/func_comp_and_construct.tex:54-60` and
`appendix/missing_proof_lb.tex:88-94`. Source SHA-256:
`e8d22bfd259aaa60385841d8643109ecb66f7eb1081dd76429f5215f05a032e8`.

Assumptions:

- Two local-sensitivity witnesses share the exact R-token suffix.
- Their target labels differ.
- Under the paper proof's premise, the final output with total window W is a
  deterministic function of the final W input tokens.
- The hard distribution is uniform on the witness pair.

## Certificate and raw numbers

When W<R, both inputs induce identical observations, so every deterministic
prediction is wrong on one of the two labels: maximum accuracy 1/2 < 2/3.

| L | R | Layer windows | W | Shared suffix | Max accuracy |
|---:|---:|---|---:|---|---:|
| 8 | 3 | 1+1 | 2 | yes | 0.5 |
| 9 | 4 | 0+1+2 | 3 | yes | 0.5 |
| 12 | 5 | 2+2 | 4 | yes | 0.5 |
| 17 | 8 | 2+2+3 | 7 | yes | 0.5 |
| 24 | 10 | 1+3+2+3 | 9 | yes | 0.5 |
| 32 | 16 | 5+5+5 | 15 | yes | 0.5 |
| 50 | 20 | 0+4+0+7+8 | 19 | yes | 0.5 |
| 65 | 32 | 10+10+11 | 31 | yes | 0.5 |

## Executable evidence

```text
uv run --frozen --no-dev python reproduction/claim2_verifier.py
```

- [Verifier](../../../reproduction/claim2_verifier.py)
- [Independent checker](../../../reproduction/claim2_checker.py)
- [Exact contract](../../../.openresearch/artifacts/claim_2/claim_contract.json)
- [All raw witnesses](../../../.openresearch/artifacts/claim_2/raw/witness_grid.csv)
- [Checker output](../../../.openresearch/artifacts/claim_2/checker_output.json)
- [Source audit](../../../.openresearch/artifacts/claim_2/source_audit.md)
- [Method](../../../.openresearch/artifacts/claim_2/method.md)

Negative control: set total window at or above R. The indistinguishability
premise breaks and the control exits **5**:
[control output](../../../.openresearch/artifacts/claim_2/negative_control_output.json).

## Environment, provenance, and limits

Fixed command:
`uv run --frozen --no-dev python scripts/run_reproduction.py`.
Python 3.12; frozen `uv.lock`; one root `.venv`; deterministic, no seeds. Git
SHA `ad7ec170730798cd2f2eee19d5e2346f4a45a0ae`; local CPU; one-core estimate;
5 seconds end-to-end; 0.772692-second verifier.

Confidence is MEDIUM because the paper never formally defines causal
sliding-window masking or its indexing convention. Verification is explicitly
conditioned on the final-suffix dependency premise used by its own proof.
