# Claim 5 CPU fidelity pilot

This node is a timing and implementation-fidelity pilot, not accepted Claim 5
evidence. Claim 5 remains `BLOCKED`.

The run uses the fixed cumulative command and the authors' audited GPTNeoX,
Mamba, selective-copy generator, masked seq-to-seq loss, AdamW, 100-step
warmup, and 4000-step linear-decay schedule. It stops after 200 steps to
measure CPU throughput. It runs the approximately-2k SSM→TF model (`d=8`) with
the Figure setup: length 100, window 20, 26 word tokens, five number tokens,
nominal state size 1, batch size 8, and deterministic seed `260308859`.

The selected effective Mamba state size is 16 despite the saved run identifier
ending in `sd1`: the authors' saved Figure 6 notebook reports exactly 11,496
parameters for SSM→TF, `d=24`, vocabulary size 11. At expansion 2,
reconstructing the model gives 9,336 with state size 1 and exactly 11,496 with
the model default state size 16. The two-SSM count independently differs by
twice the same increment. The Figure-effective approximately-2k model
therefore has 2,192 parameters. The run prints the calibration.

Compute estimate before launch: 8 scientific CPU threads, uncertain runtime,
Hugging Face `cpu-upgrade`,
`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`, timeout 3600 seconds.
The run prints the actual visible CPU count, affinity, configured Torch
threads, and wall-clock runtime.

Acceptance criterion for this pilot: the upstream model completes forward and
backward passes, the count calibration is exact, all Claims 1–4 regressions
pass, and measured throughput supports a defensible full-run plan. No accuracy
threshold is used because 200 steps is not the paper's converged regime.
