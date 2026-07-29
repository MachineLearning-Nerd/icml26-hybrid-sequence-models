# Claim 6 source audit

Retrieved from `https://export.arxiv.org/e-print/2603.08859` on
2026-07-28 with an explicit `OpenResearch-Reproduction/1.0` User-Agent.
The source archive SHA-256 is
`e8d22bfd259aaa60385841d8643109ecb66f7eb1081dd76429f5215f05a032e8`.
The audited public code revision is
`7beeb0de80f89eb5d75301aef8e97ee9b36ca999`.

## Figure 6: multi-key associative recall

The exact source anchors are `sections/experiments.tex:63-91` and
`appendix/experiment_details.tex:5-19`.

- The sequence has length \(L=100\), vocabulary size 8, and key length \(k=2\).
- The query is the final two tokens. The target is the token after the last
  earlier occurrence of that pair.
- Figure 6 compares two-layer pure Transformer, pure SSM, TF-to-SSM, and
  SSM-to-TF models while increasing hidden dimension.
- The caption and results paragraph quantify the claim as 60% mean accuracy
  with 6x fewer parameters than the pure Transformer.
- The displayed table reports, at rounded parameter buckets 1k/2k/6k/12k,
  pure-Transformer accuracies 0.124/0.159/0.230/0.668 and SSM-to-TF
  accuracies 0.144/0.512/0.990/0.989.
- Appendix lines 5-11 specify AdamW, 100 warm-up steps, linear decay, 11
  runs, mean with 0.1/0.9 quantiles, length 100, and a learning-rate sweep
  from \(10^{-4}\) through \(10^0\) by factors of \(\sqrt{10}\).

The public run notebook uses hidden dimensions 4/8/12/16/20/24, batch size 8,
four epochs of 1,000 batches, window 100 for the plotted full-context result,
one head, and a nominal Mamba state argument of 1. Exact saved parameter counts
show that this argument did not reach the model constructor: the effective
state size is the library default 16.

## Figure 5: associative recall with decoding

The exact anchors are `sections/experiments.tex:51-60`,
`sections/tasks.tex:34-40`, and `appendix/experiment_details.tex:17`.
This is not “single-key associative recall.” The input contains word tokens
and a five-bit subsequence encoding a query word. The target is the token after
the last occurrence of that decoded word. Figure 5 uses three-layer models
with hidden dimensions 24 through 768. Its claim is that the hybrid is the
only tested architecture to exceed 0.5, while no pure model exceeds 0.4.

The two figures are separate claim contracts. Their results must not be
conflated.

## Source-to-verdict resolution

The complete Figure 6 contract was rerun at all 24 architecture-width points
and 11 final seeds per point. The first mean-accuracy threshold crossings were
3,684 parameters for SSM-to-TF (0.672583 mean; normal across-seed 95% interval
0.452239--0.892928) and 7,100 parameters for pure TF (0.752170 mean; interval
0.682745--0.821596). The independently recomputed ratio is 1.927253, not 6.

Figure 5's full dimensions 24 through 768 would require three-layer CPU
training at widths 384 and 768. That stage was not run because it is not
feasible within the CPU-only campaign budget. A smaller-width run would be a
proxy and is therefore not used. The exact imported composite is nevertheless
FALSIFIED because its Figure 5 task label contradicts the source and its
Figure 6 numerical ratio contradicts the faithful complete-grid rerun.
