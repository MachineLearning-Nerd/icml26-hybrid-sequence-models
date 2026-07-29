# Claim 3 source audit

Source hashes and retrieval details are in `../project/source_audit.md`.

Selective copying is defined at `sections/tasks.tex` lines 4–8. The most recent number token is interpreted as a backward distance and the target is \(x_{L+1-n}\). Theorem 4.3 is at lines 28–31 and is restated at `appendix/constructions.tex` lines 38–40. It quantifies over every input sequence and asserts:

- two layers: Mamba followed by attention;
- \(d=O(\max(\log|\mathcal V|,\log L))\);
- \(O(|\mathcal V|)\) Mamba states;
- attention window \(O(N)\).

The proof's intended recurrence is at Appendix lines 78–119 and its attention construction at lines 121–163.

Three source defects require explicit handling:

1. The task's `argmax` is undefined when the sequence has no number token. “Every input” is therefore interpreted as every input in the task's defined domain; undefined inputs are counted separately.
2. Appendix line 126 queries \(\phi(n)\) while the target key is at relative distance \(n\); with the preceding definition of \(\phi\), the displayed indices do not match. The verifier uses the intended distance-to-distance comparison.
3. The official construction notebook at audited code SHA `7beeb0de80f89eb5d75301aef8e97ee9b36ca999` instantiates full causal attention, not the theorem's \(N\)-token sliding window. The verifier implements the actual last-\(N\)-token mask.

The finite-temperature correction uses a strict target-weight bound and a linear code decoder, avoiding the proof's unjustified equality between a finite softmax and a one-hot vector.
