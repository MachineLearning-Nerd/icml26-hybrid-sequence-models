# Claim-by-claim evaluator-visible gap analysis

Audited artifacts:

- protected current Space `DineshAI/82EJxJzG6r@9449686999e15049fa1e258517852b9f2a00bda1`;
- public comparison Space `agharsallah/82ejxjzg6r-logbook@66eb9e56f4b07b9b825d96b12997665fde90f402`;
- live verdict dataset filtered by the exact `space_id`, never by OpenReview id alone.

The comparison logbook is useful for its one-page-per-claim navigation and inline result tables. It is not accepted as scientific evidence: it exposes no executable source files, fixed command, lockfile, linked raw data files, independent checker, negative control, Git SHA per run, or complete runtime record. Its Claim 1 check also replaces the theorem's probability and \(q,|\mathcal Y|\) terms with a stronger deterministic fooling-set statement.

| Claim | Current DineshAI artifact | Comparison artifact | Required new evidence |
| --- | --- | --- | --- |
| 1 | One unsupported sentence | Finite fooling-set grid, no executable proof | Exact source audit; probability-aware derivation; injectivity cardinality audit; assumption-satisfying counterexample search; executable checker and control |
| 2 | Unsupported "28/30" | Explicit claimed witness family, no code | Symbolic receptive-field proof; complete witness data; exhaustive checker; deliberately invalid witness control |
| 3 | Unsupported "100%" | Claimed exhaustive/random accuracy, no code | Paper construction code; symbolic invariant checks; complete finite-domain exhaustion; resource scaling table; window-too-small control |
| 4 | Unsupported ">=99%" | 20k claimed trials, no code | Paper construction code; exact distribution; binomial uncertainty; coupon-window calibration independent of theorem formula; wrong-decoder control |
| 5 | No Figure 4 numbers or runs | Small substituted training sweep with three seeds | Faithful official architecture/task/protocol, 11 seeds, LR sweep, raw curves/counts, uncertainty, matched-budget and larger-pure controls |
| 6 | Explicitly deferred | Substituted last-write-wins task, not paper MKAR | Exact paper MKAR generator (length 100, vocab 8, key length 2), 11 seeds, architecture/parameter sweep; separate Figure 5 decoding-recall assessment |

## Navigation gap

The current Space has only `pages/index.md` → `pages/overview/page.md`. It has no per-claim route and references absent `outputs/verdict.json` and `outputs/gate.json`. The candidate must add current verification first, retain the old overview labeled exactly **Historical rejected baseline**, and make every code/data/checker/control link reachable from `pages/index.md`.

