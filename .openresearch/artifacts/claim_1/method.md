# Claim 1 method

Three materially different routes test the exact statement.

## Route A — cardinality proof certificate

Apply the pigeonhole principle to the assumed injection \(G:\mathcal V^m\to\mathcal Y^q\). This yields \(q\log|\mathcal Y|\ge m\log|\mathcal V|\) without sampling or fitted constants. The independent checker exhaustively enumerates coordinate encodings across the committed grid.

## Route B — scalable assumption-satisfying counterexample

Use a four-symbol vocabulary, binary outputs, and \(q=2m\) controls. Each control returns one bit from the two-bit encoding of one payload symbol, so \(G\) is injective. For any distribution selected by the theorem, one binary label has marginal probability at least 1/2. A singleton-state constant-output SSM therefore reaches the exact stated success threshold with zero state bits for every \(m\).

This falsifies the imported conclusion that the theorem forces state linear in \(m\). It does not contradict the displayed inequality, whose right-hand argument is exactly zero for this family.

## Route C — independent Fano reconstruction

Reconstruct the appendix inequality

\[
\log|\mathcal S|\ge m\log|\mathcal V|-q(H_2(\epsilon)+\epsilon\log|\mathcal Y|).
\]

For the counterexample family, \(\epsilon=1/2\) makes the reconstructed bound negative. The proof's substituted \(\epsilon=1/8\) makes it positive and linear. This confirms that the threshold change is load-bearing.

## Controls

The independent checker removes the last coordinate control. The resulting \(G\) must be non-injective and the checker must exit 4. A second conceptual control uses a balanced distribution: neither constant output exceeds 1/2, showing why the counterexample is specific to the theorem's exact threshold and does not claim success at 7/8.
