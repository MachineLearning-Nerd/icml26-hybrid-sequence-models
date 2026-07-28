# Claim 2 evaluation

Verdict: **VERIFIED** with MEDIUM confidence.

The exact Theorem 3.7 implication is reconstructed symbolically under the final-suffix dependency premise used by the paper's own proof. All committed witness cases must have:

- a shared \(R\)-token suffix;
- different target labels;
- total window \(W<R\);
- identical final-\(W\) observations;
- maximum accuracy exactly \(1/2\) under the uniform witness pair;
- strict separation \(1/2<2/3\).

The over-budget control must exit 5. Confidence remains MEDIUM because the paper never formally defines sliding-window masking or settles its indexing convention in the preliminaries.
