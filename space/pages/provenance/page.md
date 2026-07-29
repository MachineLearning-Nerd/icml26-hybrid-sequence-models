# Commands and provenance

## Fixed scientific contract

Every experiment node reports the same command from `orx exp status`:

```text
uv run --frozen --no-dev python scripts/run_reproduction.py
```

The command is implemented by
[scripts/run_reproduction.py](../../scripts/run_reproduction.py). The
environment is Python 3.12, `uv`, one repository-level `.venv`,
[pyproject.toml](../../pyproject.toml), and [uv.lock](../../uv.lock).
The runner validates the protected Space manifest, runs all current claim
verifiers, and requires its mutation control to exit nonzero.

## Paper and code provenance

- Paper: arXiv 2603.08859.
- Source URL: `https://export.arxiv.org/e-print/2603.08859`.
- Retrieval: 2026-07-28 with User-Agent
  `OpenResearch-Reproduction/1.0`.
- Source SHA-256:
  `e8d22bfd259aaa60385841d8643109ecb66f7eb1081dd76429f5215f05a032e8`.
- HTML SHA-256:
  `e35eacd382bd4acf7e4d8547927c398570cbd3ba2a5c2618b0e7e18edae444ad`.
- Official public code:
  `https://github.com/SprocketLab/hybrid-expressivity`.
- Audited official code SHA:
  `7beeb0de80f89eb5d75301aef8e97ee9b36ca999`.

## Formal launch commands

| Node | Launch command | Git SHA | Result | CPU/runtime |
|---|---|---|---|---|
| Baseline audit | `orx exp run 543d8108-22a0-405b-a16b-be0f1e1b485e --backend local` | `2b8b302ebe678190a70d94a05a225ee5ec34f152` | PASS | Local, one-core estimate, 26 s |
| Claim 1 | `orx exp run 74447983-8e8a-4356-9917-606412a71308 --backend local` | `fedeec5acb73402a70fcf2aab2ba5e94931a61bd` | FALSIFIED/HIGH | Local, one core, 10 s |
| Claim 2 | `orx exp run 9e2473c2-58e0-4bf7-8a82-2820b65f7fc2 --backend local` | `ad7ec170730798cd2f2eee19d5e2346f4a45a0ae` | VERIFIED/MEDIUM | Local, one core, 5 s |
| Claim 3 | `orx exp run 21179da6-b453-4bcb-8813-67a466097b02 --backend local` | `83a5535df35815b0e607da69774026b15292c2f7` | VERIFIED/MEDIUM | Local, one core, 5 s |
| Claim 4 | `orx exp run 7ef99447-791a-4e39-af50-204157fe1bc5 --backend local` | `efd023d8da4425517961e18d2c7656ff2994ad0a` | VERIFIED/MEDIUM | Local, one core, 5 s |
| Claim 5 learned frontier | `orx exp run d47c32bf-6884-4ac4-bbd3-9e299e573106 --backend hf --flavor cpu-upgrade --image ghcr.io/astral-sh/uv:python3.12-bookworm-slim --timeout 14400` | `d0e944e3008518a793074cf40afd7fce0566f9c1` | FALSIFIED/MEDIUM | HF cpu-upgrade, 8.0 CPUs, eight one-thread workers, 6,183.510 s |
| Claim 6 learned grid | `orx exp run 6d04b65d-b6ec-4897-b976-ca0da6c080eb --backend hf --flavor cpu-upgrade --image ghcr.io/astral-sh/uv:python3.12-bookworm-slim --timeout 43200` | `133ddebd7a6888bde8abe4e511e09a966a506828` | Scientific PASS | HF cpu-upgrade, 8.0 CPUs allocated, six one-thread workers, 14,432.196 s |
| Cumulative winner | `orx exp run d7bfc56c-ee05-4b24-905a-98504154f3b9 --backend local` | `8ba5e099657cd2b61b3201daa11692736cfb083a` | All six PASS | Local, one-core estimate, 30 s dashboard / 26.024723 s verifier |

The first Claim 6 implementation used eight persistent workers, stalled after
partial completion, and was cancelled. The accepted recovery recycles six
one-thread workers after every job and reruns the complete grid. The stalled
output is not scientific evidence.

## Seed and allocation record

Claims 1–4 are deterministic and use no seeds. Claim 5 uses calibration seeds
260350001–260350002, frontier seeds 260351001–260351003, headline seeds
260352001–260352011, and control seed 260359999. Claim 6 uses calibration
seeds 260360001–260360002, final seeds 260361001–260361011, and control seed
260369999.

Accepted HF scientific runtime totals 20,615.706 seconds (5 h 43 min 36 s).
The provider's monetary cost is not exposed by `orx`, so no cost is invented.
No GPU was requested or used.

## Protected historical state

Previous live score: 0/12. Protected Space SHA:
`9449686999e15049fa1e258517852b9f2a00bda1`. The original manifest contains
13 files and is available at
[judged_space_manifest.sha256](../../.openresearch/artifacts/project/judged_space_manifest.sha256).
The old file set is retained as a subset of the candidate.
