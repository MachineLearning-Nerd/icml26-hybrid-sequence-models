# Claim 2 method

## Symbolic universal certificate

Let \(W=\sum_i W_i<R\). Equality of the witnesses' final \(R\) tokens implies equality of their final \(W\) tokens. Under the paper proof's operational premise, the model output is the same on both witnesses. Their target labels differ, so under the uniform two-point distribution every deterministic common output has accuracy at most \(1/2\). The same bound holds for a randomized output after averaging over its internal randomness. Since \(1/2<2/3\), a model reaching the theorem threshold must have \(W\ge R\).

This is a proof-level implication over arbitrary layer count, window partition, vocabulary, and model parameters; the tabulated finite checks are regression tests for the certificate, not an attempt to infer a universal lower bound from samples.

## Independent checker

`reproduction/claim2_checker.py` constructs explicit binary witnesses, checks the shared \(R\)-suffix and differing labels, forms the precise final-\(W\) observation, and exhausts the two possible deterministic binary predictions. The committed grid varies sequence length, dependency range, depth, zero-window layers, and uneven partitions.

## Negative control

The checker replaces the representative window stack by a total window \(R+1\). This includes the differing coordinate, makes the observations unequal, violates \(W<R\), and exits 5. The control shows that the certificate does not pass once its resource premise is removed.
