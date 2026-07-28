# Paper source audit

Retrieved with the explicit User-Agent `OpenResearch-Reproduction/1.0 (paper audit; contact via GitHub repository)` on 2026-07-28 at 17:45:09 UTC.

| Source | SHA-256 |
| --- | --- |
| `https://ar5iv.labs.arxiv.org/html/2603.08859` | `e35eacd382bd4acf7e4d8547927c398570cbd3ba2a5c2618b0e7e18edae444ad` |
| `https://export.arxiv.org/e-print/2603.08859` | `e8d22bfd259aaa60385841d8643109ecb66f7eb1081dd76429f5215f05a032e8` |

The source bundle anchors below refer to the authors' TeX files.

## Claim 1 — Theorem 3.3

Anchor: `sections/func_comp_and_construct.tex`, assumption at lines 22–24 and theorem at lines 26–28; proof in `appendix/missing_proof_lb.tex`, lines 39–81.

- Domain: \(F:\mathcal V^m\times\mathcal V^n\to\mathcal Y\).
- Assumption: there is a set \(Q=\{v^{(i)}\}_{i=1}^q\) for which \(G(u)=(F(u,v^{(1)}),\ldots,F(u,v^{(q)}))\) is injective.
- Quantifier: there exists a distribution over \((u,v)\) such that every composition of \(k\) SSM layers computing \(F\) with probability \(1/2\) must satisfy
  \(\sum_i\log|\mathcal S_i|\ge\Omega(m\log|\mathcal V|-q\log|\mathcal Y|)\).
- Material source issue: the proof invokes Fano's inequality and then explicitly sets error \(<1/8\), which is success \(>7/8\), not the theorem's stated success \(1/2\). Moreover, injectivity implies \(|\mathcal Y|^q\ge|\mathcal V|^m\), hence \(q\log|\mathcal Y|\ge m\log|\mathcal V|\); the displayed asymptotic argument is non-positive and cannot establish the prose claim of linear growth in \(m\).

## Claim 2 — Theorem 3.7

Anchor: `sections/func_comp_and_construct.tex`, assumption at lines 54–56 and theorem at lines 58–60; proof in `appendix/missing_proof_lb.tex`, lines 85–104.

- Assumption: there are two length-\(L\) sequences identical on positions \(L-R+1{:}L\) but with different required outputs.
- Quantifier: there exists a two-point input distribution such that every \(k\)-layer sliding-window Transformer computing \(F\) with probability \(2/3\) has \(\sum_i W_i\ge R\).
- Proof mechanism: if the total receptive field is below \(R\), the two inputs induce the same final representation, so one deterministic output is wrong on at least half of the two-point distribution.

## Claim 3 — Theorem 4.3

Anchor: `sections/tasks.tex`, selective-copying definition at lines 4–8 and theorem at lines 28–31; construction in `appendix/constructions.tex`.

- Universal quantifier: the two-layer Mamba-then-attention construction must solve **every** input in \(\mathcal V^L\).
- Resources: \(d=O(\max(\log|\mathcal V|,\log L))\), Mamba state space \(O(|\mathcal V|)\), attention window \(O(N)\), and working memory \(\widetilde O(N)\).
- A finite random test alone cannot verify this universal claim; the campaign requires a symbolic construction checker plus exhaustive complete-domain checks where finite.

## Claim 4 — Theorem 4.6

Anchor: `sections/tasks.tex`, associative-recall-with-decoding definition at lines 37–40 and theorem at lines 59–61; restatement and construction in `appendix/constructions.tex`.

- Distribution: non-bit tokens are uniform; the decoding bits define the queried word token.
- Quantifier: a three-layer Mamba-plus-two-attention construction succeeds with probability 99%.
- Resources: \(d=O(\max(\log|\mathcal V|,\log L))\), Mamba state space \(O(|\mathcal V|)\), and attention window \(\widetilde O(|\mathcal V|)\).
- Source typo: the main theorem says "solve the selective copying task"; its section, definition, proof restatement, and construction all say associative recall with decoding. The reproduction will test the latter and disclose the typo.

## Claim 5 — Figure 4

Anchor: `sections/experiments.tex`, selective-copy table and prose; Appendix E.1.

- Paper setup: length 100, number tokens 5–10, 26 ordinary tokens, default token dimension 12, GPTNeoX attention, Mamba SSM, RoPE, single head, state expansion 1, AdamW, 100 warmup steps, linear decay, learning-rate sweep \(10^{-4}\) to \(10^0\) by \(\sqrt{10}\), 11 runs, and training to convergence.
- Reported table: at about 2,000 parameters, SSM→TF has 0.999 accuracy while pure TF and SSM have 0.352 and 0.305; at about 12,000 parameters, pure TF and SSM have 0.923 and 0.931. The prose describes an approximately \(6\times\) parameter advantage at 90% accuracy.

## Claim 6 — Figures 5–6

Anchor: `sections/experiments.tex`, associative-recall-with-decoding and MKAR sections; Appendix E.1.

- MKAR definition: query length \(k=2\); output the token after the last occurrence of the final key.
- Paper setup: length 100, vocabulary 8, token dimensions around 12, otherwise the same 11-run training protocol.
- Reported MKAR table: at about 2,000 parameters SSM→TF is 0.512 versus pure TF 0.159; at about 6,000 it is 0.990 versus pure TF 0.230; pure TF reaches 0.668 around 12,000. The prose states about 60% accuracy with \(6\times\) fewer parameters.
- Figure 5 is a separate associative-recall-with-decoding result: three-layer models near one million parameters, hybrid above 0.5, pure models below 0.4. The imported judge claim conflates this with MKAR; both components must be reported separately.

