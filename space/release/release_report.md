# Release report

- Previous live judged score: **0/12**
- Conservative projected score range after the proposed change: **6–12/12**
- Best-supported possible new score: **12/12 (forecast, not a judge result)**

The projection reflects six terminal, reproducible research verdicts and a
complete evaluator-visible traversal. The range remains wide because four
claims have MEDIUM confidence, two falsifications turn on exact imported
wording or source interpretation, and only the live evaluator can award
points.

| Claim | Current points | Possible points | Confidence | Evidence status | Basis and remaining risk |
|---|---:|---:|---|---|---|
| 1 | 0 | 2 | HIGH | FALSIFIED | Injection makes the claimed positive linear term non-positive; exact 1/2 constant-state counterexample. Risk: evaluator may score only the vacuous printed inequality rather than the imported linear consequence. |
| 2 | 0 | 2 | MEDIUM | VERIFIED | Symbolic W<R witness proof and eight independently checked cases. Risk: the paper omits a formal sliding-window indexing definition. |
| 3 | 0 | 2 | MEDIUM | VERIFIED | Corrected finite-temperature construction, symbolic resources, and 6,266/6,266 defined inputs. Risk: source has undefined inputs and an indexing defect. |
| 4 | 0 | 2 | MEDIUM | VERIFIED | Exact rational first-hit calibration and exhaustive W=2 construction. Risk: source distribution wording and absent-query target are ambiguous. |
| 5 | 0 | 2 | MEDIUM | FALSIFIED | Source table and 11-seed rerun contradict “match perfect”; calibrated gaps are 8.32×/9.61×. Risk: evaluator may treat “roughly 6×” as qualitative rather than exact. |
| 6 | 0 | 2 | HIGH | FALSIFIED | Complete 24-point × 11-seed Figure 6 rerun gives 1.927×, and Figure 5 is misidentified in the imported claim. Risk: full Figure 5 widths 384/768 remain unrun. |

## Current status

Current total score: **0/12**. Conservative projected total: **6–12/12**.
Best-supported possible total: **12/12, forecast only**. All six claims changed
from INCONCLUSIVE to evidence-backed terminal research verdicts. No claim is
BLOCKED.

The exact publication action is a text-only commit to the existing
`DineshAI/82EJxJzG6r` Space. No second Space will be created. The 13 protected
paths remain present; changed entrypoint bytes have exact historical copies.

## Pre-upload summary

| Claim | Status | Expected points | Confidence | Expected evaluator status |
|---|---|---:|---|---|
| 1 | FALSIFIED | 0–2 | HIGH | Exact counterexample and derivation discoverable |
| 2 | VERIFIED | 0–2 | MEDIUM | Symbolic certificate discoverable |
| 3 | VERIFIED | 0–2 | MEDIUM | Complete-domain construction discoverable |
| 4 | VERIFIED | 0–2 | MEDIUM | Exact first-hit certificate discoverable |
| 5 | FALSIFIED | 0–2 | MEDIUM | Source/rerun contradiction discoverable |
| 6 | FALSIFIED | 0–2 | HIGH | Complete Figure 6 contradiction discoverable; Figure 5 limitation explicit |

Conservative projected total: **6–12/12**. Best-supported possible score:
**12/12 (forecast)**. Remaining BLOCKED risk: none scientifically; evaluator
interpretation risks remain as listed above.

## Experiment tree and winner

The tree is a descending sequence of small decision rounds: protected baseline;
Claims 1–4 theorem/construction nodes; Claim 5 pilot, learned frontier, and
static replay; Claim 6 first attempt, recycled-worker recovery, and static
cumulative freeze. The winning branch is
`orx/claim-6-faithful-decoding-recall-benchmark` at Git SHA
`8ba5e099657cd2b61b3201daa11692736cfb083a`.

Accepted claim results:

- Claim 1 FALSIFIED/HIGH
- Claim 2 VERIFIED/MEDIUM
- Claim 3 VERIFIED/MEDIUM
- Claim 4 VERIFIED/MEDIUM
- Claim 5 FALSIFIED/MEDIUM
- Claim 6 FALSIFIED/HIGH

## Commands executed for formal evidence

Fixed command on every node:

```text
uv run --frozen --no-dev python scripts/run_reproduction.py
```

Formal launches:

```text
orx exp run 543d8108-22a0-405b-a16b-be0f1e1b485e --backend local
orx exp run 74447983-8e8a-4356-9917-606412a71308 --backend local
orx exp run 9e2473c2-58e0-4bf7-8a82-2820b65f7fc2 --backend local
orx exp run 21179da6-b453-4bcb-8813-67a466097b02 --backend local
orx exp run 7ef99447-791a-4e39-af50-204157fe1bc5 --backend local
orx exp run d47c32bf-6884-4ac4-bbd3-9e299e573106 --backend hf --flavor cpu-upgrade --image ghcr.io/astral-sh/uv:python3.12-bookworm-slim --timeout 14400
orx exp run 15450f40-916c-426c-9ccc-e0dff0651e17 --backend hf --flavor cpu-upgrade --timeout 43200
orx exp cancel 15450f40-916c-426c-9ccc-e0dff0651e17
orx exp run 6d04b65d-b6ec-4897-b976-ca0da6c080eb --backend hf --flavor cpu-upgrade --image ghcr.io/astral-sh/uv:python3.12-bookworm-slim --timeout 43200
orx exp run d7bfc56c-ee05-4b24-905a-98504154f3b9 --backend local
```

Evidence and release validation:

```text
uv run --frozen --no-dev python reproduction/claim1_verifier.py
uv run --frozen --no-dev python reproduction/claim2_verifier.py
uv run --frozen --no-dev python reproduction/claim3_verifier.py
uv run --frozen --no-dev python reproduction/claim4_verifier.py
uv run --frozen --no-dev python reproduction/claim5_verifier.py
uv run --frozen --no-dev python reproduction/claim6_verifier.py
uv run --frozen --no-dev python reproduction/claim6_verifier.py --negative-control
uv run --frozen --no-dev marimo check notebooks/hybrid_tradeoffs_tutorial.py
uv run --frozen --no-dev python scripts/generate_report_figures.py --output-dir reports/full-reproduction/images
uv run --frozen --no-dev python scripts/audit_release_candidate.py .openresearch/candidate_space
```

Run monitoring and evidence extraction used `orx exp wait`, `orx runs`, and
`orx logs` for every formal run. Startup audit used `orx projects --json`,
`orx project view`, all mandated `orx skill` reads, Git status/SHA/branch
inspection, disk inspection, environment-name-only inspection, explicit
User-Agent paper retrieval, exact-space verdict filtering, and exact-revision
Space download.

## Evidence paths

- Canonical Space entrypoint: `space/pages/index.md`
- Six claim pages: `space/pages/claims/claim-{1..6}/page.md`
- Executable sources: `space/reproduction/`, `space/scripts/`
- Raw evidence: `space/.openresearch/artifacts/claim_{1..6}/`
- Illustrated report: `reports/full-reproduction/report.md`
- Tutorial notebook: `notebooks/hybrid_tradeoffs_tutorial.py`
- Visibility matrix: `space/pages/visibility/page.md`
- Blind review: `space/pages/red-team/page.md`
- Full traversal JSON: `space/release/final_candidate_audit.json`
- Upload allowlist: `space/release/upload_allowlist.txt`
- Candidate hashes: `space/release/candidate_manifest.sha256`

## CPU runtime and cost

Short theorem/static runs used a one-core estimate and completed within five
minutes. Accepted scientific HF runs:

| Claim | Allocation | Runtime |
|---|---|---:|
| 5 | HF cpu-upgrade, 8.0 CPUs, eight one-thread workers | 6,183.510 s |
| 6 | HF cpu-upgrade, 8.0 CPUs allocated, six one-thread workers | 14,432.196 s |

Accepted HF scientific runtime totals 20,615.706 seconds
(5 h 43 min 36 s). The provider's monetary charge is not exposed by `orx`;
cost is recorded as **unavailable**, not estimated. No GPU was used.

## Release-gate record

- Six terminal verdicts: complete.
- Cumulative regression: PASS at winning SHA.
- Every previous judge criticism answered inline: complete.
- Raw data and fixed command: complete.
- Negative controls fail as intended: complete.
- No proxy described as full scale: complete.
- All 13 protected paths remain: complete.
- `logbook.json` and linked data parse: complete.
- Text-only allowlist and SHA-256 manifest: prepared.
- Secret scan: zero findings.
- Canonical traversal: all six visibility rows complete.
- Evaluator-blind review: repeated after fixes; zero missing targets.

The old/new subset check is path-complete (13/13). `README.md`,
`logbook.json`, and `pages/index.md` changed to expose current verification;
their exact judged bytes are preserved under
`historical/judged_revision/`. Every other protected path remains byte-identical
at its original location.

The exact Hugging Face upload allowlist is
`space/release/upload_allowlist.txt`. Only those text files will be committed
to the existing Space.
