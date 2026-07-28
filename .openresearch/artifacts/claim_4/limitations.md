# Claim 4 limitations and deviations

- The distribution is made explicit as uniform word context plus an appended fixed-length query-bit suffix.
- Word-vocabulary sizes are powers of two so every bit string maps to exactly one word.
- Query absence is treated as failure, not silently removed by conditioning.
- The verifier proves the 99% construction; it does not claim a trained neural network learns these weights.
- Exact rational calibration replaces an empirical Monte Carlo estimate, so no sampling confidence interval is needed.
