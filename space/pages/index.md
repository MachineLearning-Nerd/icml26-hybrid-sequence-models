# Current verification index

This is the canonical evaluator entrypoint for the reproduction of arXiv
2603.08859. **Current verification supersedes the Historical rejected
baseline.** The current executable suite is Git revision
`8ba5e099657cd2b61b3201daa11692736cfb083a`.

The protected previous live score remains **0/12** at Space revision
`9449686999e15049fa1e258517852b9f2a00bda1`. No score increase is claimed
before a new live verdict.

## Start here

| Page | What the evaluator can verify |
|---|---|
| [Current verification](#/current) | Illustrated result summary, exact numbers, limitations, and central evidence |
| [Claim-by-claim evidence](#/claims) | Six exact contracts with source quantifiers, assumptions, code, raw data, controls, and provenance |
| [Commands and provenance](#/provenance) | Fixed command, pinned environment, Git SHAs, CPU allocation, runtime, and important branches |
| [Evaluator visibility matrix](#/visibility) | Claim-by-claim reachability audit |
| [Release forecast and gates](#/release) | Conservative score forecast, confidence table, commands, compute, and gate status |
| [Evaluator-blind review](#/red-team) | Recorded files opened, initial findings, fixes, and repeated traversal |
| [Historical rejected baseline](#/history) | Preserved 13-file judged revision, clearly demoted from current verification |

## Current verdicts

| Claim | Verdict | Confidence | One-line basis |
|---|---|---|---|
| 1 | **FALSIFIED** | HIGH | Injectivity makes the asserted positive linear lower-bound term non-positive. |
| 2 | **VERIFIED** | MEDIUM | Symbolic shared-suffix witnesses force maximum accuracy 1/2 whenever total window W<R. |
| 3 | **VERIFIED** | MEDIUM | Corrected two-layer construction is exact on 6,266 defined inputs across five complete domains. |
| 4 | **VERIFIED** | MEDIUM | Exact first-hit calibration reaches 99% and the K−1 control stays below it. |
| 5 | **FALSIFIED** | MEDIUM | Source and rerun do not support “match perfect” or an exact 6× first-hit gap. |
| 6 | **FALSIFIED** | HIGH | Complete Figure 6 rerun gives a 1.927× threshold ratio rather than 6×. |

Fixed cumulative command:

```text
uv run --frozen --no-dev python scripts/run_reproduction.py
```

Every displayed number is inline on its claim page and linked to raw CSV/JSON.
Every verifier has an independent checker or recomputation route and a control
that exits nonzero.
