#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jejueo_eval.dataset import (
    build_eval_candidates,
    build_eval_candidates_from_parallel_text,
    select_eval_cases,
    write_eval_set,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a fixed eval-set CSV from a local Jejueo bilingual corpus file."
    )
    parser.add_argument("--input", help="Path to the local CSV, TSV, or JSONL corpus file.")
    parser.add_argument("--ko-file", help="Path to the Korean side of a parallel plain-text corpus.")
    parser.add_argument("--je-file", help="Path to the Jejueo side of a parallel plain-text corpus.")
    parser.add_argument("--output", required=True, help="Path to the output eval-set CSV.")
    parser.add_argument("--ko-col", default="korean", help="Column name containing Korean text.")
    parser.add_argument("--jejueo-col", default="jejueo", help="Column name containing Jejueo text.")
    parser.add_argument("--limit", type=int, default=180, help="Number of eval cases to select.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic selection.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    if args.input:
        dataset_path = Path(args.input)
        if not dataset_path.exists():
            raise SystemExit(f"Input dataset does not exist: {dataset_path}")
        candidates = build_eval_candidates(dataset_path, args.ko_col, args.jejueo_col)
    elif args.ko_file and args.je_file:
        ko_path = Path(args.ko_file)
        je_path = Path(args.je_file)
        if not ko_path.exists():
            raise SystemExit(f"Korean file does not exist: {ko_path}")
        if not je_path.exists():
            raise SystemExit(f"Jejueo file does not exist: {je_path}")
        candidates = build_eval_candidates_from_parallel_text(
            ko_path,
            je_path,
            ko_col=args.ko_col,
            jejueo_col=args.jejueo_col,
        )
    else:
        raise SystemExit("Provide either --input or both --ko-file and --je-file.")

    if not candidates:
        raise SystemExit("No usable bilingual rows were found. Check the file path and column names.")

    selected = select_eval_cases(candidates, limit=args.limit, seed=args.seed)
    write_eval_set(selected, output_path)

    direction_counts: dict[tuple[str, str], int] = {}
    for case in selected:
        key = (case.source_lang, case.target_lang)
        direction_counts[key] = direction_counts.get(key, 0) + 1

    print(f"Wrote {len(selected)} eval cases to {output_path}")
    for (source_lang, target_lang), count in sorted(direction_counts.items()):
        print(f"  {source_lang} -> {target_lang}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
