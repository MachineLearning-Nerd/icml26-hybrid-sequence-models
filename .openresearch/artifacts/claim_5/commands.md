# Claim 5 commands and compute

Fixed command on every node:

`uv run --frozen --no-dev python scripts/run_reproduction.py`

Scientific launch:

`orx exp run d47c32bf-6884-4ac4-bbd3-9e299e573106 --backend hf --flavor cpu-upgrade --image ghcr.io/astral-sh/uv:python3.12-bookworm-slim --timeout 14400`

Accepted run: `f3855c20-ecfe-425a-bd66-624f2183921e`

Accepted Git SHA: `d0e944e3008518a793074cf40afd7fce0566f9c1`

Allocation estimate before launch: eight cores. Actual cgroup quota: 8.0
vCPU; eight workers, one Torch thread each. Scientific runtime: 6,183.51
seconds. Fixed-command runtime: 6,197.44 seconds. Dashboard duration: 1h43m.
At the published $0.03/hour cpu-upgrade rate, the approximate compute charge is
$0.052, excluding any platform rounding.

The current static replay uses the same fixed command locally, one core, with
an expected runtime below five minutes.
