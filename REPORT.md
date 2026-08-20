# Audit report

## Executive result

Claims 2–4 pass their scoped theorem or construction contracts. Claims 1, 5,
and 6 are falsified under the exact imported contracts. The historical
external result is 0/12; no current score is claimed.

Overall status:

PARTIAL_C2_C4_VERIFIED_C1_C5_C6_FALSIFIED_HISTORICAL_SCORE_0_OF_12_NO_CURRENT_SCORE

| Claim | Result | Primary route | Main boundary |
| --- | --- | --- | --- |
| C1 | FALSIFIED_SCOPED | Injectivity/cardinality audit and constant-state binary-output counterexample | Rejects the imported positive linear consequence; does not reject every printed inequality. |
| C2 | VERIFIED_SCOPED | Eight-case sliding-window witness grid | Uses the paper’s stated suffix-indistinguishability assumption and a finite witness family. |
| C3 | VERIFIED_SCOPED | Corrected finite-temperature construction and five complete finite domains | Universal source wording is supported only over the defined domains and certificate assumptions. |
| C4 | VERIFIED_SCOPED | Exact first-hit probability calibration and finite construction | The theorem label typo and absent-query accounting are disclosed. |
| C5 | FALSIFIED_SCOPED | Source table plus 11-seed selective-copy rerun and calibrated parameter frontier | Strict asymptotic separation remains blocked; the stronger imported numerical wording is contradicted. |
| C6 | FALSIFIED_SCOPED | Complete Figure 6 grid and task-identity audit | Figure 5 full scale remains unrun; Figure 6 ratio is 1.927× rather than 6×. |

## Key numbers

- C1: printed right-hand side 0 bits; best constant-state success 0.5.
- C2: total window 7 below R=8; maximum witness-pair accuracy 0.5 versus
  target 2/3.
- C3: 6,266 of 6,266 defined finite inputs pass; 82 additional inputs are
  undefined because they contain no number token.
- C4: minimum context window 7; success 127/128 = 0.9921875; previous window
  success 0.984375.
- C5: hybrid mean 0.999985; pure Transformer mean 0.846271; pure SSM mean
  0.866493; calibrated first-hit ratios 8.321× and 9.606×.
- C6: first 0.60 hits at 3,684 hybrid parameters and 7,100 pure Transformer
  parameters; ratio 1.927×; random-target accuracy 0.0.

## Score and publication boundary

- Historical live score: 0/12
- Current score claim: false
- Publication allowed: false
- Official author endorsement: false / not claimed

The original 0/12 judged revision is retained under
space/historical/judged_revision. The current evidence package is an
independent audit maintained by MachineLearning-Nerd.

