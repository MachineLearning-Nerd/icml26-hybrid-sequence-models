# Audit status

This is a mixed, claim-by-claim reproduction audit of *Expressivity–Efficiency
Tradeoffs for Hybrid Sequence Models*. Claims 2–4 are supported within their
explicit mathematical and finite-domain scopes. Claims 1, 5, and 6 are
falsified under the exact imported contracts used by the audit.

- Paper: [Expressivity–Efficiency Tradeoffs for Hybrid Sequence Models](https://arxiv.org/abs/2603.08859)
- Authors: John Cooper, Ilias Diakonikolas, Mingchen Ma, and Frederic Sala
- Repository: [MachineLearning-Nerd/icml26-hybrid-sequence-models](https://github.com/MachineLearning-Nerd/icml26-hybrid-sequence-models)
- Historical evaluator Space: [DineshAI/82EJxJzG6r](https://huggingface.co/spaces/DineshAI/82EJxJzG6r)
- Overall status: PARTIAL_C2_C4_VERIFIED_C1_C5_C6_FALSIFIED_HISTORICAL_SCORE_0_OF_12_NO_CURRENT_SCORE
- C1: FALSIFIED_SCOPED, HIGH confidence
- C2: VERIFIED_SCOPED, MEDIUM confidence
- C3: VERIFIED_SCOPED, MEDIUM confidence
- C4: VERIFIED_SCOPED, MEDIUM confidence
- C5: FALSIFIED_SCOPED, MEDIUM confidence; its strict learned-model separation route remains protocol-blocked
- C6: FALSIFIED_SCOPED, HIGH confidence; the full Figure 5 scale was not rerun
- Historical external score: 0/12, judged on 2026-07-28
- Current score claim: false
- Publication allowed: false
- Official author endorsement: false / not claimed
- Commit identity: MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>
- Recovery bundle SHA-256: b778308e142f0880f7f4d1c2b15db458ffc9d8fb5440955000062086c76e8e93

The audit supports the paper’s central mechanism: recurrent state plus a short
attention window can solve the constructed selective-copying and
associative-recall tasks. It does not support every stronger theorem wording or
the imported numerical 6× claims. Local evidence is not a new judge score.

