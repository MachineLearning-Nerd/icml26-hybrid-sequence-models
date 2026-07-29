# Claim 1 — Theorem 3.3 state lower bound

**Verdict: FALSIFIED. Confidence: HIGH.**

## Exact claim and source contract

Imported claim: “Theorem 3.3 proves that any k-layer state-space model solving
the function-composition tasks under injectivity conditions must have total
log state-space size scaling as Ω(m log|V| − q log|Y|), linear in the hidden
dimension m.”

Source anchors: `sections/func_comp_and_construct.tex:26-28` and appendix proof
lines 62–75 in the retrieved arXiv source. The source archive SHA-256 is
`e8d22bfd259aaa60385841d8643109ecb66f7eb1081dd76429f5215f05a032e8`.

Assumptions and exact quantifier:

- F maps V^m × V^n to Y.
- A q-query map G(u)=(F(u,v1),...,F(u,vq)) is injective from V^m to Y^q.
- The theorem asserts an existential hard distribution and success probability
  exactly 1/2.
- The imported conclusion additionally calls the displayed bound linear in m.

## Independent derivation and numerical audit

Injectivity gives |Y|^q ≥ |V|^m. Taking logs gives
q log|Y| ≥ m log|V|, so the displayed argument
m log|V| − q log|Y| is never positive. The checker exhaustively enumerates
coordinate encodings:

| |V| | m range | q | Domain configurations | Printed RHS |
|---:|---:|---:|---:|---:|
| 2 | 1–6 | m | 2–64 | 0 bits |
| 4 | 1–6 | 2m | 4–4,096 | 0 bits |
| 8 | 1–4 | 3m | 8–4,096 | 0 bits |

At binary output and success threshold 1/2, one of the two constant labels has
probability at least 1/2 under every distribution. A singleton-state model
therefore reaches the exact threshold. The printed inequality remains
formally vacuous; the imported positive linear-in-m consequence is false.

## Executable evidence

```text
uv run --frozen --no-dev python reproduction/claim1_verifier.py
```

- [Verifier source](../../../reproduction/claim1_verifier.py)
- [Independent checker source](../../../reproduction/claim1_checker.py)
- [Exact contract](../../../.openresearch/artifacts/claim_1/claim_contract.json)
- [Raw cardinality grid](../../../.openresearch/artifacts/claim_1/raw/cardinality_grid.csv)
- [Counterexample family](../../../.openresearch/artifacts/claim_1/raw/counterexample_family.json)
- [Frozen checker output](../../../.openresearch/artifacts/claim_1/checker_output.json)
- [Source audit](../../../.openresearch/artifacts/claim_1/source_audit.md)
- [Method](../../../.openresearch/artifacts/claim_1/method.md)

Mutation control: delete a coordinate required for injectivity. It becomes
non-injective and exits **4**, as recorded in
[negative-control output](../../../.openresearch/artifacts/claim_1/negative_control_output.json).

## Environment, provenance, and limits

Fixed cumulative command:

```text
uv run --frozen --no-dev python scripts/run_reproduction.py
```

Environment: Python 3.12; `uv`; root `pyproject.toml` and `uv.lock`; one
repository `.venv`; no stochastic seeds. Git SHA:
`fedeec5acb73402a70fcf2aab2ba5e94931a61bd`. Formal run: local CPU, one
scientific process/core estimate, 10 seconds end-to-end, 0.521337-second
verifier.

Limit: this verdict targets the imported claim's positive linear consequence,
not the syntactically true but non-positive displayed Ω expression.
