# Claim 4 source audit

Source hashes and retrieval details are in `../project/source_audit.md`.

The task is at `sections/tasks.tex` lines 37–40: extract the bit subsequence, decode it to a word token, and output the token following that word's last occurrence. Theorem 4.6 is at lines 59–61. Its heading and task say associative recall with decoding, but its body accidentally says “selective copying.” The appendix restatement at `appendix/constructions.tex` lines 199–201 corrects the task name.

The construction comprises:

1. a Mamba shift state that decodes the bit subsequence (lines 238–288);
2. an attention layer that pairs each previous token with its successor (lines 293–315);
3. an attention layer that matches the decoded word and selects its last occurrence using positional bias (lines 316–327).

The 99% argument is a coupon-collector-style statement that each word appears in a final \(\widetilde O(W)\) window. For a fixed decoded query, only its own occurrence is necessary:

\[
\Pr[\text{query appears in final }K\text{ word slots}]
=1-\left(1-\frac1W\right)^K.
\]

The source alternates between “non-bit tokens drawn uniformly” in the main theorem and a uniform full input in the appendix. The verifier fixes the former, because it is the distribution named by the imported claim, and makes the bit suffix and word mapping explicit.
