# Claim 6 evaluator record

## Result

**FALSIFIED (HIGH confidence)** for the exact imported composite.

The paper reports a sixfold parameter advantage at 60% mean accuracy in
Figure 6. The complete 24-point, 11-seed-per-point rerun first reaches 60% at:

| Family | Point | Parameters | Mean accuracy | Normal 95% interval across seeds |
|---|---:|---:|---:|---:|
| SSM-to-Transformer hybrid | d=12 | 3,684 | 0.672583 | 0.452239--0.892928 |
| Pure Transformer | d=20 | 7,100 | 0.752170 | 0.682745--0.821596 |

The independently recomputed pure-to-hybrid ratio is **1.927253x**, not 6x.
The random-target control obtains 0/46,392 correct valid tokens (accuracy
0.0). Separately, the imported phrase “single-key associative recall” does
not describe Figure 5; that figure is associative recall with a five-bit
decoded control variable.

## Reproduce the evidence check

```text
uv run --frozen --no-dev python reproduction/claim6_verifier.py
```

The fixed cumulative command is:

```text
uv run --frozen --no-dev python scripts/run_reproduction.py
```

The mutation control must fail:

```text
uv run --frozen --no-dev python reproduction/claim6_verifier.py --negative-control
```

Expected exit code: 4.

## Evidence

- Raw accepted run: `raw/figure6_full_evidence.json`
- Independent recomputation: `checker_output.json`
- Frozen mutation-control result: `negative_control_output.json`
- Claim contract: `claim_contract.json`
- Source transcription: `source_audit.md`
- Method and deviations: `method.md`, `limitations.md`

Raw JSON SHA-256:
`25755755c56affbbf5b0e37c6d8619b3ed3191fe72fc16aae2f6f519918893c7`.
Accepted run Git SHA:
`133ddebd7a6888bde8abe4e511e09a966a506828`.
The accepted Hugging Face `cpu-upgrade` allocation exposed 8.0 CPUs; six
one-thread workers were used. Runtime was 14,432.196 seconds
(4 h 00 min 32 s). The static verifier uses one local CPU core and finishes
in seconds.

## Scope

Figure 5 was not rerun through the paper's three-layer dimensions 384 and 768;
that is not feasible within this CPU-only campaign. No reduced Figure 5 proxy
is used as full-credit evidence. The verdict applies to the exact imported
composite and the faithful finite Figure 6 contract; it does not establish
behavior outside that grid.
