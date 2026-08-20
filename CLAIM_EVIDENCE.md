# Claim-to-evidence ledger

The six claims below are frozen in the per-claim contracts under
.openresearch/artifacts/claim_N/claim_contract.json. Each verdict is scoped to
the wording, assumptions, and evidence route shown here.

| Claim | Paper or imported statement | How the result is produced | Evidence and controls | Status |
| --- | --- | --- | --- | --- |
| C1 — state lower bound | Theorem 3.3 is imported as a positive lower bound linear in hidden dimension m. | Check the theorem’s injectivity cardinality condition, inspect the Fano success threshold, and run the cardinality grid plus a constant-state binary-output counterexample. | .openresearch/artifacts/claim_1/checker_output.json, raw/cardinality_grid.csv, raw/counterexample_family.json, negative_control_output.json | FALSIFIED_SCOPED, HIGH |
| C2 — sliding-window lower bound | Theorem 3.7 requires total window size at least dependency range R. | Construct pairs with equal final-R suffixes and different labels; a predictor with total window below R sees identical observations. | .openresearch/artifacts/claim_2/checker_output.json, raw/witness_grid.csv, negative_control_output.json | VERIFIED_SCOPED, MEDIUM |
| C3 — selective-copy construction | Theorem 4.3 gives a two-layer Mamba-plus-attention construction with logarithmic embedding and O(N) attention window. | Run the symbolic resource/correctness certificate and exhaust every defined input in five finite domains. | .openresearch/artifacts/claim_3/checker_output.json, raw/complete_domain_sweep.csv, raw/construction_spec.json, raw/pure_transformer_witness.json, negative_control_output.json | VERIFIED_SCOPED, MEDIUM |
| C4 — associative recall construction | Theorem 4.6 gives a three-layer construction reaching 99% decoded associative recall. | Calibrate the first context window whose exact success probability is at least 0.99, verify the previous window is below target, then check the finite construction. | .openresearch/artifacts/claim_4/checker_output.json, raw/window_calibration_spec.csv, raw/construction_spec.json, negative_control_output.json | VERIFIED_SCOPED, MEDIUM |
| C5 — selective-copy parameter gap | A learned hybrid at about 2,000 parameters matches pure models at about 12,000, implying a 6× gap. | Compare the source table, run 11-seed paper-neighborhood models, calibrate first hits at 0.90, and use paired-seed and random-target controls. | .openresearch/artifacts/claim_5/checker_output.json, raw/frontier_results.json, static_replay_output.txt, negative_control_output.json | FALSIFIED_SCOPED, MEDIUM |
| C6 — multi-key parameter gap and Figure 5 wording | The hybrid reaches 60% multi-key recall with 6× fewer parameters, while Figures 5–6 support a single-key plateau. | Audit the source’s task split, complete the 24-point Figure 6 grid with 11 final seeds per point, count instantiated parameters, and run a random-target control. | .openresearch/artifacts/claim_6/checker_output.json, raw/figure6_full_evidence.json, negative_control_output.json | FALSIFIED_SCOPED, HIGH |

## What each verdict means

### Claim 1

The source proof’s injectivity assumption already implies
q log|Y| ≥ m log|V|, so the displayed asymptotic lower-bound term is
non-positive. The source proof also invokes an error below 1/8, which is
success above 7/8 rather than the theorem’s stated 1/2. In the checker’s
m=4, |V|=4, |Y|=2, q=8 case, the printed right-hand side is zero and a
constant-state binary-output model reaches exactly 1/2 on the balanced
distribution. The verdict rejects the imported positive linear consequence;
it does not claim that every displayed inequality in the paper is false.

### Claim 2

For length 17 and dependency range R=8, three windows have total size 7.
The constructed inputs share their final R-token suffix but have different
targets, so every deterministic predictor has maximum accuracy 0.5 on the
uniform pair, below the 2/3 target.

### Claim 3

The corrected finite-temperature selective-copy construction is checked on
6,266 defined inputs across five complete finite domains; all 6,266 pass.
The same route records 82 undefined no-number inputs, which are not silently
counted as successes. The finite certificate reports embedding dimension 9,
three reachable Mamba states, and attention window 2 in its smallest
checker case.

### Claim 4

Exact rational calibration finds context window 7 with success probability
127/128 = 0.9921875, while window 6 reaches only 0.984375. The direct
finite construction is correct on all 254 defined cases out of 256 joint
inputs. The source’s theorem label has a selective-copying typo; its
definition, section, proof restatement, and construction identify the
audited task as associative recall with decoding.

### Claim 5

The paper table reports 0.999 for the approximately 2,000-parameter hybrid,
0.923 for the approximately 12,000-parameter pure Transformer, and 0.931
for the pure SSM. The independent 11-seed means are 0.999985 for the hybrid,
0.846271 for the pure Transformer, and 0.866493 for the pure SSM. Calibrated
first-hit ratios relative to the 2,192-parameter hybrid are 8.321× and
9.606×, not 6×. The checker retains the strict route as BLOCKED because a
finite converged sweep cannot prove an asymptotic separation; the source and
calibrated evidence still falsify the stronger imported wording.

### Claim 6

The imported statement conflates two tasks. Figure 5 is associative recall
with a five-bit decoded control variable and full widths 384 and 768 were not
rerun on CPU. Figure 6 is multi-key associative recall. The complete
24-point by 11-seed rerun reaches the 0.60 threshold at 3,684 parameters for
SSM-to-Transformer and 7,100 for pure Transformer, a pure-to-hybrid ratio of
1.927×. The random-target control is 0.0 accuracy. This falsifies the exact
imported composite without making a claim about behavior outside the finite
grid.

## Evidence ladder

1. The arXiv HTML source and e-print are pinned by SHA-256 in SOURCE_AUDIT.md.
2. Each claim has a source audit, contract, method, raw output, independent
   checker, and negative control.
3. Symbolic proofs and exhaustive finite domains support universal claims only
   within their stated domains; a finite training sweep is not an asymptotic
   theorem.
4. The historical 0/12 Space contents remain available under
   space/historical/judged_revision and the protected release metadata.

