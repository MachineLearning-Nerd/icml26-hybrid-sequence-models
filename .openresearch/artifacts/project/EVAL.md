# Baseline evaluation

Expected result: the audit runner exits zero, reports the historical live score as `0/12`, and leaves all six claims `BLOCKED`.

This is an infrastructure baseline, not paper evidence. A passing baseline earns no projected points.

Run command, fixed for every experiment node:

```text
uv run --frozen --no-dev python scripts/run_reproduction.py
```

