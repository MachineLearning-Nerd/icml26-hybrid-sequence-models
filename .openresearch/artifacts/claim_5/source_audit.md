# Claim 5 empirical source audit

The exact source is Figure 4 and its surrounding text in
`sections/experiments.tex`, with setup details in
`appendix/experiment_details.tex`.

Source archive SHA-256:
`e8d22bfd259aaa60385841d8643109ecb66f7eb1081dd76429f5215f05a032e8`.
The relevant source anchors are `sections/experiments.tex` lines 26–49 and
`appendix/experiment_details.tex` lines 3–19 in the retrieved arXiv archive.

The paper's table reports SSM→TF accuracy 0.999 at approximately 2,000
parameters, while the approximately-12,000-parameter pure Transformer and
pure SSM report 0.923 and 0.931. The caption accurately says the pure models
reach only “around 0.9”; the imported judge claim instead says they “match”
the hybrid's perfect accuracy. Those are different contracts and will be
reported separately.

Audited quantifiers and setup:

- learned two-layer architectures, including SSM→TF, TF→SSM, TF→TF, SSM→SSM;
- selective copy, sequence length 100, windowed causal attention, one head;
- RoPE, Mamba state size 1, seq-to-seq token accuracy over valid targets;
- AdamW, learning-rate sweep from 1e-4 to 1 by factors of sqrt(10), 100 warmup
  steps, linear decay, “trained to convergence”;
- 11 repetitions; mean with 10th and 90th percentiles;
- Figure data identifier uses five number tokens and 26 vocabulary tokens.

Source ambiguities or inconsistencies that the final contract must not hide:

1. the prose says number tokens 5 through 10 (six inclusive), while the public
   generator and Figure data identifier use five tokens, #5 through #9;
2. no seeds are recorded;
3. “convergence” has no numerical stopping criterion;
4. saved run identifiers end in `sd1`, but the Figure parameter counts
   exactly imply effective state size 16 (the model default), not 1;
5. the table's parameter buckets are rounded, so the exact claimed 6× ratio
   must be recomputed from printed model counts;
6. the public evaluation loop uses only the first eight generated examples
   when `eval_num_batches=1`, despite an argument named `num_eval_examples=100`.

The imported claim is therefore not an exact quotation of Figure 4. Its word
"match" strengthens the paper's explicit 0.923/0.931 and "around 0.9" result
into equality with the 0.999 hybrid. The current verdict applies to that exact
imported contract; it does not reject the paper's actual ordering.
