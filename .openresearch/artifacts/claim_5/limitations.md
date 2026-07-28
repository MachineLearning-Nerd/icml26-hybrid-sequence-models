# Claim 5 limitations and deviations

- The paper records no seeds and gives no numerical convergence rule. This
  reproduction fixes and exposes all calibration, final, evaluation, and
  control seeds and uses the public 4,000-step schedule.
- The prose and run identifiers say Mamba state dimension 1, but the saved
  Figure parameter counts are reproduced only with the implementation's
  effective default state size 16. Both nominal and effective values are
  exposed.
- The prose says number tokens 5 through 10, while the public code and Figure
  identifier use five tokens (#5 through #9). The executable code is followed.
- The official evaluator effectively checks only one batch of eight examples.
  This reproduction evaluates 2,048 fixed held-out sequences per seed.
- The calibrated 8.32x and 9.61x resource ratios are finite first hits in the
  precommitted width grid, not continuous or asymptotic minima.
- Pure-SSM optimization is highly seed-sensitive (0.129 to 1.000 at 13,488
  parameters), so the precommitted upper-interval route is BLOCKED. The final
  FALSIFIED verdict instead rests on the exact source mismatch, full mean
  results, and paired-seed tests; confidence is MEDIUM.
- CPU execution uses Transformers' sequential Mamba fallback rather than its
  optional fused GPU kernels. The model equations and trainable parameters are
  unchanged, but runtime is not comparable to the paper's hardware.
