# Claim 6 current limitations

- Claim 6 remains BLOCKED until both Figure 6 and Figure 5 stages complete and
  their frozen raw evidence passes an independent checker.
- The paper does not publish seeds. This reproduction supplies deterministic,
  disjoint calibration and final seed sets.
- The public code's nominal state-size argument is not applied by its model
  constructor. Effective state size 16 is retained because it reproduces the
  saved parameter counts.
- The four-rate calibration is a precommitted subset of the authors'
  nine-rate sweep. It covers every learning rate selected for the relevant
  published MKAR grid according to the repository's `lrs.json`.
- A finite width sweep cannot establish an architectural lower bound outside
  the tested family.
