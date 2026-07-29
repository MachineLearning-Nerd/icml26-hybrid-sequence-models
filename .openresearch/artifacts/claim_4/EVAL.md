# Claim 4 evaluation

Verdict: **VERIFIED** with MEDIUM confidence under the explicit uniform-word distribution in the claim contract.

Acceptance requires:

- exact independent first-hit calibration for every vocabulary size;
- probability at \(K\) at least 0.99 and at \(K-1\) below 0.99;
- a linear-in-\(W\) certified window bound;
- \(2W-1\) reachable query-prefix states;
- logarithmic embedding dimension;
- target attention mass above 1/2;
- exact exhaustive construction behavior for \(W=2\);
- exit 9 for the \(K-1\) control.

Confidence remains MEDIUM because the paper has a task-name typo, inconsistent distribution wording, an implicit power-of-two vocabulary requirement, and an undefined target when the query word never occurs.
