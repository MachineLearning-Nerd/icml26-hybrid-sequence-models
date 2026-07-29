# Current verification

pages/current/images/claim6_mkar_frontier.svg

The strongest empirical result is Claim 6. On the complete Figure 6 grid, the
SSM→Transformer hybrid first reaches 0.60 mean accuracy at 3,684 parameters
(mean 0.672583; normal across-seed 95% interval 0.452239–0.892928). The pure
Transformer first reaches it at 7,100 parameters (mean 0.752170; interval
0.682745–0.821596). The independently recomputed ratio is **1.927253×, not
6×**.

pages/current/images/campaign_overview.svg

## What was tested

The campaign directly audits two lower bounds, two constructive theorems, and
two learned-model figures. Universal claims are accepted only through a
symbolic certificate, complete stated finite domain, or valid
assumption-satisfying counterexample. Learned-model claims use disjoint
calibration/final seeds, held-out evaluation, instantiated parameter counts,
and controls.

| Claim | Result | Central numerical evidence |
|---|---|---|
| 1 | FALSIFIED/HIGH | For every tested injective family, m log|V| − q log|Y| = 0; a singleton-state predictor reaches the theorem's 1/2 threshold. |
| 2 | VERIFIED/MEDIUM | Eight witnesses; W/R ranges from 0.5 to 0.969; maximum uniform-pair accuracy exactly 0.5 < 2/3. |
| 3 | VERIFIED/MEDIUM | 6,266/6,266 defined inputs correct; minimum target attention mass 0.880797. |
| 4 | VERIFIED/MEDIUM | At W=2, K=7 gives 127/128=0.992188 while K−1 gives 63/64=0.984375. |
| 5 | FALSIFIED/MEDIUM | 2,192p hybrid 0.999985; 10,608p TF 0.846271; 13,488p SSM 0.866493. |
| 6 | FALSIFIED/HIGH | 3,684p hybrid versus 7,100p TF first hits; ratio 1.927253; random-target accuracy 0.0. |

## Learned-model results

pages/current/images/claim5_selective_copy.svg

Claim 5 preserves the paper's qualitative ordering, but not the imported
contract. The paper table itself reports 0.999 for the hybrid and only
0.923/0.931 for pure TF/SSM, calling those values “around 0.9.” The faithful
11-seed rerun obtains 0.999985 versus 0.846271/0.866493. Its calibrated 0.90
first-hit ratios are 8.32× and 9.61×, not exactly 6×.

Claim 6 runs all four two-layer families at dimensions 4/8/12/16/20/24 with
11 final seeds per point after disjoint learning-rate calibration: 192
calibration jobs, 264 final jobs, and one random-target control. The accepted
HF CPU run took 14,432.196 seconds.

## Theorem evidence

pages/current/images/theorem_calibration.svg

Claim 1's imported linear-in-m conclusion conflicts with the theorem's own
injection assumption. Claim 2's reconstructed proof works under the exact
final-suffix dependency premise asserted in the paper, though the paper never
formally defines sliding-window indexing.

pages/current/images/construction_coverage.svg

Claim 3 is exact on every source-defined sequence in five complete finite
domains. Claim 4 calibrates the first 99% hit with exact rational arithmetic
for power-of-two word vocabularies 2 through 64 and verifies the construction
exhaustively at vocabulary 2.

## Limits that remain visible

- Claim 3's source target is undefined on number-free inputs; those 82 inputs
  are audited and excluded.
- Claim 4 needs an explicit uniform-word distribution and power-of-two word
  vocabulary because the source wording is inconsistent.
- Claim 5 uses three seeds at non-headline frontier points and 11 at headline
  points.
- Claim 6's hybrid threshold point is seed-variable.
- Figure 5's full three-layer dimensions 384/768 were not rerun on CPU; no
  smaller proxy is presented as full-scale evidence.

Use [Claim-by-claim evidence](#/claims) for contracts, code, raw data, and
controls. These verdicts are not live judge points.
