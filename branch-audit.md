# Branch audit

This repository was migrated from opaque OpenResearch-generated branch names to descriptive branches. Each clean branch preserves the corresponding experiment snapshot and makes its purpose visible.

## Mapping

| Former branch | Clean branch | Purpose |
| --- | --- | --- |
| `orx/historical-judged-baseline-audit` | `historical/judged-baseline` | Preserve the original judged Space, manifest, and protected 0/12 baseline. |
| `orx/claim-1-theorem-calibration` | `audit/claim1-theorem-calibration` | Audit Theorem 3.3's assumptions and the claimed linear state consequence. |
| `orx/claim-2-sliding-window-lower-bound` | `audit/claim2-sliding-window-lower-bound` | Build and verify the `W < R` sliding-window witness family. |
| `orx/claim-3-selective-copying-construction` | `audit/claim3-selective-copying` | Verify the corrected finite-temperature selective-copy construction. |
| `orx/claim-4-associative-recall-construction` | `audit/claim4-associative-recall` | Calibrate and exhaustively check the 99% associative-recall construction. |
| `orx/claim-5-cpu-fidelity-pilot` | `audit/claim5-cpu-fidelity-pilot` | Establish CPU fidelity and repair the fixed runner package path. |
| `orx/claim-5-selective-copy-parameter-frontier` | `audit/claim5-selective-copy-frontier` | Run the learned selective-copy parameter frontier. |
| `orx/claim-5-static-evidence-and-independent-checks` | `audit/claim5-static-evidence` | Freeze independent Claim 5 checks and source comparison. |
| `orx/claim-6-faithful-multi-key-recall-benchmark` | `audit/claim6-mkar-frontier` | Run the faithful multi-key associative-recall frontier. |
| `orx/claim-6-mkar-recycled-worker-recovery` | `audit/claim6-mkar-worker-recovery` | Recover the full MKAR sweep after the retained worker stall. |
| `orx/claim-6-faithful-decoding-recall-benchmark` | `release/evaluator-candidate` | Freeze the cumulative six-claim verification and release gates. |
| `main` | `main` | Publication surface containing the cumulative audit. |

## Migration guarantees

- All former `orx/*` remote branches were deleted after their clean replacements were pushed.
- Every live branch contains this file and the claim-focused README.
- Branch tips and historical commits were normalized to `MachineLearning-Nerd <37579156+MachineLearning-Nerd@users.noreply.github.com>`.
- The renamed repository is [`MachineLearning-Nerd/icml26-hybrid-sequence-models`](https://github.com/MachineLearning-Nerd/icml26-hybrid-sequence-models).
- The historical Hugging Face Space identifier `DineshAI/82EJxJzG6r` is intentionally retained in evaluator metadata; it is not a GitHub username or branch name.

## Verification checklist

For each clean branch, verify:

```bash
git show-ref --verify "refs/heads/<branch>"
git show "<branch>:README.md" >/dev/null
git show "<branch>:branch-audit.md" >/dev/null
git log "<branch>" --format='%an <%ae>' | sort -u
```

The expected identity is `MachineLearning-Nerd <37579156+MachineLearning-Nerd@users.noreply.github.com>`. Scientific status comes from the claim contracts and evidence pages, not from branch names alone.
