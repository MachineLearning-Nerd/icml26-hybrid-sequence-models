# Claim 5 — Figure 4 learned selective copying

**Verdict: FALSIFIED. Confidence: MEDIUM.**

## Exact imported claim and paper result

Imported claim: “On selective copying, a learned hybrid reaches perfect
accuracy with roughly 2,000 parameters while pure Transformer/SSM models need
roughly 12,000 parameters to match it, a 6× parameter gap.”

Source anchors: `sections/experiments.tex:26-49` and
`appendix/experiment_details.tex:3-19`. Source archive SHA-256:
`e8d22bfd259aaa60385841d8643109ecb66f7eb1081dd76429f5215f05a032e8`.
Official code SHA:
`7beeb0de80f89eb5d75301aef8e97ee9b36ca999`.

The source's own Figure 4 table is:

| Family | Rounded parameters | Paper accuracy |
|---|---:|---:|
| SSM→TF | ~2,000 | 0.999 |
| TF→TF | ~12,000 | 0.923 |
| SSM→SSM | ~12,000 | 0.931 |

The caption says the pure models reach “around 0.9,” not that they match the
perfect hybrid. The imported contract is stronger than the source.

## Faithful rerun contract

Length 100; vocabulary 26; five number tokens; two-layer GPTNeoX/Mamba
families; one attention head; causal window 20; RoPE; effective Mamba state
size 16 (required to reproduce saved parameter counts); AdamW; 100-step
warmup; linear decay; seq-to-seq valid-token accuracy.

Learning rate is chosen from source-neighborhood values on calibration seeds
260350001–260350002. Headline means use independent seeds
260352001–260352011; frontier points use 260351001–260351003. Every seed is
evaluated on fresh held-out sequences.

## Raw observed results

| Model | Exact parameters | Mean accuracy | Normal across-seed 95% interval | 10th–90th percentile |
|---|---:|---:|---:|---:|
| SSM→TF | 2,192 | 0.999985 | 0.999970–1.000000 | 0.999945–1.000000 |
| TF→TF | 10,608 | 0.846271 | 0.793941–0.898602 | 0.868155–0.874724 |
| SSM→SSM | 13,488 | 0.866493 | 0.710093–1.000000 | 0.664958–0.999973 |

Exact paired one-sided sign-test p-values are below 0.05 for the hybrid against
each pure family. Independently calibrated first points with mean accuracy at
least 0.90 are:

| Family | Parameters | Ratio to hybrid |
|---|---:|---:|
| SSM→TF | 2,192 | 1.00× |
| TF→TF | 18,240 | 8.32× |
| SSM→SSM | 21,056 | 9.61× |

The qualitative hybrid advantage is corroborated. The imported “match
perfect” and exact 6× contract is not.

## Executable evidence

```text
uv run --frozen --no-dev python reproduction/claim5_verifier.py
```

- [Verifier](../../../reproduction/claim5_verifier.py)
- [Independent checker](../../../reproduction/claim5_checker.py)
- [Training implementation](../../../reproduction/figure_training.py)
- [Exact contract](../../../.openresearch/artifacts/claim_5/claim_contract.json)
- [Full frontier raw JSON](../../../.openresearch/artifacts/claim_5/raw/frontier_results.json)
- [Checker output](../../../.openresearch/artifacts/claim_5/checker_output.json)
- [Source audit](../../../.openresearch/artifacts/claim_5/source_audit.md)
- [Frontier method](../../../.openresearch/artifacts/claim_5/frontier_method.md)
- [Commands](../../../.openresearch/artifacts/claim_5/commands.md)

Random-target negative control, seed 260359999: token accuracy 0.041856 and
exact-sequence accuracy 0.0. The independent evidence mutation also exits
nonzero. See [control output](../../../.openresearch/artifacts/claim_5/negative_control_output.json).

## Environment, provenance, and limits

Fixed command:
`uv run --frozen --no-dev python scripts/run_reproduction.py`.
Python 3.12; frozen `uv.lock`; one root `.venv`. Scientific Git SHA
`d0e944e3008518a793074cf40afd7fce0566f9c1`. Hugging Face
`cpu-upgrade` exposed 8.0 CPUs; eight one-thread workers were used.
Scientific runtime 6,183.510 seconds; fixed-command runtime 6,197.443 seconds.

Limitations: no paper seeds or numerical convergence rule exist; the
four-rate calibration is narrower than the paper's nine-rate list; non-
headline frontier points use three seeds; state-size and public evaluator
quirks are corrected transparently. FALSIFIED applies to the exact imported
wording, not the paper's actual qualitative ordering.
