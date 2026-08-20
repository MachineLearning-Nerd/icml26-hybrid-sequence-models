# Environment and reproduction boundary

## Locked environment

- Python: 3.12, pinned by .python-version
- Dependency lock: uv.lock
- Torch source: CPU index in pyproject.toml
- Scientific entrypoint: scripts/run_reproduction.py
- Fixed cumulative command:

  uv run --frozen --no-dev python scripts/run_reproduction.py

The theorem and construction checks are CPU-suitable. Claims 5 and 6 used
CPU-only worker runs with explicit calibration and final seeds. The final
repository verifier is static and does not silently rerun the expensive
training sweeps.

## What the cumulative runner checks

- Claim 1 theorem/cardinality calibration and its counterexample control.
- Claim 2 sliding-window witness family and negative control.
- Claim 3 symbolic construction and complete finite-domain checks.
- Claim 4 exact probability calibration and construction checks.
- Claim 5 learned selective-copy frontier, source comparison, paired seeds,
  and random-target control.
- Claim 6 full Figure 6 parameter grid, source/task correction, and
  random-target control.
- Protected historical Space manifest and release-candidate gates.

## Reproduction limits

The local evidence is not a new ICML judge result. Figure 5’s full
three-layer widths 384 and 768 were not rerun because they were not defensible
within the CPU-only campaign budget. The Claim 5 strict separation route is
marked BLOCKED rather than promoted to a universal theorem. See
CLAIM_EVIDENCE.md for the exact scope of every verdict.

