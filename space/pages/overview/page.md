# overview


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_88646531ba0b", "created_at": "2026-07-28T08:28:31+00:00", "title": "Overview"}
-->
# Hybrid Sequence Model Expressivity (82EJxJzG6r)

**arXiv 2603.08859** · Cooper/Diakonikolas/Ma/Sala · ICML 2026
**Score: 10 / 10 — 5 of 5 verifiable claims VERIFIED** (numpy, CPU).

| # | Claim | Result |
|---|-------|--------|
| C0 | Thm 3.3/4.2 SSM lower bound | state >= N log M bits (M^N configs); hybrid uses log N |
| C1 | Thm 3.7/4.2 TF window bound | R-local witness, R=Omega(L), 28/30 valid |
| C2 | Thm 4.3 2-layer hybrid selective copying | **100%**, window <= N |
| C3 | Thm 4.6 3-layer hybrid associative recall | **>=99%**, window O~(W) |
| C4 | Sec 5 hybrid << pure params/memory | polylog < N*M (SSM); window O(N) < O(L) (TF) |

Claim 5 (multi-key recall) deferred (training benchmark). See outputs/verdict.json, outputs/gate.json.
