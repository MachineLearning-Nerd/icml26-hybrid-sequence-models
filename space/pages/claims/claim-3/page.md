# Claim 3 — Theorem 4.3 selective copying construction

**Verdict: VERIFIED. Confidence: MEDIUM.**

## Exact claim, domain, and assumptions

Imported claim: “Theorem 4.3 constructs a two-layer hybrid (Mamba + attention)
that solves selective copying with embedding dimension
O(max(log|V|,log L)) and working memory Õ(N), versus Ω(L) for pure
Transformers.”

Source anchors: `sections/tasks.tex:4-8`, theorem lines 28–31, and
`appendix/constructions.tex:38-40,78-163`. Source SHA-256:
`e8d22bfd259aaa60385841d8643109ecb66f7eb1081dd76429f5215f05a032e8`.

Verified domain: every length-L sequence containing at least one number token;
the source argmax target is undefined on number-free inputs. Number tokens
encode distances 1...N; the most recent one controls the output; binary token
and relative-position codes are distinct.

## Construction and exhaustive audit

Layer 1 is a selective recurrence holding one of N+1 states: bottom or the
code of the most recent control distance. Layer 2 is finite-temperature causal
attention over exactly the final N tokens. Its query and relative-position key
match the desired distance; the chosen inverse temperature makes target mass
strictly above 1/2. Linear code correlation then decodes the token.

Embedding dimension is
2 ceil(log2|V|) + 2 ceil(log2 L) + 1.

| L | |V| | N | Defined inputs | Undefined audited | Accuracy |
|---:|---:|---:|---:|---:|---:|
| 4 | 4 | 2 | 240 | 16 | 1.0 |
| 5 | 3 | 1 | 211 | 32 | 1.0 |
| 5 | 4 | 2 | 992 | 32 | 1.0 |
| 6 | 3 | 2 | 728 | 1 | 1.0 |
| 6 | 4 | 3 | 4,095 | 1 | 1.0 |

Total: **6,266/6,266 defined sequences correct**. Minimum target attention
mass is 0.880797; the representative L=4,V=4,N=2 construction has 3 reachable
states, window 2, and dimension 9.

## Executable evidence

```text
uv run --frozen --no-dev python reproduction/claim3_verifier.py
```

- [Verifier](../../../reproduction/claim3_verifier.py)
- [Independent checker](../../../reproduction/claim3_checker.py)
- [Contract](../../../.openresearch/artifacts/claim_3/claim_contract.json)
- [Complete-domain CSV](../../../.openresearch/artifacts/claim_3/raw/complete_domain_sweep.csv)
- [Construction specification](../../../.openresearch/artifacts/claim_3/raw/construction_spec.json)
- [Pure-Transformer witness](../../../.openresearch/artifacts/claim_3/raw/pure_transformer_witness.json)
- [Checker output](../../../.openresearch/artifacts/claim_3/checker_output.json)
- [Source audit](../../../.openresearch/artifacts/claim_3/source_audit.md)

Negative control: zero inverse temperature destroys the strict target-mass
certificate and exits **7**:
[control output](../../../.openresearch/artifacts/claim_3/negative_control_output.json).

## Environment, provenance, and deviations

Fixed command:
`uv run --frozen --no-dev python scripts/run_reproduction.py`.
Python 3.12, frozen `uv.lock`, one `.venv`, deterministic/no seeds. Git SHA
`83a5535df35815b0e607da69774026b15292c2f7`; local CPU, one-core estimate,
5 seconds end-to-end, 1.118072-second verifier.

Visible corrections: undefined number-free inputs are excluded; the paper's
query/key index mismatch is corrected to distance-to-distance comparison; and
the checker applies a true N-token mask that the public notebook omits.
