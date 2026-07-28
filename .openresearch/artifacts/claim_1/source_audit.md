# Claim 1 source audit

Source hashes and retrieval details are in `../project/source_audit.md`.

The theorem statement is at `sections/func_comp_and_construct.tex` lines 26–28. It assumes an injective map

\[
G:\mathcal V^m\rightarrow\mathcal Y^q
\]

and claims a distribution under which success probability \(1/2\) requires

\[
\sum_i\log|\mathcal S_i|\ge\Omega(m\log|\mathcal V|-q\log|\mathcal Y|).
\]

The paper's prose immediately calls this linear in \(m\). Two exact source facts prevent that conclusion:

1. Injectivity itself forces \(|\mathcal V|^m\le|\mathcal Y|^q\), so the argument inside the displayed \(\Omega\) is always non-positive.
2. The proof at Appendix lines 62–75 derives a Fano bound and then changes the error to \(<1/8\). The theorem statement's success \(1/2\) permits error \(1/2\).

The verifier tests the exact 1/2 threshold. It does not silently strengthen it to 7/8 or replace the \(q,|\mathcal Y|\) terms with a deterministic full-recovery problem.
