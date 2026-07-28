# Claim 6 commands

Fixed command inherited by every node:

```text
uv run --frozen --no-dev python scripts/run_reproduction.py
```

Scientific launch:

```text
orx exp run 15450f40-916c-426c-9ccc-e0dff0651e17 --backend hf --flavor cpu-upgrade --timeout 43200
```

The command is fixed; the committed `reproduction/campaign.json` selects the
Figure 6 stage and its precommitted grid.
