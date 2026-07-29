# Claim 6 limitations

- The paper does not publish seeds. This reproduction supplies deterministic,
  disjoint calibration and final seed sets.
- The public code's nominal state-size argument is not applied by its model
  constructor. Effective state size 16 is retained because it reproduces the
  saved parameter counts.
- The four-rate calibration is a precommitted subset of the authors'
  nine-rate sweep. It covers every learning rate selected for the relevant
  published MKAR grid according to the repository's `lrs.json`.
- The SSM-to-TF first-hit mean has substantial seed variation: its normal
  across-seed 95% interval is 0.452239--0.892928. The threshold decision is
  defined on the paper's mean-over-11-runs convention, not on every seed
  exceeding 0.60.
- A finite width sweep cannot establish an architectural lower bound outside
  the tested family.
- Figure 5 was not rerun at its full three-layer dimensions 24 through 768:
  widths 384 and 768 are not feasible in this CPU-only campaign. A reduced
  sweep would be a proxy and is not presented as full-credit evidence.
- FALSIFIED applies to the exact imported composite wording and the
  precommitted Figure 6 reproduction contract. The empirical divergence is
  not evidence that the archived paper plot was fabricated.
