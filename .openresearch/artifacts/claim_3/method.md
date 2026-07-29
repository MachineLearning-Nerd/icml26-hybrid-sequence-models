# Claim 3 method

## Corrected two-layer construction

The recurrent layer has reachable state \(\{\bot,1,\ldots,N\}\). On a number token it replaces the state with that token's distance; on any ordinary token it carries the state. This is the paper's selective Mamba recurrence and has \(N+1=O(|\mathcal V|)\) reachable states.

At the final position, attention sees exactly the last \(N\) tokens. Query and key are signed binary codes for the stored control distance and each relative distance. Equal codes have dot product \(b\); every unequal code has dot product at most \(b-2\). With

\[
\beta=1+\tfrac12\log(\max(1,N-1)),
\]

the target softmax mass is bounded below by

\[
\frac{1}{1+(N-1)e^{-2\beta}}>1/2.
\]

Values are signed binary token codes. More than half the mass on the target preserves every coordinate's sign, so a linear correlation decoder returns the exact target token.

The embedding dimension used by the certificate is

\[
d=2\lceil\log_2|\mathcal V|\rceil+2\lceil\log_2L\rceil+1,
\]

and the \(N\)-vector attention memory is \(O(N\max(\log|\mathcal V|,\log L))=\widetilde O(N)\).

## Complete-domain checks

The independent checker enumerates every sequence for five finite \((L,|\mathcal V|,N)\) domains. It separately counts sequences without a number token, because the paper does not define a target on them. Universality is supplied by the recurrence and attention-dominance proof; enumeration guards the implementation.

## Pure-Transformer comparison

Two length-\(L\) sequences differ only in the first number token, 1 versus 2, share the remaining \(L-1\) tokens, and select distinct final tokens. Verified Claim 2 gives total window at least \(L-1=\Omega(L)\) on their uniform mixture.

## Negative control

Setting attention temperature to zero makes the two-token window uniform. The committed adversarial sequence then decodes token 0 instead of target token 3, and the checker exits 7.
