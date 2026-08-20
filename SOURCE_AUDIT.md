# Source audit entry point

## Primary source

- Paper: *Expressivity–Efficiency Tradeoffs for Hybrid Sequence Models*
- Authors: John Cooper, Ilias Diakonikolas, Mingchen Ma, and Frederic Sala
- arXiv: [2603.08859](https://arxiv.org/abs/2603.08859)
- HTML source: https://ar5iv.labs.arxiv.org/html/2603.08859
- E-print: https://export.arxiv.org/e-print/2603.08859
- Retrieved: 2026-07-28 17:45:09 UTC
- HTML SHA-256: e35eacd382bd4acf7e4d8547927c398570cbd3ba2a5c2618b0e7e18edae444ad
- E-print SHA-256: e8d22bfd259aaa60385841d8643109ecb66f7eb1081dd76429f5215f05a032e8

The complete source-audit notes and TeX anchors are preserved in
.openresearch/artifacts/project/source_audit.md and the six claim-specific
source_audit.md files.

## Claim anchors

- C1: sections/func_comp_and_construct.tex lines 22–28; proof in
  appendix/missing_proof_lb.tex lines 39–81. The proof’s stated error
  threshold and the injectivity cardinality condition do not support the
  imported positive linear consequence.
- C2: sections/func_comp_and_construct.tex lines 54–60; proof in
  appendix/missing_proof_lb.tex lines 85–104. The witness mechanism is a
  shared final-R suffix with different labels.
- C3: sections/tasks.tex lines 4–8 and 28–31; construction in
  appendix/constructions.tex. The universal quantifier is checked by a
  symbolic certificate plus complete finite domains.
- C4: sections/tasks.tex lines 37–40 and 59–61; construction in
  appendix/constructions.tex. The text contains a theorem-label typo, which
  is disclosed rather than silently corrected.
- C5: sections/experiments.tex and Appendix E.1, Figure 4. The source setup
  uses length 100, 26 ordinary tokens, five number tokens, GPTNeoX attention,
  Mamba, RoPE, one attention head, AdamW, 100 warmup steps, a square-root
  ten learning-rate sweep, and 11 runs.
- C6: sections/experiments.tex and Appendix E.1, Figures 5–6. Figure 5 is
  associative recall with decoding; Figure 6 is multi-key associative recall
  with key length 2 and output after the last final-key occurrence.

## Fidelity boundary

Claims 1–4 are symbolic or finite-domain audits. Claims 5–6 use
paper-anchored CPU experiments with explicit seed and parameter accounting.
They do not claim to reproduce unrecorded hardware, hidden checkpoints, or
behavior beyond the stated finite grids. The original judged Space and its
0/12 result are historical evidence, not author endorsement.

