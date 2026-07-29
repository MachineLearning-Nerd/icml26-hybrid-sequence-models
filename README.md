# Expressivity–Efficiency Tradeoffs for Hybrid Sequence Models — reproduction

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-82EJxJzG6r-expressivity-efficiency-tradeoffs-for-hybrid-sequence-models/blob/main/notebooks/hybrid_tradeoffs_tutorial.py)

This repository reproduces all six judged claims for
[arXiv:2603.08859](https://arxiv.org/abs/2603.08859): two lower bounds, two
constructive theorems, and the learned-model results in Figures 4–6. The
cumulative evidence reports Claims 2–4 **VERIFIED** and Claims 1, 5, and 6
**FALSIFIED** under their exact imported contracts. These are research
verdicts, not live judge points; the protected score remains **0/12** until the
evaluator reruns.

The evaluator-visible artifact is published to the existing
[DineshAI/82EJxJzG6r Space](https://huggingface.co/spaces/DineshAI/82EJxJzG6r/tree/f80ea6a457fe121824b86f9862ea6d6c568947f5)
at revision `f80ea6a457fe121824b86f9862ea6d6c568947f5`. A fresh download of that
revision passed the canonical-entrypoint traversal, manifest, protected-history,
secret, and six-verifier checks. It is awaiting a live judge rerun.

The strongest empirical divergence is Figure 6. The paper/imported claim gives
a 6× parameter advantage at 60% mean multi-key-recall accuracy. Across the
complete 24-point grid and 11 final seeds per point, the observed first hits
are 3,684 parameters for SSM→TF (0.672583 mean) and 7,100 for pure TF
(0.752170), a **1.927×** ratio. For Figure 4, the reproduced headline values
are 0.999985 at 2,192 hybrid parameters versus 0.846271 at 10,608 pure-TF and
0.866493 at 13,488 pure-SSM parameters.

All long or uncertain CPU work used Hugging Face `cpu-upgrade`; short checks
used one local CPU core. No GPU was used. Figure 5's full three-layer
dimensions 384/768 were not run because they are not defensible under the
CPU-only campaign; no downscaled proxy is presented as full-scale evidence.
Claims 3–4 explicitly repair source-defined ambiguities and state the scoped
domain/distribution on their evidence pages.

- [Illustrated reproduction report](reports/full-reproduction/report.md)
- [Evidence-first marimo tutorial](notebooks/hybrid_tradeoffs_tutorial.py)
- [Evaluator-visible Space source](space/pages/index.md)
- [Raw claim artifacts](.openresearch/artifacts)

The fixed cumulative command is:

```bash
uv run --frozen --no-dev python scripts/run_reproduction.py
```

## Experiment log

| Branch / experiment | Purpose or change | Exact run command | Assessment / outcome | Compute |
|---|---|---|---|---|
| `main` | Public README, report, notebook, and Space mirror | Not run as an experiment (publication surface) | Presentation-only | None |
| [Historical judged baseline](https://github.com/MachineLearning-Nerd/icml26-repro-82EJxJzG6r-expressivity-efficiency-tradeoffs-for-hybrid-sequence-models/tree/orx/historical-judged-baseline-audit) | Freeze paper, verdict, and exact judged-Space manifest | `uv run --frozen --no-dev python scripts/run_reproduction.py` | PASS; protected score 0/12 | Local CPU, 26 s |
| [Claim 1 theorem calibration](https://github.com/MachineLearning-Nerd/icml26-repro-82EJxJzG6r-expressivity-efficiency-tradeoffs-for-hybrid-sequence-models/tree/orx/claim-1-theorem-calibration) | Audit Theorem 3.3 quantifiers and construct a scalable counterexample | `uv run --frozen --no-dev python scripts/run_reproduction.py` | FALSIFIED/HIGH | Local CPU, 10 s |
| [Claim 2 sliding-window lower bound](https://github.com/MachineLearning-Nerd/icml26-repro-82EJxJzG6r-expressivity-efficiency-tradeoffs-for-hybrid-sequence-models/tree/orx/claim-2-sliding-window-lower-bound) | Symbolic W<R witness family | `uv run --frozen --no-dev python scripts/run_reproduction.py` | VERIFIED/MEDIUM | Local CPU, 5 s |
| [Claim 3 selective-copy construction](https://github.com/MachineLearning-Nerd/icml26-repro-82EJxJzG6r-expressivity-efficiency-tradeoffs-for-hybrid-sequence-models/tree/orx/claim-3-selective-copying-construction) | Corrected construction plus complete defined-domain sweep | `uv run --frozen --no-dev python scripts/run_reproduction.py` | VERIFIED/MEDIUM | Local CPU, 5 s |
| [Claim 4 associative-recall construction](https://github.com/MachineLearning-Nerd/icml26-repro-82EJxJzG6r-expressivity-efficiency-tradeoffs-for-hybrid-sequence-models/tree/orx/claim-4-associative-recall-construction) | Exact rational 99% first-hit calibration | `uv run --frozen --no-dev python scripts/run_reproduction.py` | VERIFIED/MEDIUM | Local CPU, 5 s |
| [Claim 5 learned frontier](https://github.com/MachineLearning-Nerd/icml26-repro-82EJxJzG6r-expressivity-efficiency-tradeoffs-for-hybrid-sequence-models/tree/orx/claim-5-selective-copy-parameter-frontier) | Faithful selective-copy parameter sweep | `uv run --frozen --no-dev python scripts/run_reproduction.py` | FALSIFIED/MEDIUM | HF cpu-upgrade, 8 one-thread workers, 1 h 43 min |
| [Claim 6 recycled-worker recovery](https://github.com/MachineLearning-Nerd/icml26-repro-82EJxJzG6r-expressivity-efficiency-tradeoffs-for-hybrid-sequence-models/tree/orx/claim-6-mkar-recycled-worker-recovery) | Complete Figure 6 grid after the retained eight-worker stall | `uv run --frozen --no-dev python scripts/run_reproduction.py` | Scientific PASS; ratio 1.927× | HF cpu-upgrade, 6 one-thread workers, 4 h 01 min |
| [Cumulative winner](https://github.com/MachineLearning-Nerd/icml26-repro-82EJxJzG6r-expressivity-efficiency-tradeoffs-for-hybrid-sequence-models/tree/orx/claim-6-faithful-decoding-recall-benchmark) | Freeze Claim 6 and rerun all six independent verifiers | `uv run --frozen --no-dev python scripts/run_reproduction.py` | PASS; no BLOCKED claims | Local CPU, 30 s |

## Run locally

```bash
uv sync --frozen
uv run --frozen --no-dev python scripts/run_reproduction.py
```

The marimo tutorial embeds the accepted results and never launches training:

```bash
uv run --frozen --no-dev marimo edit notebooks/hybrid_tradeoffs_tutorial.py
uv run --frozen --no-dev marimo run notebooks/hybrid_tradeoffs_tutorial.py
```

Methods, source anchors, exact assumptions, raw CSV/JSON, checker outputs,
negative controls, seeds, CPU allocation, runtime, and limitations are linked
from the [report](reports/full-reproduction/report.md).
