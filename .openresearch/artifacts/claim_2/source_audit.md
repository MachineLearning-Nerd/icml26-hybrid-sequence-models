# Claim 2 source audit

Source hashes and retrieval details are in `../project/source_audit.md`.

The local-sensitivity assumption is at `sections/func_comp_and_construct.tex` lines 54–56. It requires two sequences whose last \(R\) coordinates are equal while their target values differ. The theorem is at lines 58–60:

\[
\Pr_D[M(x)=F(x)]\ge 2/3
\quad\Longrightarrow\quad
\sum_{i=1}^k W_i\ge R.
\]

The proof is at `appendix/missing_proof_lb.tex` lines 88–94. It sets \(W=\sum_i W_i\), asserts that the final output is a deterministic function of the final \(W\) input tokens, and uses the uniform distribution on the two witnesses. When \(W<R\), their observations are identical, so any common prediction is wrong on one of the two labels and has accuracy at most \(1/2<2/3\).

The paper's preliminaries define full attention but do not formally define a causal sliding-window mask or its indexing convention. The verification therefore conditions on the exact suffix-dependency premise explicitly used in the theorem proof. This missing definition is why confidence is MEDIUM rather than HIGH.
