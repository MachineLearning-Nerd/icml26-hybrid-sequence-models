# Claim 6 commands

Fixed command inherited by every node:

```text
uv run --frozen --no-dev python scripts/run_reproduction.py
```

Scientific launch:

```text
orx exp run 6d04b65d-7bca-4aff-8da6-38c30e0ba3f1 --backend hf --flavor cpu-upgrade --image ghcr.io/astral-sh/uv:python3.12-bookworm-slim --timeout 43200
```

The command is fixed; the committed `reproduction/campaign.json` selects the
Figure 6 stage and its precommitted grid.

Static cumulative replay:

```text
orx exp run d7bfc56c-ee05-4b24-905a-98504154f3b9 --backend local
```

The local replay is a one-core, under-five-minute integrity check of frozen
evidence. It does not retrain models.
