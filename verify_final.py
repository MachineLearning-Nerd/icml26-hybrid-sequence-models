#!/usr/bin/env python3
"""Verify the committed publication contract for this repository."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED_STATUS = (
    "PARTIAL_C2_C4_VERIFIED_C1_C5_C6_FALSIFIED_"
    "HISTORICAL_SCORE_0_OF_12_NO_CURRENT_SCORE"
)
EXPECTED_BRANCHES = {
    "audit/claim1-theorem-calibration",
    "audit/claim2-sliding-window-lower-bound",
    "audit/claim3-selective-copying",
    "audit/claim4-associative-recall",
    "audit/claim5-cpu-fidelity-pilot",
    "audit/claim5-selective-copy-frontier",
    "audit/claim5-static-evidence",
    "audit/claim6-mkar-frontier",
    "audit/claim6-mkar-worker-recovery",
    "historical/judged-baseline",
    "main",
    "release/evaluator-candidate",
}
EXPECTED_COMMITS = 30
CANONICAL_IDENTITY = (
    "MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>"
)
CLAIM_IDS = ["C1", "C2", "C3", "C4", "C5", "C6"]


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"verification failed: {message}")


def published_branches() -> set[str]:
    remote = {
        name.removeprefix("origin/")
        for name in git(
            "for-each-ref",
            "refs/remotes/origin",
            "--format=%(refname:short)",
        ).splitlines()
        if name.startswith("origin/") and name != "origin/HEAD"
    }
    if remote:
        return remote
    return set(git("for-each-ref", "refs/heads", "--format=%(refname:short)").splitlines())


def main() -> None:
    claims = load("claims.json")
    verdicts = load("reproduction_verdicts.json")
    manifest = load("EVIDENCE_MANIFEST.json")
    state = load("AUTONOMOUS_STATE.json")
    logbook = load("space/logbook.json")
    verdict_record = load(".openresearch/artifacts/project/verdict_record.json")
    final_audit = load("space/release/final_candidate_audit.json")
    claim1 = load(".openresearch/artifacts/claim_1/checker_output.json")
    claim2 = load(".openresearch/artifacts/claim_2/checker_output.json")
    claim3 = load(".openresearch/artifacts/claim_3/checker_output.json")
    claim4 = load(".openresearch/artifacts/claim_4/checker_output.json")
    claim5 = load(".openresearch/artifacts/claim_5/checker_output.json")
    claim6 = load(".openresearch/artifacts/claim_6/checker_output.json")

    expected_statuses = {
        "C1": "FALSIFIED_SCOPED",
        "C2": "VERIFIED_SCOPED",
        "C3": "VERIFIED_SCOPED",
        "C4": "VERIFIED_SCOPED",
        "C5": "FALSIFIED_SCOPED",
        "C6": "FALSIFIED_SCOPED",
    }
    require(claims["overall_status"] == EXPECTED_STATUS, "claims overall status")
    require(state["overall_status"] == EXPECTED_STATUS, "autonomous state overall status")
    require(
        verdicts["overall_verdict"] == "PARTIAL_C2_C4_VERIFIED_C1_C5_C6_FALSIFIED",
        "overall verdict",
    )
    require([claim["id"] for claim in claims["claims"]] == CLAIM_IDS, "claim ordering")
    require(
        {claim["id"]: claim["status"] for claim in claims["claims"]} == expected_statuses,
        "claim statuses",
    )
    require(verdicts["claim_statuses"] == expected_statuses, "verdict statuses")
    require(
        all((ROOT / path).exists() for path in manifest["required_paths"]),
        "manifest paths",
    )

    require(logbook["space_id"] == "DineshAI/82EJxJzG6r", "Space identity")
    require(logbook["revision"] == "current-six-claim-evidence", "current logbook revision")
    require(verdict_record["space_id"] == "DineshAI/82EJxJzG6r", "historical verdict identity")
    require(verdict_record["score"] == "0/12", "historical score")
    require(final_audit["status"] == "PASS", "release audit status")
    require(final_audit["canonical_entrypoint"] == "pages/index.md", "release entrypoint")
    require(final_audit["missing_targets"] == [], "release missing targets")
    require(final_audit["secret_findings"] == [], "release secret findings")

    require(claim1["injective"] is True, "C1 injectivity")
    require(claim1["printed_rhs_bits"] == 0.0, "C1 printed right-hand side")
    require(claim1["best_uniform_constant_success"] == 0.5, "C1 counterexample")
    require(claim2["premise_total_window_below_r"] is True, "C2 premise")
    require(claim2["total_window"] < claim2["dependency_range"], "C2 total window")
    require(claim2["max_accuracy_on_uniform_pair"] < claim2["target_threshold"], "C2 threshold")
    require(
        claim3["valid_sequences"] == claim3["correct_sequences"] == 240,
        "C3 checker finite case",
    )
    require(claim3["accuracy_on_defined_domain"] == 1.0, "C3 accuracy")
    require(
        claim4["success_probability"] >= claim4["target_probability"]
        > claim4["previous_success_probability"],
        "C4 calibration",
    )
    require(claim4["direct_correct_when_defined"] == 254, "C4 direct construction")
    require(claim5["verdict"] == "FALSIFIED", "C5 verdict")
    require(claim5["strict_route_status"] == "BLOCKED", "C5 strict-route boundary")
    require(
        claim5["source_route"]["paper_table"] == {
            "hybrid_approx_2000": 0.999,
            "pure_ssm_approx_12000": 0.931,
            "pure_tf_approx_12000": 0.923,
        },
        "C5 source table",
    )
    require(claim5["negative_control"]["passed"] is True, "C5 negative control")
    require(claim6["verdict"] == "FALSIFIED", "C6 verdict")
    require(claim6["figure_5_full_scale_status"].startswith("Not rerun"), "C6 Figure 5 boundary")
    require(
        abs(claim6["pure_tf_to_ssm_tf_first_hit_parameter_ratio"] - 1.9272529858849077)
        < 1e-12,
        "C6 observed ratio",
    )
    require(claim6["random_target_control_accuracy"] == 0.0, "C6 negative control")

    branches = published_branches()
    require(branches == EXPECTED_BRANCHES, "published branches")
    require(not any(branch.startswith("orx/") for branch in branches), "legacy orx branch")
    require(int(git("rev-list", "--all", "--count")) == EXPECTED_COMMITS, "reachable commit count")
    identities = git("log", "--all", "--format=%an <%ae>\n%cn <%ce>").splitlines()
    require(identities and all(identity == CANONICAL_IDENTITY for identity in identities), "canonical identity")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    require("STATUS.md" in readme and "CLAIM_EVIDENCE.md" in readme, "README dossier links")
    require("MachineLearning-Nerd@users.noreply.github.com" in readme, "README attribution")

    print(
        "FINAL_AUDIT=VERIFIED "
        f"branches={len(branches)} commits={EXPECTED_COMMITS} "
        "claims=C2:C4_verified_scoped,C1:C5:C6_falsified_scoped "
        "historical_score=0/12 current_score_claim=false publication_allowed=false"
    )


if __name__ == "__main__":
    main()
