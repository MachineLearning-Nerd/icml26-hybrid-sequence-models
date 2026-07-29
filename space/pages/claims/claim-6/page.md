# Claim 6 — Figures 5–6 associative recall

**Verdict: FALSIFIED. Confidence: HIGH.**

## Exact imported composite and source split

Imported claim: “On multi-key associative recall, the hybrid reaches 60%
accuracy using 6× fewer parameters than pure Transformers, which plateau near
40% accuracy on single-key associative recall (Figures 5–6).”

Figure 6 source anchors:
`sections/experiments.tex:63-91` and
`appendix/experiment_details.tex:5-19`.
It is multi-key associative recall at length 100, vocabulary 8, key length 2,
with two-layer TF/SSM/hybrid families and 11 runs.

Figure 5 source anchors:
`sections/experiments.tex:51-60`, `sections/tasks.tex:34-40`, and
`appendix/experiment_details.tex:17`.
It is **associative recall with a five-bit decoded control variable**, not
single-key associative recall. It uses three-layer models at dimensions
24–768.

Source archive SHA-256:
`e8d22bfd259aaa60385841d8643109ecb66f7eb1081dd76429f5215f05a032e8`.
Official code SHA:
`7beeb0de80f89eb5d75301aef8e97ee9b36ca999`.

## Faithful Figure 6 contract

The query is the last two tokens; the target follows their last earlier
occurrence. All four two-layer families are trained at hidden dimensions
4/8/12/16/20/24, one attention head, window 100, effective Mamba state 16,
4,000 AdamW steps. Four learning rates are chosen using calibration seeds
260360001–260360002. Final means use independent seeds
260361001–260361011 and 1,024 held-out sequences per seed.

The full grid contains 192 calibration jobs and 264 final jobs. The independent
checker reinstantiates all 24 models, verifies integer token counts, recomputes
every seed aggregate and interval, and finds the first grid point whose mean
reaches 0.60.

## Raw observed results

| Family | First ≥0.60 point | Parameters | Mean accuracy | Normal across-seed 95% interval |
|---|---:|---:|---:|---:|
| SSM→TF | d=12 | 3,684 | 0.672583 | 0.452239–0.892928 |
| TF→TF | d=20 | 7,100 | 0.752170 | 0.682745–0.821596 |

Pure-TF/hybrid parameter ratio:
**7,100 / 3,684 = 1.927253×**, versus the claimed 6×.
Pure SSM and TF→SSM never reach 0.60 within the grid.

Random-target control seed 260369999: 0/46,392 correct valid tokens,
accuracy 0.0. A separate mutation changing only the stored ratio to 6.0 exits
**4**.

## Executable evidence

```text
uv run --frozen --no-dev python reproduction/claim6_verifier.py
```

- [Verifier](../../../reproduction/claim6_verifier.py)
- [Independent checker](../../../reproduction/claim6_checker.py)
- [Training implementation](../../../reproduction/figure_training.py)
- [Exact contract](../../../.openresearch/artifacts/claim_6/claim_contract.json)
- [Full 457-job raw JSON](../../../.openresearch/artifacts/claim_6/raw/figure6_full_evidence.json)
- [Independent recomputation](../../../.openresearch/artifacts/claim_6/checker_output.json)
- [Negative-control output](../../../.openresearch/artifacts/claim_6/negative_control_output.json)
- [Source audit](../../../.openresearch/artifacts/claim_6/source_audit.md)
- [Method](../../../.openresearch/artifacts/claim_6/method.md)
- [Provenance](../../../.openresearch/artifacts/claim_6/provenance.json)

## Environment, CPU, runtime, and limits

Fixed command:
`uv run --frozen --no-dev python scripts/run_reproduction.py`.
Python 3.12; frozen `uv.lock`; one root `.venv`. Scientific Git SHA
`133ddebd7a6888bde8abe4e511e09a966a506828`. Hugging Face
`cpu-upgrade` exposed 8.0 CPUs; six one-thread workers were used.
Scientific runtime 14,432.196 seconds. The cumulative static verifier at Git
SHA `8ba5e099657cd2b61b3201daa11692736cfb083a` ran locally with a one-core
estimate in 26.024723 seconds.

The SSM→TF threshold mean is seed-variable, as its interval shows. Four
learning rates are a precommitted subset of the paper's nine-rate sweep.
Figure 5 was not rerun through three-layer dimensions 384/768 because that is
not defensible in this CPU-only campaign; no downscaled proxy is used.
FALSIFIED targets the exact imported composite and faithful finite Figure 6
contract. It does not claim the archived plot was fabricated or establish
behavior outside the tested grid.
