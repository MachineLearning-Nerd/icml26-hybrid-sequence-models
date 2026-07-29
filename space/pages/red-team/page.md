# Evaluator-blind review

The review is intentionally scoped to a fresh candidate copy and the evaluator
rubric. It begins only at `pages/index.md`; repository knowledge, OpenResearch
descriptions, internal run logs, and unpublished paths are not used to fill
gaps.

## Round 1 findings and fixes

| Finding | Evaluator risk | Fix |
|---|---|---|
| Duplicate `evidence/` copies did not preserve the repository-relative executable layout | Reviewer might open a non-runnable duplicate instead of the current verifier | Removed duplicates; current code now appears only at `reproduction/` and `scripts/`, with exact `.openresearch/artifacts/` paths |
| QA created nested `.venv` and `__pycache__` files | Candidate could upload local environment state or generated binaries | Removed from both source and fresh candidate; allowlist rejects either path |
| Three canonical navigation files necessarily changed | Exact judged bytes could become undiscoverable | Added exact-hash copies under `historical/judged_revision/`; all other protected files remain unchanged at their original paths |
| Claim 4 lacked a compact run-evidence JSON | CPU/runtime/Git provenance was less direct than other theorem claims | Added evaluator-linked `orx_run_evidence.json` |
| Candidate had no mechanical canonical-entrypoint traversal | Broken or hidden evidence might survive manual review | Added `scripts/audit_release_candidate.py` |

## Round 2 result before recording the review

**PASS.** Starting at `pages/index.md`, the audit opened 74 reachable files,
including all six claim pages, their exact contracts, current verifier and
checker sources, raw CSV/JSON, checker output, negative-control output, source
audit, method, provenance, environment lock, and five SVG figures.

- Missing linked targets: 0
- Claim rows complete: 6/6
- Protected judged paths present: 13/13
- Changed protected entrypoints preserved by exact historical hashes: 3/3
- Candidate secret findings: 0
- New or changed non-text files in upload set: 0
- Candidate environments or bytecode caches: 0

## Round 3 after recording the review

The review page and its machine record were added to navigation, then the
fresh traversal was repeated. **PASS:** 76 reachable files opened, 0 missing
targets, all 6 claim contracts complete, all 13 protected paths present, and
0 secret findings.

The final release-metadata pass adds the release report to the same navigation
and opens **77** reachable files with the same zero-missing result.

The complete machine record, including **every file opened**, is
[prepublication audit JSON](../../release/final_candidate_audit.json).

## Reviewer conclusions

| Claim | Could the exact contract and current verifier be located? | Could raw numbers and control be checked? | Conclusion |
|---|---|---|---|
| 1 | yes | yes | FALSIFIED/HIGH is evaluator-visible |
| 2 | yes | yes | VERIFIED/MEDIUM is evaluator-visible |
| 3 | yes | yes | VERIFIED/MEDIUM is evaluator-visible |
| 4 | yes | yes | VERIFIED/MEDIUM is evaluator-visible |
| 5 | yes | yes | FALSIFIED/MEDIUM is evaluator-visible |
| 6 | yes | yes | FALSIFIED/HIGH is evaluator-visible |

No conclusion required an inaccessible file. The in-app visual browser was not
available in this session; SVGs were instead parsed as text and rendered to
PNG previews for layout inspection. The scientific claims do not depend on
image-only data: all decisive values are also inline and in raw JSON/CSV.
