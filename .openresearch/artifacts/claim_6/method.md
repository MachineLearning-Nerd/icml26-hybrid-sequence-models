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

Estimated allocation is 8 cores: eight one-thread workers. Selected compute is
Hugging Face `cpu-upgrade`, whose current documented allocation is 8 vCPU and
32 GB. Runtime is uncertain and expected to take multiple hours, so local
execution is prohibited by the campaign compute contract.
