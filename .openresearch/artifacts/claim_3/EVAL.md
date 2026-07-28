# Claim 3 evaluation

Verdict: **VERIFIED** with MEDIUM confidence on every input for which selective copying is defined.

Release acceptance requires:

- exact accuracy 1.0 on every valid sequence in each complete finite domain;
- a strict target attention mass above 1/2;
- \(N+1\) reachable recurrent states;
- window exactly \(N\);
- the explicit logarithmic embedding bound;
- a local-sensitivity witness with shared suffix \(L-1\) and different targets;
- exit 7 for the zero-temperature control.

Confidence is MEDIUM because the source's universal domain includes undefined number-free inputs, its displayed query/key indices require correction, and the official notebook does not apply a sliding-window mask. These deviations are visible rather than silently normalized.
