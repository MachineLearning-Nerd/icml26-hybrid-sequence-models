#!/usr/bin/env python3
"""Audit a Space candidate from its evaluator-visible canonical entrypoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import deque
from pathlib import Path, PurePosixPath


FIXED_COMMAND = "uv run --frozen --no-dev python scripts/run_reproduction.py"
CLAIM_EXPECTATIONS = {
    1: ("FALSIFIED", "HIGH", ["0 bits", "**4**"]),
    2: ("VERIFIED", "MEDIUM", ["1/2 < 2/3", "**5**"]),
    3: ("VERIFIED", "MEDIUM", ["6,266/6,266", "**7**"]),
    4: ("VERIFIED", "MEDIUM", ["127/128", "**9**"]),
    5: ("FALSIFIED", "MEDIUM", ["0.999985", "8.32×", "0.041856"]),
    6: ("FALSIFIED", "HIGH", ["1.927253×", "0/46,392", "**4**"]),
}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SECRET_PATTERNS = [
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|password|secret|hf_token)\b\s*[:=]\s*"
        r"[\"'][^\"'$<{]{8,}[\"']"
    ),
]


class AuditError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_manifest(path: Path) -> list[tuple[str, str]]:
    rows = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            digest, relative = raw.split("  ", 1)
            rows.append((digest, relative))
    return rows


def flatten_tree(node: dict, mapping: dict[str, str]) -> None:
    mapping[node["slug"]] = node["file"]
    for child in node.get("children", []):
        flatten_tree(child, mapping)


def safe_resolve(root: Path, source: str, target: str) -> Path:
    target_path = PurePosixPath(source).parent / PurePosixPath(target)
    normalized = PurePosixPath(*[part for part in target_path.parts if part != "."])
    stack: list[str] = []
    for part in normalized.parts:
        if part == "..":
            if not stack:
                raise AuditError(f"unsafe link from {source}: {target}")
            stack.pop()
        else:
            stack.append(part)
    path = root.joinpath(*stack).resolve()
    if root.resolve() not in path.parents and path != root.resolve():
        raise AuditError(f"link escapes candidate: {source} -> {target}")
    return path


def traverse(root: Path, slug_map: dict[str, str]) -> tuple[list[str], list[str]]:
    queue = deque(["pages/index.md"])
    opened: list[str] = []
    missing: list[str] = []
    seen: set[str] = set()
    while queue:
        relative = queue.popleft()
        if relative in seen:
            continue
        seen.add(relative)
        path = root / relative
        if not path.is_file():
            missing.append(relative)
            continue
        opened.append(relative)
        text = path.read_text(encoding="utf-8")
        targets = LINK_RE.findall(text)
        targets.extend(
            line.strip()
            for line in text.splitlines()
            if line.strip().lower().endswith((".svg", ".png", ".jpg", ".jpeg"))
            and " " not in line.strip()
        )
        for target in targets:
            if target.startswith("#/"):
                slug = target[2:]
                if slug not in slug_map:
                    missing.append(f"{relative} -> unknown slug {slug}")
                else:
                    queue.append(slug_map[slug])
                continue
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0]
            resolved = (
                (root / clean).resolve()
                if clean.startswith(("pages/", "images/"))
                else safe_resolve(root, relative, clean)
            )
            try:
                linked = resolved.relative_to(root.resolve()).as_posix()
            except ValueError as exc:
                raise AuditError(f"link escapes root: {target}") from exc
            if not resolved.is_file():
                missing.append(f"{relative} -> {linked}")
            elif resolved.suffix.lower() in {
                ".md",
                ".json",
                ".csv",
                ".py",
                ".toml",
                ".lock",
                ".svg",
                ".txt",
            } or resolved.name in {"uv.lock", ".python-version"}:
                queue.append(linked)
    return opened, missing


def audit_claim_pages(root: Path, reachable: set[str]) -> dict[str, dict]:
    results: dict[str, dict] = {}
    for claim_id, (verdict, confidence, markers) in CLAIM_EXPECTATIONS.items():
        relative = f"pages/claims/claim-{claim_id}/page.md"
        if relative not in reachable:
            raise AuditError(f"claim page is unreachable: {relative}")
        text = (root / relative).read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        required = [
            verdict,
            confidence,
            "Exact",
            "Source",
            "Assumption" if claim_id in {1, 2, 3, 4} else "contract",
            FIXED_COMMAND,
            "Git SHA",
            "CPU",
            f"reproduction/claim{claim_id}_verifier.py",
            f"reproduction/claim{claim_id}_checker.py",
            f".openresearch/artifacts/claim_{claim_id}/claim_contract.json",
            f".openresearch/artifacts/claim_{claim_id}/checker_output.json",
            f".openresearch/artifacts/claim_{claim_id}/negative_control_output.json",
            *markers,
        ]
        absent = [
            marker
            for marker in required
            if " ".join(marker.split()).lower() not in normalized.lower()
        ]
        if absent:
            raise AuditError(f"claim {claim_id} page missing markers: {absent}")
        results[str(claim_id)] = {
            "page": relative,
            "verdict": verdict,
            "confidence": confidence,
            "required_markers": len(required),
            "status": "COMPLETE",
        }
    return results


def historical_preservation(
    root: Path, manifest: list[tuple[str, str]]
) -> dict[str, dict]:
    mapping: dict[str, dict] = {}
    for digest, relative in manifest:
        current = root / relative
        if not current.is_file():
            raise AuditError(f"protected path missing: {relative}")
        if sha256(current) == digest:
            preserved = relative
            mode = "unchanged canonical path"
        else:
            historical = root / "historical" / "judged_revision" / relative
            if not historical.is_file() or sha256(historical) != digest:
                raise AuditError(f"protected bytes not preserved: {relative}")
            preserved = historical.relative_to(root).as_posix()
            mode = "exact historical copy; canonical navigation updated"
        mapping[relative] = {
            "sha256": digest,
            "preserved_at": preserved,
            "mode": mode,
        }
    return mapping


def changed_text_allowlist(
    root: Path, manifest: list[tuple[str, str]]
) -> list[str]:
    old = dict((relative, digest) for digest, relative in manifest)
    allowed_suffixes = {
        ".css",
        ".csv",
        ".html",
        ".json",
        ".lock",
        ".md",
        ".py",
        ".sha256",
        ".svg",
        ".tex",
        ".toml",
        ".txt",
    }
    special_names = {
        ".gitattributes",
        ".python-version",
        "LICENSE.upstream",
        "uv.lock",
    }
    allowlist = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        relative_parts = PurePosixPath(relative).parts
        if ".cache" in relative_parts or ".venv" in relative_parts:
            continue
        if relative in old and sha256(path) == old[relative]:
            continue
        if path.suffix.lower() not in allowed_suffixes and path.name not in special_names:
            raise AuditError(f"new or changed non-text file: {relative}")
        path.read_text(encoding="utf-8")
        allowlist.append(relative)
    return allowlist


def scan_secrets(root: Path, allowlist: list[str]) -> list[str]:
    findings = []
    for relative in allowlist:
        text = (root / relative).read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{relative}: {pattern.pattern}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument(
        "--protected-manifest",
        type=Path,
        default=Path(".openresearch/artifacts/project/judged_space_manifest.sha256"),
    )
    args = parser.parse_args()
    root = args.candidate.resolve()
    if not root.is_dir():
        raise AuditError(f"candidate directory missing: {root}")

    logbook = json.loads((root / "logbook.json").read_text(encoding="utf-8"))
    if logbook["space_id"] != "DineshAI/82EJxJzG6r":
        raise AuditError("wrong Space id")
    if logbook["root"]["file"] != "pages/index.md":
        raise AuditError("canonical root is not pages/index.md")
    if logbook["root"]["children"][0]["slug"] != "current":
        raise AuditError("current verification is not first in navigation")

    slug_map: dict[str, str] = {}
    flatten_tree(logbook["root"], slug_map)
    opened, missing = traverse(root, slug_map)
    if missing:
        raise AuditError(f"missing traversal targets: {missing}")
    reachable = set(opened)
    claim_pages = audit_claim_pages(root, reachable)

    manifest = parse_manifest(args.protected_manifest.resolve())
    preservation = historical_preservation(root, manifest)
    allowlist = changed_text_allowlist(root, manifest)
    secret_findings = scan_secrets(root, allowlist)
    if secret_findings:
        raise AuditError(f"possible secrets: {secret_findings}")
    if any(".venv" in PurePosixPath(path).parts for path in allowlist):
        raise AuditError("candidate contains an environment")

    result = {
        "status": "PASS",
        "canonical_entrypoint": "pages/index.md",
        "space_id": logbook["space_id"],
        "opened_files": opened,
        "opened_file_count": len(opened),
        "claim_pages": claim_pages,
        "missing_targets": missing,
        "protected_manifest_entries": len(manifest),
        "protected_paths_present": all((root / relative).is_file() for _, relative in manifest),
        "historical_preservation": preservation,
        "upload_allowlist": allowlist,
        "upload_allowlist_entries": len(allowlist),
        "secret_findings": secret_findings,
        "fixed_command": FIXED_COMMAND,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
