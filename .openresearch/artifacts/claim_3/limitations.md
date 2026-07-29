# Claim 3 limitations and deviations

- Inputs with no number token are counted but cannot be scored because the paper's target is undefined.
- This verifies an explicit existential construction, not the learnability of a trained Mamba/Transformer implementation.
- The source query/key indexing is corrected and finite softmax decoding is proved with a strict margin.
- The official notebook is comparative context only; it uses full causal attention. The verifier independently enforces a true \(N\)-token window.
- Complete finite domains corroborate code; the general claim rests on the symbolic recurrence and dominance proof.
