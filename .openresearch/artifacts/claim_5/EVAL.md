# Claim 5 evaluation

Verdict: **FALSIFIED** (MEDIUM confidence) for the exact imported claim.

The imported wording says the roughly-12k pure models "match" the perfect
roughly-2k hybrid. The paper's own Figure 4 table instead reports 0.999 versus
0.923/0.931 and says the pure models reach only "around 0.9." The independent
11-seed CPU rerun finds:

| Model | Exact parameters | Mean accuracy | 10th–90th percentile |
|---|---:|---:|---:|
| SSM→TF | 2,192 | 0.999985 | 0.999945–1.000000 |
| TF→TF | 10,608 | 0.846271 | 0.868155–0.874724 |
| SSM→SSM | 13,488 | 0.866493 | 0.664958–0.999973 |

Across the same 11 seeds, exact one-sided sign-test p-values are below 0.05
for hybrid versus each pure model. In the precommitted finite width grid, the
first mean accuracy at least 0.90 occurs at 2,192 parameters for SSM→TF,
18,240 for TF→TF (8.32x), and 21,056 for SSM→SSM (9.61x). Random-target
accuracy is 0.041856 and exact-sequence accuracy is zero.

The paper's actual qualitative and rounded quantitative ordering is
corroborated. The falsification is scoped to the imported stronger word
"match" and exact 6x assertion.
