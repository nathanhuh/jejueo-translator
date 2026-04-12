from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from .dataset import EvalCase, read_eval_set
from .prompt import build_translation_prompt


@dataclass
class EvalConfig:
    model_path: str
    eval_set_path: str
    output_dir: str
    backend: str = "llama_cpp"
    temperature: float = 0.4
    repeat_penalty: float = 1.1
    top_p: float = 0.9
    max_tokens: int = 256
    n_ctx: int = 2048
    n_threads: int = 4
    n_gpu_layers: int = 0
    max_cases: int = 0
    llama_cli_path: str = "llama-completion"
    device: str = ""


def _load_llama():
    try:
        from llama_cpp import Llama
    except ImportError as exc:
        raise RuntimeError(
            "llama-cpp-python is not installed. Install it with "
            '`python3 -m pip install -e "packages/eval[llama]"`.'
        ) from exc
    return Llama


def _run_single_case_llama_cli(case: EvalCase, config: EvalConfig) -> dict[str, object]:
    cli_path = shutil.which(config.llama_cli_path) or config.llama_cli_path
    prompt = build_translation_prompt(case.source_lang, case.target_lang, case.source_text)
    command = [
        cli_path,
        "-m",
        config.model_path,
        "-n",
        str(config.max_tokens),
        "-c",
        str(config.n_ctx),
        "--temp",
        str(config.temperature),
        "--top-p",
        str(config.top_p),
        "--repeat-penalty",
        str(config.repeat_penalty),
        "--simple-io",
        "--no-display-prompt",
        "-p",
        prompt,
    ]
    if config.device:
        command.extend(["--device", config.device])
    command.extend(["-ngl", str(config.n_gpu_layers)])

    started = time.perf_counter()
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    stdout = completed.stdout
    stdout = re.sub(r"<think>.*?</think>", "", stdout, flags=re.DOTALL)
    stdout = stdout.replace("> EOF by user", "")
    prediction = stdout.strip()
    return {
        "case_id": case.case_id,
        "source_lang": case.source_lang,
        "target_lang": case.target_lang,
        "source_text": case.source_text,
        "reference_text": case.reference_text,
        "prediction": prediction,
        "suggested_category": case.suggested_category,
        "category_final": case.category_final,
        "notes": case.notes,
        "source_row_id": case.source_row_id,
        "latency_ms": elapsed_ms,
    }


def _run_single_case(llm, case: EvalCase, config: EvalConfig) -> dict[str, object]:
    prompt = build_translation_prompt(case.source_lang, case.target_lang, case.source_text)
    started = time.perf_counter()
    result = llm.create_completion(
        prompt=prompt,
        temperature=config.temperature,
        top_p=config.top_p,
        repeat_penalty=config.repeat_penalty,
        max_tokens=config.max_tokens,
        stop=["</s>", "\n\nSource ("],
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    prediction = result["choices"][0]["text"].strip()
    return {
        "case_id": case.case_id,
        "source_lang": case.source_lang,
        "target_lang": case.target_lang,
        "source_text": case.source_text,
        "reference_text": case.reference_text,
        "prediction": prediction,
        "suggested_category": case.suggested_category,
        "category_final": case.category_final,
        "notes": case.notes,
        "source_row_id": case.source_row_id,
        "latency_ms": elapsed_ms,
    }


def run_eval(config: EvalConfig) -> Path:
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    eval_cases = read_eval_set(Path(config.eval_set_path))
    if config.max_cases > 0:
        eval_cases = eval_cases[: config.max_cases]

    llm = None
    if config.backend == "llama_cpp":
        Llama = _load_llama()
        llm = Llama(
            model_path=config.model_path,
            n_ctx=config.n_ctx,
            n_threads=config.n_threads,
            n_gpu_layers=config.n_gpu_layers,
            verbose=False,
        )
    elif config.backend != "llama_cli":
        raise ValueError(f"Unsupported backend: {config.backend}")

    predictions_path = output_dir / "predictions.jsonl"
    review_path = output_dir / "review.csv"
    summary_path = output_dir / "run-summary.json"

    predictions: list[dict[str, object]] = []
    with predictions_path.open("w", encoding="utf-8") as handle:
        for case in eval_cases:
            if config.backend == "llama_cli":
                prediction = _run_single_case_llama_cli(case, config)
            else:
                prediction = _run_single_case(llm, case, config)
            predictions.append(prediction)
            handle.write(json.dumps(prediction, ensure_ascii=False) + "\n")

    with review_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case_id",
                "source_lang",
                "target_lang",
                "suggested_category",
                "source_text",
                "reference_text",
                "prediction",
                "latency_ms",
                "meaning_review",
                "dialect_review",
                "format_review",
                "translation_only_review",
                "hallucination_review",
                "failure_label",
                "review_notes",
            ],
        )
        writer.writeheader()
        for item in predictions:
            writer.writerow(
                {
                    "case_id": item["case_id"],
                    "source_lang": item["source_lang"],
                    "target_lang": item["target_lang"],
                    "suggested_category": item["suggested_category"],
                    "source_text": item["source_text"],
                    "reference_text": item["reference_text"],
                    "prediction": item["prediction"],
                    "latency_ms": item["latency_ms"],
                    "meaning_review": "",
                    "dialect_review": "",
                    "format_review": "",
                    "translation_only_review": "",
                    "hallucination_review": "",
                    "failure_label": "",
                    "review_notes": "",
                }
            )

    latencies = [float(item["latency_ms"]) for item in predictions]
    summary = {
        "config": asdict(config),
        "num_cases": len(predictions),
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
        "min_latency_ms": min(latencies) if latencies else 0.0,
        "max_latency_ms": max(latencies) if latencies else 0.0,
        "predictions_path": str(predictions_path),
        "review_path": str(review_path),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_dir
