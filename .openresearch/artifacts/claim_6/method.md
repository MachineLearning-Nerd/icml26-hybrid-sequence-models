# Claim 6 method: Figure 6 MKAR stage

This node directly executes the authors' copied task generator and
GPTNeoX/Mamba implementation. It sweeps the exact hidden dimensions
4/8/12/16/20/24 for all four two-layer architectures.

For every model point, four source-neighborhood learning rates
0.001/0.0031622776601683794/0.01/0.03162277660168379 are compared on two disjoint 1,000-step
calibration seeds. Selection is by highest held-out valid-token accuracy,
then lowest training loss. The chosen rate is then trained for 4,000 steps on
11 independent final seeds. Every seed is evaluated on 1,024 newly generated
held-out sequences rather than the public evaluator's single eight-sequence
batch.

The primary statistic is the independently computed first point in the
precommitted grid reaching mean accuracy 0.60. The pure-Transformer to
SSM-to-TF parameter ratio is computed from instantiated, trainable parameter
counts. This is a finite-grid claim and not an asymptotic lower bound.

A negative control trains the SSM-to-TF d=12 model on randomized valid-token
labels. It must remain below 0.25 clean-target accuracy. All jobs run in
separate spawned processes with one Torch thread each.

The recovery run estimates six required cores: six one-thread workers, each
recycled after one training job to avoid persistent PyTorch process state.
Selected compute remains Hugging Face `cpu-upgrade`, whose current documented
allocation is 8 vCPU and 32 GB; two vCPUs are intentionally left as process
spawn and orchestration headroom. The preceding eight-worker attempt is
retained as a historical stalled run and is not accepted as scientific
evidence. Runtime is uncertain and expected to take multiple hours, so local
execution is prohibited by the campaign compute contract.

## Accepted run and static replay

The accepted run used Git SHA
`133ddebd7a6888bde8abe4e511e09a966a506828`, Hugging Face
`cpu-upgrade`, and image
`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`. The cgroup exposed 8.0 CPUs;
the experiment used six one-thread workers and took 14,432.196 seconds
(4 h 00 min 32 s). It completed 192 calibration jobs, 264 final jobs, and one
random-target control.

The static checker does not trust stored aggregates. It validates the complete
paper table transcription, instantiates all 24 models to recompute trainable
parameter counts, checks token accuracies from integer counts, rebuilds every
11-seed mean and interval, and recomputes the two first-hit points and their
ratio. A mutation that changes only the stored ratio to 6.0 must exit nonzero.
