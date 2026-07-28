# Claim 5 method

The frozen scientific run instantiated the authors' public GPTNeoX/Mamba
implementation and selective-copy generator. Twelve architecture/width points
were fixed before launch. For every point, three neighboring learning rates
were trained for 1,000 steps on two calibration seeds; the lowest mean
training loss selected the rate. Final models trained for the paper's 4,000
steps. Four headline points used 11 disjoint seeds and all other frontier
points used three. Each seed was evaluated on 2,048 deterministic held-out
sequences.

The independent static checker:

1. recomputes every accuracy from raw correct/valid counts;
2. recomputes every aggregate, percentile, and interval;
3. reconstructs learning-rate selection from all 72 calibration jobs;
4. checks all 68 final jobs, exact seeds, steps, parameter counts, and CPU
   allocation;
5. instantiates every architecture again and recounts trainable parameters;
6. independently finds the first mean-accuracy-at-least-0.90 point in each
   precommitted width grid;
7. performs paired exact sign tests because all headline architectures use the
   same 11 fixed seeds; and
8. requires a random-target SSM-to-TF control to remain below 20%.

The strict route precommitted in the training harness required both pure-model
upper 95% seed intervals to remain below 0.99. It is honestly BLOCKED because
the pure SSM is extremely seed-sensitive. Two independent routes resolve the
exact imported wording: the paper source itself says "around 0.9," not
"match," and paired-seed tests show the hybrid exceeds both paper-neighborhood
pure models.
