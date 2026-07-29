#!/usr/bin/env python3
"""Build deterministic text-only Space release metadata from a passed audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


RELEASE_PATHS = {
    "release/candidate_manifest.sha256",
    "release/final_candidate_audit.json",
    "release/historical_preservation.json",
    "release/release_report.md",
    "release/upload_allowlist.txt",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("audit_json", type=Path)
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    audit = json.loads(args.audit_json.read_text(encoding="utf-8"))
    if audit["status"] != "PASS":
        raise RuntimeError("release metadata requires a passing audit")
    release = candidate / "release"
    release.mkdir(parents=True, exist_ok=True)

    allowlist = sorted(set(audit["upload_allowlist"]) | RELEASE_PATHS)
    (release / "final_candidate_audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (release / "historical_preservation.json").write_text(
        json.dumps(audit["historical_preservation"], indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    (release / "upload_allowlist.txt").write_text(
        "\n".join(allowlist) + "\n", encoding="utf-8"
    )

    missing = [relative for relative in allowlist if not (candidate / relative).is_file()]
    if missing:
        raise RuntimeError(f"allowlisted paths missing: {missing}")
    manifest_rows = [
        f"{sha256(candidate / relative)}  {relative}"
        for relative in allowlist
        if relative != "release/candidate_manifest.sha256"
    ]
    (release / "candidate_manifest.sha256").write_text(
        "\n".join(manifest_rows) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "allowlist_entries": len(allowlist),
                "manifest_entries": len(manifest_rows),
                "manifest_self_exclusion": "release/candidate_manifest.sha256",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
