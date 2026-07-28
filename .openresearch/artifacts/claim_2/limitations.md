# Claim 2 limitations and deviations

- The result verifies the theorem under the dependency semantics asserted in its proof; the paper omits a formal sliding-window definition.
- The theorem's lower bound is on the sum of per-layer windows, not parameter count, training efficiency, or performance under a natural data distribution.
- The hard distribution contains only the two local-sensitivity witnesses. This is the theorem's exact existential distribution, not a claim about average-case data.
- The finite grid is diagnostic only. Universality comes from the symbolic suffix-inclusion and indistinguishability certificate.
