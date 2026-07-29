#!/usr/bin/env python3
"""Generate deterministic SVG figures for the reproduction report."""

from __future__ import annotations

import argparse
import csv
import json
import math
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / ".openresearch" / "artifacts"
COLORS = {
    "hybrid": "#0f766e",
    "tf": "#c2410c",
    "ssm": "#7c3aed",
    "other": "#2563eb",
    "verified": "#15803d",
    "falsified": "#b91c1c",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(
        path,
        format="svg",
        bbox_inches="tight",
        metadata={"Date": None, "Creator": "OpenResearch reproduction"},
    )
    plt.close(fig)


def setup() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titleweight": "bold",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.18,
            "figure.facecolor": "white",
            "axes.facecolor": "#fcfcfc",
            "svg.fonttype": "none",
        }
    )


def claim6_frontier(output_dir: Path) -> None:
    document = load_json(
        ARTIFACTS / "claim_6" / "raw" / "figure6_full_evidence.json"
    )
    evidence = document["empirical_result"]
    points = evidence["point_summaries"]
    styles = {
        "ssm_tf": ("SSM→TF hybrid", COLORS["hybrid"], "o"),
        "tf_tf": ("TF→TF", COLORS["tf"], "s"),
        "ssm_ssm": ("SSM→SSM", COLORS["ssm"], "^"),
        "tf_ssm": ("TF→SSM", COLORS["other"], "D"),
    }
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    for family, (label, color, marker) in styles.items():
        rows = sorted(
            (
                item["expected_parameters"],
                item["statistics"]["mean_accuracy"],
                item["statistics"]["normal_95_interval_across_seeds"],
            )
            for item in points.values()
            if item["family"] == family
        )
        x = np.array([row[0] for row in rows], dtype=float)
        y = np.array([row[1] for row in rows], dtype=float)
        lower = y - np.array([row[2][0] for row in rows], dtype=float)
        upper = np.array([row[2][1] for row in rows], dtype=float) - y
        ax.errorbar(
            x,
            y,
            yerr=np.vstack([lower, upper]),
            color=color,
            marker=marker,
            linewidth=2,
            markersize=5,
            capsize=2,
            label=f"{label} (reproduction)",
        )
    table = evidence["source_contract"]["paper_table"]
    buckets = np.array([1000, 2000, 6000, 12000], dtype=float)
    ax.plot(
        buckets,
        [table[str(int(value))]["ssm_tf"] for value in buckets],
        linestyle="--",
        color=COLORS["hybrid"],
        alpha=0.6,
        label="SSM→TF (paper table)",
    )
    ax.plot(
        buckets,
        [table[str(int(value))]["tf_tf"] for value in buckets],
        linestyle="--",
        color=COLORS["tf"],
        alpha=0.6,
        label="TF→TF (paper table)",
    )
    ax.axhline(0.60, color="#111827", linestyle=":", linewidth=1.5)
    ax.annotate(
        "hybrid first hit\n3,684 params",
        (3684, 0.6725832353812686),
        xytext=(2500, 0.84),
        arrowprops={"arrowstyle": "->", "color": COLORS["hybrid"]},
        color=COLORS["hybrid"],
        ha="right",
    )
    ax.annotate(
        "pure TF first hit\n7,100 params",
        (7100, 0.7521704923409668),
        xytext=(9700, 0.54),
        arrowprops={"arrowstyle": "->", "color": COLORS["tf"]},
        color=COLORS["tf"],
    )
    ax.text(
        0.99,
        0.03,
        "Observed first-hit ratio: 1.93×  •  paper claim: 6×",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontweight="bold",
        bbox={"facecolor": "#fff7ed", "edgecolor": "#fdba74", "pad": 5},
    )
    ax.set_xscale("log")
    ax.set_ylim(0, 1.04)
    ax.set_xlabel("Trainable parameters (log scale)")
    ax.set_ylabel("Mean valid-token accuracy (11 seeds)")
    ax.set_title("Claim 6: complete Figure 6 grid does not recover the 6× threshold gap")
    ax.legend(ncol=2, fontsize=8, loc="upper left")
    save(fig, output_dir / "claim6_mkar_frontier.svg")


def claim5_selective_copy(output_dir: Path) -> None:
    evidence = load_json(
        ARTIFACTS / "claim_5" / "raw" / "frontier_results.json"
    )
    points = evidence["point_summaries"]
    headline_ids = ["ssm_tf_d8", "tf_tf_d24", "ssm_ssm_d24"]
    labels = ["SSM→TF", "TF→TF", "SSM→SSM"]
    colors = [COLORS["hybrid"], COLORS["tf"], COLORS["ssm"]]
    observed = [points[point]["statistics"]["mean_accuracy"] for point in headline_ids]
    paper_table = evidence["source_contracts"]["paper_table"]
    paper = [
        paper_table["hybrid_approx_2000"],
        paper_table["pure_tf_approx_12000"],
        paper_table["pure_ssm_approx_12000"],
    ]
    params = [points[point]["expected_parameters"] for point in headline_ids]
    first_hits = evidence["threshold_0_90_first_hits"]

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))
    x = np.arange(len(labels))
    width = 0.34
    axes[0].bar(x - width / 2, paper, width, color="#94a3b8", label="Paper table")
    axes[0].bar(x + width / 2, observed, width, color=colors, label="Reproduction")
    for index, (accuracy, count) in enumerate(zip(observed, params, strict=True)):
        axes[0].text(
            index + width / 2,
            accuracy + 0.015,
            f"{accuracy:.3f}\n{count:,}p",
            ha="center",
            fontsize=8,
        )
    axes[0].set_xticks(x, labels)
    axes[0].set_ylim(0, 1.09)
    axes[0].set_ylabel("Mean accuracy")
    axes[0].set_title("Headline points: ordering agrees,\n'match perfect' does not")
    axes[0].legend(fontsize=8, loc="lower left")

    hit_labels = ["SSM→TF", "TF→TF", "SSM→SSM"]
    hit_values = [
        first_hits["ssm_tf"]["expected_parameters"],
        first_hits["tf_tf"]["expected_parameters"],
        first_hits["ssm_ssm"]["expected_parameters"],
    ]
    bars = axes[1].barh(hit_labels, hit_values, color=colors)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("First parameters with mean accuracy ≥ 0.90")
    axes[1].set_title("Calibrated finite-grid first hits")
    for bar, value in zip(bars, hit_values, strict=True):
        ratio = value / hit_values[0]
        axes[1].text(
            value + 350,
            bar.get_y() + bar.get_height() / 2,
            f"{value:,}  ({ratio:.2f}×)",
            va="center",
            fontsize=9,
        )
    axes[1].set_xlim(0, max(hit_values) * 1.25)
    fig.suptitle("Claim 5: selective-copying evidence", fontsize=14, fontweight="bold")
    fig.tight_layout()
    save(fig, output_dir / "claim5_selective_copy.svg")


def theorem_calibration(output_dir: Path) -> None:
    with (ARTIFACTS / "claim_1" / "raw" / "cardinality_grid.csv").open(
        encoding="utf-8"
    ) as handle:
        claim1 = list(csv.DictReader(handle))
    with (ARTIFACTS / "claim_2" / "raw" / "witness_grid.csv").open(
        encoding="utf-8"
    ) as handle:
        claim2 = list(csv.DictReader(handle))

    words_values = [2, 4, 8, 16, 32, 64]
    first_hits = []
    previous = []
    for words in words_values:
        window = 1
        while 1 - Fraction(words - 1, words) ** window < Fraction(99, 100):
            window += 1
        first_hits.append(window)
        previous.append(float(1 - Fraction(words - 1, words) ** (window - 1)))

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    for alphabet_bits in sorted({int(row["alphabet_bits"]) for row in claim1}):
        rows = [row for row in claim1 if int(row["alphabet_bits"]) == alphabet_bits]
        axes[0].plot(
            [int(row["m"]) for row in rows],
            [float(row["expected_printed_rhs_bits"]) for row in rows],
            marker="o",
            label=f"log₂|V|={alphabet_bits}",
        )
    axes[0].set_xlabel("Hidden dimension m")
    axes[0].set_ylabel("m log|V| − q log|Y|")
    axes[0].set_title("Claim 1\ninjectivity makes RHS zero")
    axes[0].set_ylim(-0.1, 1)
    axes[0].legend(fontsize=7)

    ranges = np.array([int(row["dependency_range"]) for row in claim2])
    windows = np.array([int(row["total_window"]) for row in claim2])
    axes[1].scatter(ranges, windows, color=COLORS["other"])
    max_range = int(ranges.max()) + 2
    axes[1].plot([0, max_range], [0, max_range], "k--", linewidth=1)
    axes[1].set_xlabel("Dependency range R")
    axes[1].set_ylabel("Total window W")
    axes[1].set_title("Claim 2\nall witnesses satisfy W < R")

    axes[2].plot(words_values, first_hits, marker="o", color=COLORS["verified"])
    axes[2].plot(
        words_values,
        [math.ceil(value * math.log(100)) + 1 for value in words_values],
        linestyle="--",
        color="#64748b",
        label="certified linear bound",
    )
    axes[2].set_xscale("log", base=2)
    axes[2].set_yscale("log", base=2)
    axes[2].set_xlabel("Word vocabulary |V|")
    axes[2].set_ylabel("First 99% context window")
    axes[2].set_title("Claim 4\nexact first-hit calibration")
    axes[2].legend(fontsize=7)
    fig.suptitle("Theorem calibration: exact arithmetic and complete witnesses", fontweight="bold")
    fig.tight_layout()
    save(fig, output_dir / "theorem_calibration.svg")


def construction_coverage(output_dir: Path) -> None:
    with (ARTIFACTS / "claim_3" / "raw" / "complete_domain_sweep.csv").open(
        encoding="utf-8"
    ) as handle:
        claim3 = list(csv.DictReader(handle))
    labels = [
        f"L={row['length']}, V={row['vocabulary_size']}, N={row['number_tokens']}"
        for row in claim3
    ]
    valid = np.array([int(row["expected_valid_sequences"]) for row in claim3])
    undefined = np.array([int(row["expected_undefined_sequences"]) for row in claim3])

    words_values = [2, 4, 8, 16, 32, 64]
    at_hit = []
    before_hit = []
    for words in words_values:
        window = 1
        while 1 - Fraction(words - 1, words) ** window < Fraction(99, 100):
            window += 1
        at_hit.append(float(1 - Fraction(words - 1, words) ** window))
        before_hit.append(float(1 - Fraction(words - 1, words) ** (window - 1)))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    x = np.arange(len(labels))
    axes[0].bar(x, valid, color=COLORS["verified"], label="valid and correct")
    axes[0].bar(
        x,
        undefined,
        bottom=valid,
        color="#cbd5e1",
        label="undefined, excluded",
    )
    axes[0].set_yscale("log")
    axes[0].set_xticks(x, labels, rotation=25, ha="right", fontsize=8)
    axes[0].set_ylabel("Complete-domain sequences (log scale)")
    axes[0].set_title("Claim 3: 100% on every defined input")
    axes[0].legend(fontsize=8)

    axes[1].plot(
        words_values,
        before_hit,
        marker="x",
        color=COLORS["falsified"],
        label="K−1 (must fail 99%)",
    )
    axes[1].plot(
        words_values,
        at_hit,
        marker="o",
        color=COLORS["verified"],
        label="K (first hit)",
    )
    axes[1].axhline(0.99, linestyle=":", color="#111827")
    axes[1].set_xscale("log", base=2)
    axes[1].set_ylim(0.982, 0.996)
    axes[1].set_xlabel("Word vocabulary |V|")
    axes[1].set_ylabel("Exact success probability")
    axes[1].set_title("Claim 4: first-hit control separates K−1 from K")
    axes[1].legend(fontsize=8)
    fig.suptitle("Construction evidence and negative-control boundaries", fontweight="bold")
    fig.tight_layout()
    save(fig, output_dir / "construction_coverage.svg")


def campaign_overview(output_dir: Path) -> None:
    campaign = load_json(ROOT / "reproduction" / "campaign.json")
    confidence = {
        1: "HIGH",
        2: "MEDIUM",
        3: "MEDIUM",
        4: "MEDIUM",
        5: "MEDIUM",
        6: "HIGH",
    }
    claims = campaign["claims"]
    fig, ax = plt.subplots(figsize=(10.5, 3.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")
    for index, claim in enumerate(claims):
        y = 6 - index
        status = claim["verdict"]
        color = COLORS["verified"] if status == "VERIFIED" else COLORS["falsified"]
        ax.add_patch(
            plt.Rectangle((0.2, y - 0.35), 11.5, 0.7, color="#f8fafc", ec="#e2e8f0")
        )
        ax.text(0.45, y, f"C{claim['id']}", va="center", fontweight="bold")
        ax.text(1.35, y, status, va="center", color=color, fontweight="bold")
        ax.text(3.35, y, confidence[claim["id"]], va="center")
        summary = {
            1: "injection cancels the claimed positive linear term",
            2: "symbolic W < R witness family",
            3: "complete defined-domain construction",
            4: "exact 99% first-hit calibration",
            5: "1.000 vs 0.846 / 0.866 at headline sizes",
            6: "1.93× reproduced threshold gap, not 6×",
        }[claim["id"]]
        ax.text(4.8, y, summary, va="center", fontsize=9)
    ax.text(0.45, 6.65, "Claim", fontweight="bold")
    ax.text(1.35, 6.65, "Verdict", fontweight="bold")
    ax.text(3.35, 6.65, "Confidence", fontweight="bold")
    ax.text(4.8, 6.65, "Decisive evidence", fontweight="bold")
    ax.set_title(
        "Cumulative reproduction verdicts (research evidence, not live judge points)",
        loc="left",
        fontsize=14,
        fontweight="bold",
    )
    save(fig, output_dir / "campaign_overview.svg")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    setup()
    claim6_frontier(output_dir)
    claim5_selective_copy(output_dir)
    theorem_calibration(output_dir)
    construction_coverage(output_dir)
    campaign_overview(output_dir)
    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "figures": sorted(path.name for path in output_dir.glob("*.svg")),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
