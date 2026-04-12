#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jejueo_eval.runner import EvalConfig, run_eval


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run local Q4 evaluation on a fixed Jejueo eval set."
    )
    parser.add_argument("--model", required=True, help="Path to the Q4 GGUF model file.")
    parser.add_argument("--eval-set", required=True, help="Path to the fixed eval-set CSV.")
    parser.add_argument("--output-dir", required=True, help="Directory for predictions and review files.")
    parser.add_argument(
        "--backend",
        choices=["llama_cpp", "llama_cli"],
        default="llama_cpp",
        help="Inference backend to use for local evaluation.",
    )
    parser.add_argument(
        "--llama-cli-path",
        default="llama-completion",
        help="Path to llama-completion/llama-cli when using --backend llama_cli.",
    )
    parser.add_argument(
        "--device",
        default="",
        help="Optional llama.cpp device selection, e.g. 'none' for CPU-only.",
    )
    parser.add_argument("--temperature", type=float, default=0.4)
    parser.add_argument("--repeat-penalty", type=float, default=1.1)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--n-ctx", type=int, default=2048)
    parser.add_argument("--n-threads", type=int, default=4)
    parser.add_argument("--n-gpu-layers", type=int, default=0)
    parser.add_argument("--max-cases", type=int, default=0, help="Optional limit for smoke tests.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = run_eval(
        EvalConfig(
            model_path=args.model,
            eval_set_path=args.eval_set,
            output_dir=args.output_dir,
            backend=args.backend,
            temperature=args.temperature,
            repeat_penalty=args.repeat_penalty,
            top_p=args.top_p,
            max_tokens=args.max_tokens,
            n_ctx=args.n_ctx,
            n_threads=args.n_threads,
            n_gpu_layers=args.n_gpu_layers,
            max_cases=args.max_cases,
            llama_cli_path=args.llama_cli_path,
            device=args.device,
        )
    )
    print(f"Wrote evaluation artifacts to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
