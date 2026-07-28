#!/usr/bin/env python3
"""Deterministic CPU harness around the authors' Figure 4--6 model code."""

from __future__ import annotations

import json
import math
import multiprocessing
import os
import platform
import random
import statistics
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
from torch.optim import AdamW
from transformers import get_scheduler

from reproduction.upstream_hybrid_expressivity.data_utils import (
    EvalDataset,
    TrainDataset,
    get_tokenizer,
)
from reproduction.upstream_hybrid_expressivity.models import (
    HybridConfig,
    HybridForCausalLM,
)

_INTEROP_CONFIGURED = False


def cgroup_cpu_quota() -> float | None:
    """Return the enforced container CPU quota when cgroups expose it."""
    cpu_max = Path("/sys/fs/cgroup/cpu.max")
    if cpu_max.is_file():
        quota, period = cpu_max.read_text(encoding="utf-8").strip().split()
        if quota != "max":
            return int(quota) / int(period)
    quota_path = Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
    period_path = Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us")
    if quota_path.is_file() and period_path.is_file():
        quota = int(quota_path.read_text(encoding="utf-8").strip())
        period = int(period_path.read_text(encoding="utf-8").strip())
        if quota > 0:
            return quota / period
    return None


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


def attention_window_mask(length: int, window: int) -> torch.Tensor:
    ones = torch.ones((length, length))
    return (
        torch.triu(ones, diagonal=0) - torch.triu(ones, diagonal=window)
    ).T


def make_tokenizer(task: str, vocabulary: int, number_tokens: int):
    args = SimpleNamespace(
        model=None,
        train_task=task,
        num_vocab=vocabulary,
        num_numbers=number_tokens,
    )
    return get_tokenizer(args)


def make_model(
    *,
    layers: list[str],
    hidden_size: int,
    vocabulary_size: int,
    state_size: int,
    expansion: int,
) -> HybridForCausalLM:
    config = HybridConfig(
        layers=layers,
        bos_token_id=0,
        eos_token_id=0,
        hidden_size=hidden_size,
        intermediate_size=hidden_size * 4,
        num_attention_heads=1,
        state_size=state_size,
        vocab_size=vocabulary_size,
        expand=expansion,
    )
    return HybridForCausalLM(config)


def count_parameters(model: torch.nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)


def masked_loss(
    labels: torch.Tensor, logits: torch.Tensor, valid_mask: torch.Tensor
) -> torch.Tensor:
    raw = torch.nn.functional.cross_entropy(
        logits.reshape(-1, logits.shape[-1]),
        labels.reshape(-1),
        reduction="none",
    ).reshape_as(labels)
    return (raw * valid_mask).sum() / valid_mask.sum()


def evaluate(
    model: torch.nn.Module,
    tokenizer,
    attention_mask: torch.Tensor,
    *,
    task: str,
    sequence_length: int,
    sampled_length: int,
    batches: int,
    batch_size: int,
    probability: float,
    seed: int,
) -> dict:
    seed_everything(seed)
    dataset = EvalDataset(
        tokenizer,
        train_task=task,
        sequence_length=sequence_length,
        min_subseq_length=sampled_length,
        max_subseq_length=sampled_length,
        num_examples=batches,
        batch_size=batch_size,
        p=probability,
    )
    correct = 0
    valid = 0
    exact_sequences = 0
    defined_sequences = 0
    model.eval()
    with torch.no_grad():
        for batch_index in range(batches):
            batch = dataset[batch_index]
            logits = model(
                batch["input_ids"],
                attention_mask=attention_mask,
                return_dict=True,
            )["logits"]
            predictions = logits.argmax(dim=-1)
            mask = batch["mask"].bool()
            correct += int(((predictions == batch["output_ids"]) & mask).sum())
            valid += int(mask.sum())
            for row in range(batch_size):
                row_mask = mask[row]
                if int(row_mask.sum()) == 0:
                    continue
                defined_sequences += 1
                exact_sequences += int(
                    torch.equal(
                        predictions[row][row_mask],
                        batch["output_ids"][row][row_mask],
                    )
                )
    accuracy = correct / valid
    standard_error = math.sqrt(accuracy * (1 - accuracy) / valid)
    return {
        "accuracy": accuracy,
        "correct_tokens": correct,
        "valid_tokens": valid,
        "normal_95_interval": [
            max(0.0, accuracy - 1.96 * standard_error),
            min(1.0, accuracy + 1.96 * standard_error),
        ],
        "exact_sequence_accuracy": exact_sequences / defined_sequences,
        "exact_sequences": exact_sequences,
        "defined_sequences": defined_sequences,
        "sampled_length": sampled_length,
        "padded_sequence_length": sequence_length,
        "seed": seed,
    }


def evaluate_preserving_rng(*args, **kwargs) -> dict:
    python_state = random.getstate()
    numpy_state = np.random.get_state()
    torch_state = torch.random.get_rng_state()
    try:
        return evaluate(*args, **kwargs)
    finally:
        random.setstate(python_state)
        np.random.set_state(numpy_state)
        torch.random.set_rng_state(torch_state)


def train_selective_copy_job(job: dict) -> dict:
    """Train one isolated Figure 4 configuration inside a spawned process."""
    global _INTEROP_CONFIGURED
    started = time.perf_counter()
    torch.set_num_threads(int(job["torch_threads"]))
    if not _INTEROP_CONFIGURED:
        torch.set_num_interop_threads(1)
        _INTEROP_CONFIGURED = True
    seed_everything(int(job["seed"]))

    tokenizer = make_tokenizer("var-copy", 26, 5)
    model = make_model(
        layers=list(job["layers"]),
        hidden_size=int(job["hidden_size"]),
        vocabulary_size=len(tokenizer),
        state_size=int(job["state_size"]),
        expansion=2,
    )
    parameter_count = count_parameters(model)
    expected = int(job["expected_parameters"])
    if parameter_count != expected:
        raise RuntimeError(
            f"{job['job_id']} parameter count {parameter_count}, expected {expected}"
        )

    steps = int(job["steps"])
    dataset = TrainDataset(
        tokenizer,
        task="var-copy",
        sequence_length=100,
        min_subseq_length=97,
        max_subseq_length=98,
        num_examples=steps,
        batch_size=8,
        p=0.2,
    )
    mask = attention_window_mask(100, 20)
    optimizer = AdamW(
        model.parameters(),
        lr=float(job["learning_rate"]),
        weight_decay=0.1,
    )
    scheduler = get_scheduler(
        name="linear",
        optimizer=optimizer,
        num_warmup_steps=100,
        num_training_steps=4000,
    )
    optimizer.zero_grad(set_to_none=True)
    losses: list[float] = []
    epoch_losses: list[float] = []
    training_curve: list[dict] = []
    random_targets = bool(job.get("random_targets", False))

    for step in range(1, steps + 1):
        batch = dataset[step - 1]
        labels = batch["output_ids"]
        if random_targets:
            labels = labels.clone()
            replacement = torch.randint(
                low=0,
                high=len(tokenizer),
                size=labels.shape,
            )
            labels[batch["mask"].bool()] = replacement[batch["mask"].bool()]
        logits = model(
            batch["input_ids"],
            attention_mask=mask,
            return_dict=True,
        )["logits"]
        loss = masked_loss(labels, logits, batch["mask"])
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad(set_to_none=True)
        loss_value = float(loss.detach())
        losses.append(loss_value)
        epoch_losses.append(loss_value)

        if step % 1000 == 0 or step == steps:
            curve_row = {
                "step": step,
                "mean_loss_since_previous_checkpoint": statistics.fmean(epoch_losses),
                "learning_rate": optimizer.param_groups[0]["lr"],
            }
            epoch_eval_batches = int(job.get("epoch_evaluation_batches", 0))
            if epoch_eval_batches:
                curve_row["held_out"] = evaluate_preserving_rng(
                    model,
                    tokenizer,
                    mask,
                    task="var-copy",
                    sequence_length=100,
                    sampled_length=97,
                    batches=epoch_eval_batches,
                    batch_size=8,
                    probability=0.2,
                    seed=int(job["evaluation_seed"]),
                )
                model.train()
            training_curve.append(curve_row)
            epoch_losses = []

    final_evaluation = evaluate_preserving_rng(
        model,
        tokenizer,
        mask,
        task="var-copy",
        sequence_length=100,
        sampled_length=97,
        batches=int(job["final_evaluation_batches"]),
        batch_size=8,
        probability=0.2,
        seed=int(job["evaluation_seed"]),
    )
    runtime = time.perf_counter() - started
    output = {
        "job_id": job["job_id"],
        "point_id": job["point_id"],
        "phase": job["phase"],
        "layers": list(job["layers"]),
        "hidden_size": int(job["hidden_size"]),
        "effective_state_size": int(job["state_size"]),
        "nominal_state_size": 1,
        "parameters": parameter_count,
        "learning_rate": float(job["learning_rate"]),
        "seed": int(job["seed"]),
        "evaluation_seed": int(job["evaluation_seed"]),
        "steps": steps,
        "random_targets": random_targets,
        "mean_training_loss": statistics.fmean(losses),
        "final_training_loss": losses[-1],
        "training_curve": training_curve,
        "final_evaluation": final_evaluation,
        "runtime_seconds": runtime,
        "torch_threads": torch.get_num_threads(),
        "cgroup_cpu_quota": cgroup_cpu_quota(),
        "cpu_affinity": (
            len(os.sched_getaffinity(0))
            if hasattr(os, "sched_getaffinity")
            else None
        ),
    }
    print(
        "FIGURE4_JOB_COMPLETE "
        + json.dumps(
            {
                "job_id": output["job_id"],
                "parameters": parameter_count,
                "mean_training_loss": output["mean_training_loss"],
                "accuracy": final_evaluation["accuracy"],
                "runtime_seconds": runtime,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return output


def run_parallel_jobs(jobs: list[dict], workers: int) -> list[dict]:
    results: list[dict] = []
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=workers, mp_context=context) as executor:
        futures = {
            executor.submit(train_selective_copy_job, job): job["job_id"]
            for job in jobs
        }
        for future in as_completed(futures):
            results.append(future.result())
    return sorted(results, key=lambda row: row["job_id"])


def train_mkar_job(job: dict) -> dict:
    """Train one isolated Figure 6 multi-key associative-recall model."""
    global _INTEROP_CONFIGURED
    started = time.perf_counter()
    torch.set_num_threads(int(job["torch_threads"]))
    if not _INTEROP_CONFIGURED:
        torch.set_num_interop_threads(1)
        _INTEROP_CONFIGURED = True
    seed_everything(int(job["seed"]))

    task = "assoc-recall-mk"
    sequence_length = 100
    tokenizer = make_tokenizer(task, 8, 0)
    model = make_model(
        layers=list(job["layers"]),
        hidden_size=int(job["hidden_size"]),
        vocabulary_size=len(tokenizer),
        state_size=int(job["state_size"]),
        expansion=2,
    )
    parameter_count = count_parameters(model)
    expected = int(job["expected_parameters"])
    if parameter_count != expected:
        raise RuntimeError(
            f"{job['job_id']} parameter count {parameter_count}, expected {expected}"
        )

    steps = int(job["steps"])
    dataset = TrainDataset(
        tokenizer,
        task=task,
        sequence_length=sequence_length,
        min_subseq_length=97,
        max_subseq_length=98,
        num_examples=steps,
        batch_size=8,
        p=0.2,
    )
    mask = attention_window_mask(sequence_length, 100)
    optimizer = AdamW(
        model.parameters(),
        lr=float(job["learning_rate"]),
        weight_decay=0.1,
    )
    scheduler = get_scheduler(
        name="linear",
        optimizer=optimizer,
        num_warmup_steps=100,
        num_training_steps=4000,
    )
    optimizer.zero_grad(set_to_none=True)
    losses: list[float] = []
    curve: list[dict] = []
    checkpoint_losses: list[float] = []
    random_targets = bool(job.get("random_targets", False))

    for step in range(1, steps + 1):
        batch = dataset[step - 1]
        labels = batch["output_ids"]
        if random_targets:
            labels = labels.clone()
            replacement = torch.randint(
                low=0,
                high=len(tokenizer),
                size=labels.shape,
            )
            valid = batch["mask"].bool()
            labels[valid] = replacement[valid]
        logits = model(
            batch["input_ids"],
            attention_mask=mask,
            return_dict=True,
        )["logits"]
        loss = masked_loss(labels, logits, batch["mask"])
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad(set_to_none=True)
        loss_value = float(loss.detach())
        losses.append(loss_value)
        checkpoint_losses.append(loss_value)
        if step % 1000 == 0 or step == steps:
            curve.append(
                {
                    "step": step,
                    "mean_loss_since_previous_checkpoint": statistics.fmean(
                        checkpoint_losses
                    ),
                    "learning_rate": optimizer.param_groups[0]["lr"],
                }
            )
            checkpoint_losses = []

    final_evaluation = evaluate_preserving_rng(
        model,
        tokenizer,
        mask,
        task=task,
        sequence_length=sequence_length,
        sampled_length=97,
        batches=int(job["final_evaluation_batches"]),
        batch_size=8,
        probability=0.2,
        seed=int(job["evaluation_seed"]),
    )
    runtime = time.perf_counter() - started
    output = {
        "job_id": job["job_id"],
        "point_id": job["point_id"],
        "phase": job["phase"],
        "layers": list(job["layers"]),
        "hidden_size": int(job["hidden_size"]),
        "effective_state_size": int(job["state_size"]),
        "nominal_state_size": 1,
        "parameters": parameter_count,
        "learning_rate": float(job["learning_rate"]),
        "seed": int(job["seed"]),
        "evaluation_seed": int(job["evaluation_seed"]),
        "steps": steps,
        "random_targets": random_targets,
        "mean_training_loss": statistics.fmean(losses),
        "final_training_loss": losses[-1],
        "training_curve": curve,
        "final_evaluation": final_evaluation,
        "runtime_seconds": runtime,
        "torch_threads": torch.get_num_threads(),
        "cgroup_cpu_quota": cgroup_cpu_quota(),
        "cpu_affinity": (
            len(os.sched_getaffinity(0))
            if hasattr(os, "sched_getaffinity")
            else None
        ),
    }
    print(
        "FIGURE6_JOB_COMPLETE "
        + json.dumps(
            {
                "job_id": output["job_id"],
                "parameters": parameter_count,
                "mean_training_loss": output["mean_training_loss"],
                "accuracy": final_evaluation["accuracy"],
                "runtime_seconds": runtime,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return output


def run_mkar_parallel_jobs(jobs: list[dict], workers: int) -> list[dict]:
    results: list[dict] = []
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=workers, mp_context=context) as executor:
        futures = {
            executor.submit(train_mkar_job, job): job["job_id"] for job in jobs
        }
        for future in as_completed(futures):
            results.append(future.result())
    return sorted(results, key=lambda row: row["job_id"])


def aggregate_accuracy(rows: list[dict]) -> dict:
    accuracies = [float(row["final_evaluation"]["accuracy"]) for row in rows]
    mean = statistics.fmean(accuracies)
    standard_deviation = statistics.stdev(accuracies) if len(accuracies) > 1 else 0.0
    half_width = 1.96 * standard_deviation / math.sqrt(len(accuracies))
    return {
        "seeds": len(accuracies),
        "accuracies": accuracies,
        "mean_accuracy": mean,
        "standard_deviation": standard_deviation,
        "normal_95_interval_across_seeds": [
            max(0.0, mean - half_width),
            min(1.0, mean + half_width),
        ],
        "quantile_10": float(np.quantile(accuracies, 0.1)),
        "quantile_90": float(np.quantile(accuracies, 0.9)),
        "minimum": min(accuracies),
        "maximum": max(accuracies),
        "total_valid_tokens": sum(
            int(row["final_evaluation"]["valid_tokens"]) for row in rows
        ),
    }


def run_claim6_mkar_frontier(config: dict) -> dict:
    """Calibrate and reproduce the exact Figure 6 MKAR dimension sweep."""
    started = time.perf_counter()
    dimensions = [4, 8, 12, 16, 20, 24]
    architectures = [
        ("tf_tf", ["TF", "TF"], 1),
        ("ssm_ssm", ["SSM", "SSM"], 16),
        ("tf_ssm", ["TF", "SSM"], 16),
        ("ssm_tf", ["SSM", "TF"], 16),
    ]
    expected_counts = {
        "tf_tf": {4: 396, 8: 1304, 12: 2724, 16: 4656, 20: 7100, 24: 10056},
        "ssm_ssm": {4: 1164, 8: 2712, 12: 4644, 16: 6960, 20: 9820, 24: 12936},
        "tf_ssm": {4: 780, 8: 2008, 12: 3684, 16: 5808, 20: 8460, 24: 11496},
        "ssm_tf": {4: 780, 8: 2008, 12: 3684, 16: 5808, 20: 8460, 24: 11496},
    }
    points = [
        {
            "point_id": f"{prefix}_d{dimension}",
            "family": prefix,
            "layers": layers,
            "hidden_size": dimension,
            "state_size": state_size,
            "expected_parameters": expected_counts[prefix][dimension],
        }
        for prefix, layers, state_size in architectures
        for dimension in dimensions
    ]
    learning_rates = [float(value) for value in config["learning_rates"]]
    calibration_jobs = [
        {
            **point,
            "job_id": (
                f"cal_{point['point_id']}_lr{learning_rate:.10g}_s{seed}"
            ),
            "phase": "learning_rate_calibration",
            "learning_rate": learning_rate,
            "seed": int(seed),
            "evaluation_seed": int(seed) + 100_000,
            "steps": int(config["calibration_steps"]),
            "final_evaluation_batches": int(
                config["calibration_evaluation_batches"]
            ),
            "torch_threads": int(config["torch_threads_per_worker"]),
        }
        for point in points
        for learning_rate in learning_rates
        for seed in config["calibration_seeds"]
    ]
    calibration_results = run_mkar_parallel_jobs(
        calibration_jobs, int(config["max_workers"])
    )

    selected_learning_rates: dict[str, float] = {}
    calibration_summary: dict[str, list[dict]] = {}
    for point in points:
        candidates = []
        for learning_rate in learning_rates:
            rows = [
                row
                for row in calibration_results
                if row["point_id"] == point["point_id"]
                and row["learning_rate"] == learning_rate
            ]
            candidates.append(
                {
                    "learning_rate": learning_rate,
                    "replicates": len(rows),
                    "mean_training_loss": statistics.fmean(
                        row["mean_training_loss"] for row in rows
                    ),
                    "mean_accuracy": statistics.fmean(
                        row["final_evaluation"]["accuracy"] for row in rows
                    ),
                }
            )
        candidates.sort(
            key=lambda row: (
                -row["mean_accuracy"],
                row["mean_training_loss"],
                row["learning_rate"],
            )
        )
        calibration_summary[point["point_id"]] = candidates
        selected_learning_rates[point["point_id"]] = candidates[0][
            "learning_rate"
        ]

    final_jobs = [
        {
            **point,
            "job_id": f"final_{point['point_id']}_s{seed}",
            "phase": "converged_final",
            "learning_rate": selected_learning_rates[point["point_id"]],
            "seed": int(seed),
            "evaluation_seed": int(seed) + 200_000,
            "steps": int(config["final_steps"]),
            "final_evaluation_batches": int(config["final_evaluation_batches"]),
            "torch_threads": int(config["torch_threads_per_worker"]),
        }
        for point in points
        for seed in config["final_seeds"]
    ]
    final_results = run_mkar_parallel_jobs(
        final_jobs, int(config["max_workers"])
    )
    point_summaries = {
        point["point_id"]: {
            **point,
            "selected_learning_rate": selected_learning_rates[point["point_id"]],
            "statistics": aggregate_accuracy(
                [
                    row
                    for row in final_results
                    if row["point_id"] == point["point_id"]
                ]
            ),
        }
        for point in points
    }

    def first_hit(family: str) -> dict | None:
        eligible = [
            summary
            for summary in point_summaries.values()
            if summary["family"] == family
            and summary["statistics"]["mean_accuracy"] >= 0.60
        ]
        return (
            min(eligible, key=lambda row: row["expected_parameters"])
            if eligible
            else None
        )

    first_hits = {family: first_hit(family) for family, _, _ in architectures}
    ratio = None
    if first_hits["ssm_tf"] and first_hits["tf_tf"]:
        ratio = (
            first_hits["tf_tf"]["expected_parameters"]
            / first_hits["ssm_tf"]["expected_parameters"]
        )

    control_point = next(
        point for point in points if point["point_id"] == "ssm_tf_d12"
    )
    control_job = {
        **control_point,
        "job_id": "control_ssm_tf_d12_random_targets",
        "phase": "negative_control",
        "learning_rate": selected_learning_rates["ssm_tf_d12"],
        "seed": int(config["negative_control_seed"]),
        "evaluation_seed": int(config["negative_control_seed"]) + 200_000,
        "steps": int(config["final_steps"]),
        "final_evaluation_batches": int(config["final_evaluation_batches"]),
        "torch_threads": int(config["torch_threads_per_worker"]),
        "random_targets": True,
    }
    negative_control = run_mkar_parallel_jobs(
        [control_job], int(config["max_workers"])
    )[0]
    if negative_control["final_evaluation"]["accuracy"] >= 0.25:
        raise RuntimeError("MKAR random-target control unexpectedly reached 25%")

    bucket_table = {}
    for target in (1000, 2000, 6000, 12000):
        bucket_table[str(target)] = {}
        for family, _, _ in architectures:
            closest = min(
                (
                    summary
                    for summary in point_summaries.values()
                    if summary["family"] == family
                ),
                key=lambda row: abs(row["expected_parameters"] - target),
            )
            bucket_table[str(target)][family] = {
                "point_id": closest["point_id"],
                "parameters": closest["expected_parameters"],
                "mean_accuracy": closest["statistics"]["mean_accuracy"],
            }

    return {
        "stage": "claim_6_mkar_parameter_frontier",
        "scientific_status": "PROVISIONAL_PENDING_DECODE_RECALL_AND_STATIC_CHECKER",
        "source_contract": {
            "task": "multi-key associative recall",
            "sequence_length": 100,
            "key_length": 2,
            "vocabulary_size": 8,
            "paper_threshold_accuracy": 0.60,
            "paper_parameter_ratio": 6.0,
            "paper_runs": 11,
            "paper_table": {
                "1000": {"tf_tf": 0.124, "ssm_ssm": 0.158, "tf_ssm": 0.131, "ssm_tf": 0.144},
                "2000": {"tf_tf": 0.159, "ssm_ssm": 0.173, "tf_ssm": 0.183, "ssm_tf": 0.512},
                "6000": {"tf_tf": 0.230, "ssm_ssm": 0.356, "tf_ssm": 0.286, "ssm_tf": 0.990},
                "12000": {"tf_tf": 0.668, "ssm_ssm": 0.517, "tf_ssm": 0.524, "ssm_tf": 0.989},
            },
        },
        "calibration": {
            "selection_rule": (
                "highest mean held-out accuracy, then lowest mean loss, "
                "over two disjoint 1000-step calibration seeds"
            ),
            "learning_rates": learning_rates,
            "summary": calibration_summary,
            "selected": selected_learning_rates,
            "raw_runs": calibration_results,
        },
        "final_runs": final_results,
        "point_summaries": point_summaries,
        "threshold_0_60_first_hits": first_hits,
        "pure_tf_to_ssm_tf_first_hit_parameter_ratio": ratio,
        "paper_bucket_nearest_points": bucket_table,
        "negative_control": negative_control,
        "runtime": {
            "total_seconds": time.perf_counter() - started,
            "max_workers": int(config["max_workers"]),
            "torch_threads_per_worker": int(config["torch_threads_per_worker"]),
            "estimated_scientific_cores": (
                int(config["max_workers"])
                * int(config["torch_threads_per_worker"])
            ),
            "cgroup_cpu_quota": cgroup_cpu_quota(),
            "os_cpu_count": os.cpu_count(),
            "cpu_affinity": (
                len(os.sched_getaffinity(0))
                if hasattr(os, "sched_getaffinity")
                else None
            ),
            "calibration_jobs": len(calibration_jobs),
            "final_jobs": len(final_jobs),
            "negative_control_jobs": 1,
        },
        "limitations": [
            "The effective Mamba state size is 16 because exact saved parameter counts show that the nominal sd1 CLI value was not applied.",
            "The source records no seeds; this reproduction supplies deterministic disjoint calibration and final seeds.",
            "Evaluation uses 1,024 held-out sequences per seed instead of the public evaluator's one batch of eight.",
            "The first-hit ratio is restricted to the paper's precommitted hidden-dimension grid and is not an asymptotic lower bound.",
            "This stage tests Figure 6 only; the imported Claim 6 also mislabels the distinct Figure 5 decoding-recall task and remains pending.",
        ],
    }


def run_claim5_frontier(config: dict) -> dict:
    """Calibrate learning rates and reproduce the Figure 4 parameter frontier."""
    started = time.perf_counter()
    points = [
        {"point_id": "ssm_tf_d4", "layers": ["SSM", "TF"], "hidden_size": 4, "state_size": 16, "expected_parameters": 872, "headline": False},
        {"point_id": "ssm_tf_d8", "layers": ["SSM", "TF"], "hidden_size": 8, "state_size": 16, "expected_parameters": 2192, "headline": True},
        {"point_id": "ssm_tf_d12", "layers": ["SSM", "TF"], "hidden_size": 12, "state_size": 16, "expected_parameters": 3960, "headline": False},
        {"point_id": "tf_ssm_d8", "layers": ["TF", "SSM"], "hidden_size": 8, "state_size": 16, "expected_parameters": 2192, "headline": True},
        {"point_id": "tf_tf_d16", "layers": ["TF", "TF"], "hidden_size": 16, "state_size": 1, "expected_parameters": 5024, "headline": False},
        {"point_id": "tf_tf_d20", "layers": ["TF", "TF"], "hidden_size": 20, "state_size": 1, "expected_parameters": 7560, "headline": False},
        {"point_id": "tf_tf_d24", "layers": ["TF", "TF"], "hidden_size": 24, "state_size": 1, "expected_parameters": 10608, "headline": True},
        {"point_id": "tf_tf_d32", "layers": ["TF", "TF"], "hidden_size": 32, "state_size": 1, "expected_parameters": 18240, "headline": False},
        {"point_id": "ssm_ssm_d16", "layers": ["SSM", "SSM"], "hidden_size": 16, "state_size": 16, "expected_parameters": 7328, "headline": False},
        {"point_id": "ssm_ssm_d20", "layers": ["SSM", "SSM"], "hidden_size": 20, "state_size": 16, "expected_parameters": 10280, "headline": False},
        {"point_id": "ssm_ssm_d24", "layers": ["SSM", "SSM"], "hidden_size": 24, "state_size": 16, "expected_parameters": 13488, "headline": True},
        {"point_id": "ssm_ssm_d32", "layers": ["SSM", "SSM"], "hidden_size": 32, "state_size": 16, "expected_parameters": 21056, "headline": False},
    ]
    learning_rates = [float(value) for value in config["learning_rates"]]
    calibration_jobs: list[dict] = []
    for point in points:
        for learning_rate in learning_rates:
            for seed in config["calibration_seeds"]:
                calibration_jobs.append(
                    {
                        **point,
                        "job_id": f"cal_{point['point_id']}_lr{learning_rate:.10g}_s{seed}",
                        "phase": "learning_rate_calibration",
                        "learning_rate": learning_rate,
                        "seed": int(seed),
                        "evaluation_seed": int(seed) + 100_000,
                        "steps": int(config["calibration_steps"]),
                        "epoch_evaluation_batches": 0,
                        "final_evaluation_batches": int(config["calibration_evaluation_batches"]),
                        "torch_threads": int(config["torch_threads_per_worker"]),
                    }
                )
    calibration_results = run_parallel_jobs(
        calibration_jobs, int(config["max_workers"])
    )

    selected_learning_rates: dict[str, float] = {}
    calibration_summary: dict[str, list[dict]] = {}
    for point in points:
        candidates: list[dict] = []
        for learning_rate in learning_rates:
            rows = [
                row
                for row in calibration_results
                if row["point_id"] == point["point_id"]
                and row["learning_rate"] == learning_rate
            ]
            candidates.append(
                {
                    "learning_rate": learning_rate,
                    "replicates": len(rows),
                    "mean_training_loss": statistics.fmean(
                        row["mean_training_loss"] for row in rows
                    ),
                    "mean_accuracy": statistics.fmean(
                        row["final_evaluation"]["accuracy"] for row in rows
                    ),
                }
            )
        candidates.sort(key=lambda row: (row["mean_training_loss"], row["learning_rate"]))
        calibration_summary[point["point_id"]] = candidates
        selected_learning_rates[point["point_id"]] = candidates[0]["learning_rate"]

    final_jobs: list[dict] = []
    frontier_seeds = [int(seed) for seed in config["frontier_seeds"]]
    headline_seeds = [int(seed) for seed in config["headline_seeds"]]
    for point in points:
        seeds = headline_seeds if point["headline"] else frontier_seeds
        for seed in seeds:
            final_jobs.append(
                {
                    **point,
                    "job_id": f"final_{point['point_id']}_s{seed}",
                    "phase": "converged_final",
                    "learning_rate": selected_learning_rates[point["point_id"]],
                    "seed": seed,
                    "evaluation_seed": seed + 200_000,
                    "steps": int(config["final_steps"]),
                    "epoch_evaluation_batches": int(config["epoch_evaluation_batches"]),
                    "final_evaluation_batches": int(config["final_evaluation_batches"]),
                    "torch_threads": int(config["torch_threads_per_worker"]),
                }
            )
    final_results = run_parallel_jobs(final_jobs, int(config["max_workers"]))

    point_summaries: dict[str, dict] = {}
    for point in points:
        rows = [
            row for row in final_results if row["point_id"] == point["point_id"]
        ]
        point_summaries[point["point_id"]] = {
            **point,
            "selected_learning_rate": selected_learning_rates[point["point_id"]],
            "statistics": aggregate_accuracy(rows),
        }

    hybrid_lr = selected_learning_rates["ssm_tf_d8"]
    control_job = {
        **next(point for point in points if point["point_id"] == "ssm_tf_d8"),
        "job_id": "control_ssm_tf_d8_random_targets",
        "phase": "negative_control",
        "learning_rate": hybrid_lr,
        "seed": int(config["negative_control_seed"]),
        "evaluation_seed": int(config["negative_control_seed"]) + 200_000,
        "steps": int(config["final_steps"]),
        "epoch_evaluation_batches": int(config["epoch_evaluation_batches"]),
        "final_evaluation_batches": int(config["final_evaluation_batches"]),
        "torch_threads": int(config["torch_threads_per_worker"]),
        "random_targets": True,
    }
    negative_control = run_parallel_jobs(
        [control_job], int(config["max_workers"])
    )[0]
    if negative_control["final_evaluation"]["accuracy"] >= 0.2:
        raise RuntimeError("random-target negative control unexpectedly reached 20%")

    # Independent structural checks over the completed result matrix.
    for point in points:
        candidates = calibration_summary[point["point_id"]]
        selected = selected_learning_rates[point["point_id"]]
        if selected != min(
            candidates,
            key=lambda row: (row["mean_training_loss"], row["learning_rate"]),
        )["learning_rate"]:
            raise RuntimeError("learning-rate calibration selection changed")
        expected_seeds = (
            len(headline_seeds) if point["headline"] else len(frontier_seeds)
        )
        if point_summaries[point["point_id"]]["statistics"]["seeds"] != expected_seeds:
            raise RuntimeError(f"seed count changed for {point['point_id']}")

    def first_hit(prefix: str) -> dict | None:
        eligible = [
            summary
            for point_id, summary in point_summaries.items()
            if point_id.startswith(prefix)
            and summary["statistics"]["mean_accuracy"] >= 0.9
        ]
        return min(eligible, key=lambda row: row["expected_parameters"]) if eligible else None

    first_hits = {
        "ssm_tf": first_hit("ssm_tf_"),
        "tf_tf": first_hit("tf_tf_"),
        "ssm_ssm": first_hit("ssm_ssm_"),
    }
    ratios = {}
    if first_hits["ssm_tf"]:
        for pure in ("tf_tf", "ssm_ssm"):
            if first_hits[pure]:
                ratios[pure] = (
                    first_hits[pure]["expected_parameters"]
                    / first_hits["ssm_tf"]["expected_parameters"]
                )

    hybrid = point_summaries["ssm_tf_d8"]["statistics"]
    pure_tf = point_summaries["tf_tf_d24"]["statistics"]
    pure_ssm = point_summaries["ssm_ssm_d24"]["statistics"]
    if (
        hybrid["mean_accuracy"] >= 0.99
        and max(
            pure_tf["normal_95_interval_across_seeds"][1],
            pure_ssm["normal_95_interval_across_seeds"][1],
        )
        < 0.99
    ):
        imported_claim_verdict = "FALSIFIED"
        verdict_basis = (
            "The approximately-2k hybrid reaches at least 0.99 mean accuracy, "
            "while the upper 95% seed intervals for both approximately-12k "
            "pure models remain below 0.99; they therefore do not match it."
        )
    else:
        imported_claim_verdict = "BLOCKED"
        verdict_basis = (
            "The finite converged runs did not establish the strict separation "
            "needed to verify or falsify the imported wording."
        )

    total_seconds = time.perf_counter() - started
    return {
        "stage": "claim_5_selective_copy_parameter_frontier",
        "scientific_status": "PROVISIONAL_PENDING_STATIC_REPLAY_VERIFIER",
        "exact_imported_claim_verdict": imported_claim_verdict,
        "verdict_basis": verdict_basis,
        "source_contracts": {
            "paper_table": {
                "hybrid_approx_2000": 0.999,
                "pure_tf_approx_12000": 0.923,
                "pure_ssm_approx_12000": 0.931,
            },
            "paper_caption": (
                "At 2000 parameters hybrids consistently attain perfect "
                "accuracy; pure models with 6x parameters attain around 0.9."
            ),
            "imported_claim_difference": (
                "The imported claim says the pure models need approximately "
                "12000 parameters to match perfect accuracy, whereas the paper "
                "caption explicitly says they reach only around 0.9."
            ),
        },
        "calibration": {
            "selection_rule": "lowest mean 1000-step training loss over two calibration seeds",
            "learning_rates": learning_rates,
            "summary": calibration_summary,
            "selected": selected_learning_rates,
            "raw_runs": calibration_results,
        },
        "final_runs": final_results,
        "point_summaries": point_summaries,
        "threshold_0_90_first_hits": first_hits,
        "first_hit_parameter_ratios_relative_to_ssm_tf": ratios,
        "negative_control": negative_control,
        "runtime": {
            "total_seconds": total_seconds,
            "max_workers": int(config["max_workers"]),
            "torch_threads_per_worker": int(config["torch_threads_per_worker"]),
            "estimated_scientific_cores": (
                int(config["max_workers"])
                * int(config["torch_threads_per_worker"])
            ),
            "cgroup_cpu_quota": cgroup_cpu_quota(),
            "os_cpu_count": os.cpu_count(),
            "cpu_affinity": (
                len(os.sched_getaffinity(0))
                if hasattr(os, "sched_getaffinity")
                else None
            ),
            "calibration_jobs": len(calibration_jobs),
            "final_jobs": len(final_jobs),
            "negative_control_jobs": 1,
        },
        "limitations": [
            "The effective state size is 16 because exact saved Figure counts show the nominal sd1 argument was not applied.",
            "The source records no original seeds; this reproduction supplies deterministic seeds.",
            "The fixed evaluation uses 2,048 held-out sequences per seed instead of the public loop's eight examples.",
            "Normal 95% intervals summarize variability across 11 headline seeds; the 10th/90th quantiles match the paper's reporting convention.",
            "The 0.90 first-hit frontier is a finite calibrated sweep over the explicitly listed dimensions, not an asymptotic lower bound.",
        ],
    }


def run_cpu_fidelity_pilot(config: dict) -> dict:
    started = time.perf_counter()
    threads = int(config["torch_threads"])
    torch.set_num_threads(threads)
    torch.set_num_interop_threads(1)
    seed = int(config["seed"])
    seed_everything(seed)

    task = "var-copy"
    sequence_length = 100
    window = 20
    vocabulary = 26
    number_tokens = 5
    probability = 0.2
    hidden_size = 8
    # The saved Figure parameter counts reveal that the nominal `sd1` argument
    # did not reach the model: the effective state size was the model default
    # 16. See the count calibration below.
    state_size = 16
    expansion = 2
    layers = ["SSM", "TF"]
    tokenizer = make_tokenizer(task, vocabulary, number_tokens)
    model = make_model(
        layers=layers,
        hidden_size=hidden_size,
        vocabulary_size=len(tokenizer),
        state_size=state_size,
        expansion=expansion,
    )
    parameters = count_parameters(model)

    # The saved Figure 6 notebook reports exactly 11,496 parameters for the
    # d=24 SSM->TF model despite a run identifier ending in `sd1`. Expansion 2
    # with state size 1 gives 9,336, while expansion 2 with the model default
    # state size 16 gives exactly 11,496. The corresponding two-SSM counts
    # differ by 4,320 and independently confirm the same diagnosis.
    mkar_tokenizer = make_tokenizer("assoc-recall-mk", 8, 0)
    count_calibration: dict[str, int] = {}
    for candidate_state_size in (1, 16):
        calibration_model = make_model(
            layers=layers,
            hidden_size=24,
            vocabulary_size=len(mkar_tokenizer),
            state_size=candidate_state_size,
            expansion=2,
        )
        count_calibration[str(candidate_state_size)] = count_parameters(calibration_model)
        del calibration_model
    if count_calibration != {"1": 9336, "16": 11496}:
        raise RuntimeError(f"parameter-count calibration changed: {count_calibration}")
    if parameters != 2192:
        raise RuntimeError(f"target model is no longer approximately 2k parameters: {parameters}")

    train_dataset = TrainDataset(
        tokenizer,
        task=task,
        sequence_length=sequence_length,
        min_subseq_length=97,
        max_subseq_length=98,
        num_examples=int(config["pilot_steps"]),
        batch_size=8,
        p=probability,
    )
    mask = attention_window_mask(sequence_length, window)
    optimizer = AdamW(
        model.parameters(),
        lr=float(config["learning_rate"]),
        weight_decay=0.1,
    )
    scheduler = get_scheduler(
        name="linear",
        optimizer=optimizer,
        num_warmup_steps=100,
        num_training_steps=4000,
    )
    optimizer.zero_grad(set_to_none=True)

    initial_evaluation = evaluate(
        model,
        tokenizer,
        mask,
        task=task,
        sequence_length=sequence_length,
        sampled_length=97,
        batches=int(config["evaluation_batches"]),
        batch_size=8,
        probability=probability,
        seed=seed + 10_000,
    )
    # Restore the training RNG after the held-out evaluation.
    seed_everything(seed)
    checkpoints: list[dict] = []
    training_started = time.perf_counter()
    model.train()
    for step in range(1, int(config["pilot_steps"]) + 1):
        batch = train_dataset[step - 1]
        logits = model(
            batch["input_ids"],
            attention_mask=mask,
            return_dict=True,
        )["logits"]
        loss = masked_loss(batch["output_ids"], logits, batch["mask"])
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad(set_to_none=True)
        if step == 1 or step % 50 == 0 or step == int(config["pilot_steps"]):
            checkpoint = {
                "step": step,
                "loss": float(loss.detach()),
                "learning_rate": optimizer.param_groups[0]["lr"],
                "elapsed_seconds": time.perf_counter() - training_started,
            }
            checkpoints.append(checkpoint)
            print("FIGURE_TRAINING_PROGRESS " + json.dumps(checkpoint, sort_keys=True), flush=True)

    training_seconds = time.perf_counter() - training_started
    final_evaluation = evaluate(
        model,
        tokenizer,
        mask,
        task=task,
        sequence_length=sequence_length,
        sampled_length=97,
        batches=int(config["evaluation_batches"]),
        batch_size=8,
        probability=probability,
        seed=seed + 10_000,
    )
    total_seconds = time.perf_counter() - started
    cpu_affinity = (
        len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None
    )
    return {
        "stage": "claim_5_cpu_fidelity_pilot",
        "scientific_status": "PILOT_ONLY_NOT_CLAIM_EVIDENCE",
        "source_fidelity": {
            "architecture": "authors' audited GPTNeoX + sequential Mamba implementation",
            "layers": layers,
            "task_generator": "authors' var-copy generator",
            "sequence_length": sequence_length,
            "sampled_length": 97,
            "window": window,
            "vocabulary_tokens": vocabulary,
            "number_tokens": number_tokens,
            "number_token_values": ["#5", "#6", "#7", "#8", "#9"],
            "number_probability": probability,
            "batch_size": 8,
            "state_size": state_size,
            "nominal_run_identifier_state_size": 1,
            "mamba_expansion": expansion,
            "hidden_size": hidden_size,
            "learning_rate": float(config["learning_rate"]),
            "optimizer": "AdamW(weight_decay=0.1)",
            "schedule": "100-step warmup then linear decay over 4000 planned steps",
            "gradient_clip_norm": 1.0,
            "upstream_sha": "7beeb0de80f89eb5d75301aef8e97ee9b36ca999",
        },
        "parameter_count": parameters,
        "parameter_count_calibration": {
            "saved_figure_6_ssm_tf_d24": 11496,
            "effective_state_size_1": count_calibration["1"],
            "effective_state_size_16": count_calibration["16"],
        },
        "seed": seed,
        "initial_evaluation": initial_evaluation,
        "checkpoints": checkpoints,
        "final_evaluation": final_evaluation,
        "runtime": {
            "training_seconds": training_seconds,
            "total_seconds": total_seconds,
            "steps_per_second": int(config["pilot_steps"]) / training_seconds,
            "torch_threads_requested": threads,
            "torch_threads_actual": torch.get_num_threads(),
            "torch_interop_threads_actual": torch.get_num_interop_threads(),
            "os_cpu_count": os.cpu_count(),
            "cpu_affinity": cpu_affinity,
            "platform": platform.platform(),
            "torch_version": torch.__version__,
        },
        "pilot_limitations": [
            "Only 200 of the paper's 4000 final-training steps are run.",
            "This run estimates CPU throughput and checks implementation fidelity; it cannot verify Figure 4 accuracy.",
            "The public source does not record seeds; saved parameter counts show that runs named sd1 used effective state size 16.",
            "The paper says number tokens 5 through 10, while the Figure data key and public generator use five tokens, #5 through #9.",
        ],
    }
