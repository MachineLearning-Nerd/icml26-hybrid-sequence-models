# Expressivity–Efficiency Tradeoffs for Hybrid Sequence Models

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-hybrid-sequence-models/blob/main/notebooks/hybrid_tradeoffs_tutorial.py)

Independent claim-by-claim reproduction audit for [*Expressivity-Efficiency Tradeoffs for Hybrid Sequence Models*](https://arxiv.org/abs/2603.08859), by John Cooper, Ilias Diakonikolas, Mingchen Ma, and Frederic Sala. This repository is an audit and reproduction workspace; it is not the authors' official implementation.

## Paper in one paragraph

The paper studies hybrid sequence models that combine Transformer attention with state-space-model layers. Its theory identifies limitations for non-hybrid models on synthetic sequence tasks, then constructs compact hybrids for selective copying and associative recall. Its experiments evaluate learned hybrids on the same task family and report improvements in parameter efficiency, length generalization, and out-of-distribution robustness.

## Audit headline

The six evaluator-selected claims have terminal, evidence-backed verdicts: Claims 2–4 are **VERIFIED**, while Claims 1, 5, and 6 are **FALSIFIED** under their exact imported contracts. The audit still supports the paper's central architectural mechanism—recurrent state plus short attention can solve the constructed tasks—but it does not support every strong numerical or wording claim attached to it. These are reproduction assessments, not live judge points; the protected historical score remains 0/12 until the evaluator reruns.

The strongest empirical divergence is Figure 6: the complete 24-point grid reaches 60% mean multi-key recall at 3,684 parameters for SSM→Transformer and 7,100 for pure Transformer, a **1.927×** ratio rather than the imported 6×. Figure 5's full three-layer widths 384 and 768 were not rerun on CPU; no downscaled proxy is presented as full-scale evidence.

The compact status and audit entry points are [STATUS.md](STATUS.md),
[CLAIM_EVIDENCE.md](CLAIM_EVIDENCE.md), [SOURCE_AUDIT.md](SOURCE_AUDIT.md),
[ENVIRONMENT.md](ENVIRONMENT.md), and [REPORT.md](REPORT.md). The historical
0/12 evaluator result is preserved separately from the current local evidence;
this repository makes no current score or author-endorsement claim.

## Claim and evidence ledger

| Claim | Paper/imported result | Reproduction assessment | How the result is produced |
| --- | --- | --- | --- |
| 1 | Theorem 3.3 gives a state lower bound linear in hidden dimension `m` | **FALSIFIED — HIGH** | Injectivity forces `q log|Y| >= m log|V|`, making the displayed expression non-positive; a singleton-state binary-output model reaches the exact 1/2 threshold. |
| 2 | Theorem 3.7 requires total sliding-window size at least the dependency range `R` | **VERIFIED — MEDIUM** | Construct eight pairs with identical final-`R` suffixes and different labels; every `W < R` deterministic predictor is limited to 1/2 accuracy. |
| 3 | A two-layer SSM→attention hybrid solves selective copying with logarithmic embedding and `O(N)` attention window | **VERIFIED — MEDIUM** | Apply the corrected finite-temperature construction to every defined sequence in five complete finite domains: 6,266/6,266 pass. |
| 4 | A three-layer hybrid reaches 99% decoded associative recall with logarithmic embedding and near-linear window | **VERIFIED — MEDIUM** | Use exact rational probability calibration, verify `K` passes and `K-1` fails for vocabulary sizes 2–64, and exhaustively check the `W=2` construction. |
| 5 | Roughly 2k hybrid parameters match pure models at roughly 12k, implying a 6× selective-copy advantage | **FALSIFIED — MEDIUM** | Source values are 0.999 versus 0.923/0.931, not equal; the 11-seed rerun gives 0.999985 versus 0.846271/0.866493, with calibrated 0.90 first-hit ratios 8.32×/9.61×. |
| 6 | Figures 5–6 show a 6× multi-key advantage and a single-key recall plateau | **FALSIFIED — HIGH** | Figure 5 is associative recall with a five-bit decoded control variable, not single-key recall; the complete Figure 6 rerun gives 3,684 versus 7,100 parameters, ratio 1.927×. |

The exact contracts, source audits, raw outputs, controls, and limitations are under [`.openresearch/artifacts/`](.openresearch/artifacts/). The illustrated explanation is [`reports/full-reproduction/report.md`](reports/full-reproduction/report.md), and each claim has a canonical page under [`space/pages/claims/`](space/pages/claims/).

## How each claim is produced

Every claim follows one auditable path:

1. Anchor the imported wording to the paper source and freeze assumptions, quantifiers, and verdict scope in `claim_contract.json`.
2. Record source hashes, implementation deviations, and limitations in `source_audit.md` and `limitations.md`.
3. Reconstruct the theorem, construction, or training protocol in `reproduction/`.
4. Run an independent checker, a mutation or random-target control, and preserve raw JSON/CSV results with the exact command.
5. Publish the cumulative status in [`space/pages/current/page.md`](space/pages/current/page.md), the visibility page, and the release audit.

Symbolic proofs and complete finite domains support universal claims. Learned-model claims use disjoint calibration/final seeds, held-out sequences, instantiated trainable-parameter counts, and explicit CPU provenance. A finite training sweep is not presented as an architectural theorem.

## Repository contents

- [`reproduction/`](reproduction/) — claim verifiers, independent checkers, model code, and figure-training helpers.
- [`scripts/run_reproduction.py`](scripts/run_reproduction.py) — fixed cumulative runner.
- [`notebooks/hybrid_tradeoffs_tutorial.py`](notebooks/hybrid_tradeoffs_tutorial.py) — evidence-first tutorial notebook.
- [`reports/full-reproduction/report.md`](reports/full-reproduction/report.md) — technical report with equations, results, and limits.
- [`.openresearch/artifacts/`](.openresearch/artifacts/) — claim contracts, source audits, raw data, checker outputs, controls, and provenance.
- [`space/pages/`](space/pages/) — evaluator-visible claim pages and current verification.
- [`space/release/`](space/release/) — allowlist, manifest, visibility, and candidate audit.
- [`branch-audit.md`](branch-audit.md) — old-to-clean branch lineage and migration record.

## Reproduce locally

Install [uv](https://docs.astral.sh/uv/), then run:

```bash
uv sync --frozen
uv run --frozen --no-dev python scripts/run_reproduction.py
```

The tutorial can be checked or opened with:

```bash
uv run --frozen --no-dev marimo check notebooks/hybrid_tradeoffs_tutorial.py
uv run --frozen --no-dev marimo edit notebooks/hybrid_tradeoffs_tutorial.py
```

The cumulative runner exits nonzero when a verifier, independent checker, mutation control, protected manifest, or release gate fails. The environment is Python 3.12 with the committed `uv.lock`. Short theorem checks use local CPU; the accepted Claim 5 and Claim 6 sweeps used Hugging Face `cpu-upgrade` with no GPU.

## Branch map

`main` is the publication surface. Focused branches preserve the experiment lineage with descriptive names; the complete mapping from the former `orx/*` names is in [`branch-audit.md`](branch-audit.md).

| Clean branch | Purpose | Status |
| --- | --- | --- |
| [`historical/judged-baseline`](https://github.com/MachineLearning-Nerd/icml26-hybrid-sequence-models/tree/historical/judged-baseline) | Preserve the original judged Space, manifest, and 0/12 baseline | Historical record |
| [`audit/claim1-theorem-calibration`](https://github.com/MachineLearning-Nerd/icml26-hybrid-sequence-models/tree/audit/claim1-theorem-calibration) | Test Theorem 3.3's quantifiers and state lower-bound consequence | Claim 1 falsified |
| [`audit/claim2-sliding-window-lower-bound`](https://github.com/MachineLearning-Nerd/icml26-hybrid-sequence-models/tree/audit/claim2-sliding-window-lower-bound) | Construct `W < R` indistinguishable suffix witnesses | Claim 2 verified |
| [`audit/claim3-selective-copying`](https://github.com/MachineLearning-Nerd/icml26-hybrid-sequence-models/tree/audit/claim3-selective-copying) | Verify the corrected selective-copy construction | Claim 3 verified |
| [`audit/claim4-associative-recall`](https://github.com/MachineLearning-Nerd/icml26-hybrid-sequence-models/tree/audit/claim4-associative-recall) | Calibrate the 99% associative-recall construction | Claim 4 verified |
| [`audit/claim5-cpu-fidelity-pilot`](https://github.com/MachineLearning-Nerd/icml26-hybrid-sequence-models/tree/audit/claim5-cpu-fidelity-pilot) | Establish CPU fidelity and repair the fixed runner path | Supporting pilot |
| [`audit/claim5-selective-copy-frontier`](https://github.com/MachineLearning-Nerd/icml26-hybrid-sequence-models/tree/audit/claim5-selective-copy-frontier) | Run the learned selective-copy parameter frontier | Claim 5 falsified |
| [`audit/claim5-static-evidence`](https://github.com/MachineLearning-Nerd/icml26-hybrid-sequence-models/tree/audit/claim5-static-evidence) | Freeze independent Claim 5 checks and source comparison | Claim 5 audit |
| [`audit/claim6-mkar-frontier`](https://github.com/MachineLearning-Nerd/icml26-hybrid-sequence-models/tree/audit/claim6-mkar-frontier) | Run the faithful multi-key associative-recall frontier | Claim 6 evidence |
| [`audit/claim6-mkar-worker-recovery`](https://github.com/MachineLearning-Nerd/icml26-hybrid-sequence-models/tree/audit/claim6-mkar-worker-recovery) | Recover the full MKAR sweep after the retained worker stall | Claim 6 evidence |
| [`release/evaluator-candidate`](https://github.com/MachineLearning-Nerd/icml26-hybrid-sequence-models/tree/release/evaluator-candidate) | Freeze the cumulative six-claim verification and release gates | Candidate release |

## Citation

If this audit or its evidence package is useful, please cite the paper:

```bibtex
@misc{cooper2026expressivity,
  title        = {Expressivity-Efficiency Tradeoffs for Hybrid Sequence Models},
  author       = {Cooper, John and Diakonikolas, Ilias and Ma, Mingchen and Sala, Frederic},
  year         = {2026},
  eprint       = {2603.08859},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  url          = {https://arxiv.org/abs/2603.08859}
}
```

## Thank you

Thank you to John Cooper, Ilias Diakonikolas, Mingchen Ma, and Frederic Sala for presenting a precise hybrid-model setting with both constructive theory and empirical comparisons. This audit is intended as a respectful, transparent reproduction record: it preserves the paper's central mechanism, separates universal arguments from finite training evidence, and reports disagreements and unresolved scale limits explicitly.

## Attribution and scope

The repository is maintained by [MachineLearning-Nerd](https://github.com/MachineLearning-Nerd). The normalized commit identity is `MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>`. The original repository slug was `icml26-repro-82EJxJzG6r-expressivity-efficiency-tradeoffs-for-hybrid-sequence-models`; it was renamed to `icml26-hybrid-sequence-models`. The evaluator's historical [DineshAI/82EJxJzG6r Space](https://huggingface.co/spaces/DineshAI/82EJxJzG6r) remains referenced by the protected release metadata and is intentionally not renamed by this GitHub cleanup.
