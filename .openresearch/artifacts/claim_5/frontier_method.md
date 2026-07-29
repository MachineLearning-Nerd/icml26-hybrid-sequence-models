# Claim 5 selective-copy parameter frontier

This run tests Figure 4 with the authors' audited architecture and generator.
It does not choose a sample size or parameter point from the claimed 6×
formula.

For each of 12 architecture/width points, three neighboring learning rates
(`0.0031623`, `0.01`, `0.0316228`) are independently calibrated by the lowest
mean 1,000-step loss over two deterministic seeds. Each point is then trained
for the paper's 4,000 steps. Three seeds establish the resource frontier;
the four Figure headline points use 11 disjoint seeds. Final evaluation uses
2,048 fixed held-out sequences per seed and reports token accuracy, a 95%
interval across seeds, and the paper's 10th/90th percentiles.

The finite 90%-accuracy first hit is measured across:

- SSM→TF: dimensions 4, 8, 12;
- TF→TF: dimensions 16, 20, 24, 32;
- SSM→SSM: dimensions 16, 20, 24, 32;
- TF→SSM at dimension 8 as the order control.

A separately trained SSM→TF model receives independent random targets at
every valid training token, then is evaluated on the real held-out task. It
must remain below 20% accuracy. The cumulative runner also reruns Claims 1–4
and their negative controls.

Compute estimate before corrected launch: eight spawned workers × one Torch
thread = eight scientific CPU cores on Hugging Face `cpu-upgrade` (8 vCPU,
32 GB); runtime uncertain and expected above five minutes; timeout 14,400
seconds. The initial 8×8 launch was cancelled before any accepted result after
the allocation audit showed that the container exposed 64 host CPUs but the
selected flavor enforces eight vCPUs. Every worker records its seed, learning
rate, exact parameters, runtime, Torch threads, cgroup quota, visible affinity,
losses, learning curve, and raw held-out counts.
