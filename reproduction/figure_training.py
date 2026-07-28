#!/usr/bin/env python3
"""Deterministic CPU harness around the authors' Figure 4--6 model code."""

from __future__ import annotations

import json
import math
import os
import platform
import random
import time
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
