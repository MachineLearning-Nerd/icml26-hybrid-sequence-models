# Evaluator visibility matrix

Traversal starts at `pages/index.md` or the root of this logbook. No internal
dashboard, unpublished branch, or hidden run log is needed to interpret a
verdict.

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | [Claim 1](#/claim-1) | verifier + independent checker | RHS grid and threshold inline | CSV + JSON | exhaustive injection/Fano reconstruction | missing-coordinate exit 4 | exact 1/2 threshold and linear-in-m consequence | FALSIFIED/HIGH |
| 2 | [Claim 2](#/claim-2) | verifier + independent checker | all 8 witness rows inline | witness CSV | symbolic suffix certificate | W≥R exit 5 | exact 2/3 implication under proof premise | VERIFIED/MEDIUM |
| 3 | [Claim 3](#/claim-3) | verifier + independent checker | all 5 complete domains inline | CSV + construction JSON | exhaustive 6,266-input checker | zero-temperature exit 7 | defined universal domain and resource bounds | VERIFIED/MEDIUM |
| 4 | [Claim 4](#/claim-4) | verifier + independent checker | exact K/K−1 fractions inline | calibration CSV + construction JSON | rational first-hit search + exhaustive W=2 | K−1 exit 9 | explicit uniform-word distribution | VERIFIED/MEDIUM |
| 5 | [Claim 5](#/claim-5) | verifier + checker + training code | paper and observed tables inline | full frontier JSON | independent aggregate/parameter replay | random targets + evidence mutation | imported “match” and exact 6× wording | FALSIFIED/MEDIUM |
| 6 | [Claim 6](#/claim-6) | verifier + checker + training code | threshold hits, intervals, ratio inline | complete 457-job JSON | 24-model/264-seed replay | random targets + ratio mutation exit 4 | exact imported composite and full Figure 6 grid | FALSIFIED/HIGH |

## Shared release requirements

| Requirement | Evaluator-visible location | Status |
|---|---|---|
| Exact fixed command | every claim page; [provenance](#/provenance) | complete |
| Pinned environment | root `pyproject.toml`, `uv.lock`, `.python-version`; provenance page | complete |
| Source URLs, hashes, anchors | every claim source audit and page | complete |
| Git SHA, seeds, CPU, runtime | every claim page and provenance page | complete |
| Limitations/deviations | every claim page and linked limitations file | complete |
| Historical rejected baseline | [history](#/history), original page unchanged | complete |
| Current verifier obvious | current verification is first in navigation; current SHA named on index | complete |
| Live-score honesty | index and current report retain 0/12 until evaluator reruns | complete |
| Evaluator-blind review | [recorded traversal](#/red-team) with every opened file in JSON | complete |

This matrix is a discoverability claim. The release audit must re-download the
candidate, begin only at the canonical index, open every linked file, and
treat anything unreachable as missing.
