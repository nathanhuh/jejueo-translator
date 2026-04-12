from __future__ import annotations

import csv
import hashlib
import json
import random
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_LANGS = {"ko", "ko-jeju"}
SUGGESTED_CATEGORIES = (
    "everyday",
    "proper_nouns",
    "line_breaks",
    "honorifics",
    "ambiguous_dialect",
)

HONORIFIC_PATTERNS = (
    "습니다",
    "습니까",
    "세요",
    "십시오",
    "드립니다",
    "께서",
    "저희",
    "올립니다",
)

JEJUEO_HINTS = (
    "하영",
    "혼저",
    "게난",
    "무사",
    "주게",
    "마씀",
)


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    source_lang: str
    target_lang: str
    source_text: str
    reference_text: str
    suggested_category: str
    category_final: str
    notes: str
    source_row_id: str


def _normalize_text(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def _detect_delimiter(path: Path) -> str:
    if path.suffix.lower() == ".tsv":
        return "\t"
    sample = path.read_text(encoding="utf-8")[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
        return dialect.delimiter
    except csv.Error:
        return ","


def _iter_csv_rows(path: Path) -> Iterable[dict[str, str]]:
    delimiter = _detect_delimiter(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        for row in reader:
            yield {str(k): (v if v is not None else "") for k, v in row.items()}


def _iter_jsonl_rows(path: Path) -> Iterable[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                continue
            yield {str(k): str(v) if v is not None else "" for k, v in payload.items()}


def iter_bilingual_rows(path: Path) -> Iterable[dict[str, str]]:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        yield from _iter_csv_rows(path)
        return
    if suffix == ".jsonl":
        yield from _iter_jsonl_rows(path)
        return
    raise ValueError(f"Unsupported dataset format: {path.suffix}")


def iter_parallel_text_rows(
    ko_path: Path,
    jejueo_path: Path,
) -> Iterable[dict[str, str]]:
    with ko_path.open("r", encoding="utf-8") as ko_handle, jejueo_path.open(
        "r", encoding="utf-8"
    ) as jejueo_handle:
        for row_index, (ko_line, jejueo_line) in enumerate(
            zip(ko_handle, jejueo_handle, strict=True), start=1
        ):
            yield {
                "row_id": str(row_index),
                "korean": ko_line.rstrip("\n"),
                "jejueo": jejueo_line.rstrip("\n"),
            }


def suggest_category(source_text: str, target_text: str) -> str:
    combined = f"{source_text} {target_text}"
    if "\n" in source_text or "\n" in target_text:
        return "line_breaks"
    if any(token in combined for token in HONORIFIC_PATTERNS):
        return "honorifics"
    if re.search(r"[A-Za-z0-9]", combined):
        return "proper_nouns"
    if any(token in combined for token in JEJUEO_HINTS):
        return "ambiguous_dialect"
    return "everyday"


def _make_case_id(
    source_lang: str,
    target_lang: str,
    source_text: str,
    reference_text: str,
) -> str:
    payload = "\u241f".join([source_lang, target_lang, source_text, reference_text]).encode("utf-8")
    digest = hashlib.sha1(payload).hexdigest()[:12]
    return f"{source_lang}-{target_lang}-{digest}"


def build_eval_candidates(
    dataset_path: Path,
    ko_col: str,
    jejueo_col: str,
) -> list[EvalCase]:
    cases: list[EvalCase] = []
    for row_index, row in enumerate(iter_bilingual_rows(dataset_path), start=1):
        ko_text = _normalize_text(row.get(ko_col, ""))
        jejueo_text = _normalize_text(row.get(jejueo_col, ""))
        if not ko_text or not jejueo_text:
            continue

        source_row_id = str(row.get("id") or row.get("row_id") or row_index)

        for source_lang, target_lang, source_text, reference_text in (
            ("ko", "ko-jeju", ko_text, jejueo_text),
            ("ko-jeju", "ko", jejueo_text, ko_text),
        ):
            category = suggest_category(source_text, reference_text)
            cases.append(
                EvalCase(
                    case_id=_make_case_id(source_lang, target_lang, source_text, reference_text),
                    source_lang=source_lang,
                    target_lang=target_lang,
                    source_text=source_text,
                    reference_text=reference_text,
                    suggested_category=category,
                    category_final="",
                    notes="",
                    source_row_id=source_row_id,
                )
            )

    return cases


def build_eval_candidates_from_parallel_text(
    ko_path: Path,
    jejueo_path: Path,
    ko_col: str = "korean",
    jejueo_col: str = "jejueo",
) -> list[EvalCase]:
    cases: list[EvalCase] = []
    for row_index, row in enumerate(iter_parallel_text_rows(ko_path, jejueo_path), start=1):
        ko_text = _normalize_text(row.get(ko_col, ""))
        jejueo_text = _normalize_text(row.get(jejueo_col, ""))
        if not ko_text or not jejueo_text:
            continue

        source_row_id = str(row.get("row_id") or row_index)
        for source_lang, target_lang, source_text, reference_text in (
            ("ko", "ko-jeju", ko_text, jejueo_text),
            ("ko-jeju", "ko", jejueo_text, ko_text),
        ):
            category = suggest_category(source_text, reference_text)
            cases.append(
                EvalCase(
                    case_id=_make_case_id(source_lang, target_lang, source_text, reference_text),
                    source_lang=source_lang,
                    target_lang=target_lang,
                    source_text=source_text,
                    reference_text=reference_text,
                    suggested_category=category,
                    category_final="",
                    notes="",
                    source_row_id=source_row_id,
                )
            )
    return cases


def select_eval_cases(cases: list[EvalCase], limit: int, seed: int) -> list[EvalCase]:
    if limit <= 0:
        raise ValueError("limit must be positive")
    by_direction: dict[tuple[str, str], list[EvalCase]] = {
        ("ko", "ko-jeju"): [],
        ("ko-jeju", "ko"): [],
    }
    for case in cases:
        by_direction[(case.source_lang, case.target_lang)].append(case)

    rng = random.Random(seed)
    for items in by_direction.values():
        rng.shuffle(items)

    per_direction = max(1, limit // 2)
    selected: list[EvalCase] = []
    for direction in (("ko", "ko-jeju"), ("ko-jeju", "ko")):
        selected.extend(by_direction[direction][:per_direction])

    if len(selected) < limit:
        remaining = [
            case
            for direction_cases in by_direction.values()
            for case in direction_cases
            if case.case_id not in {chosen.case_id for chosen in selected}
        ]
        rng.shuffle(remaining)
        selected.extend(remaining[: limit - len(selected)])

    return sorted(selected[:limit], key=lambda case: case.case_id)


def write_eval_set(cases: list[EvalCase], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case_id",
                "source_lang",
                "target_lang",
                "source_text",
                "reference_text",
                "suggested_category",
                "category_final",
                "notes",
                "source_row_id",
            ],
        )
        writer.writeheader()
        for case in cases:
            writer.writerow(
                {
                    "case_id": case.case_id,
                    "source_lang": case.source_lang,
                    "target_lang": case.target_lang,
                    "source_text": case.source_text,
                    "reference_text": case.reference_text,
                    "suggested_category": case.suggested_category,
                    "category_final": case.category_final,
                    "notes": case.notes,
                    "source_row_id": case.source_row_id,
                }
            )


def read_eval_set(eval_set_path: Path) -> list[EvalCase]:
    rows: list[EvalCase] = []
    with eval_set_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            source_lang = row["source_lang"]
            target_lang = row["target_lang"]
            if source_lang not in SUPPORTED_LANGS or target_lang not in SUPPORTED_LANGS:
                raise ValueError(f"Unsupported language pair in eval set: {source_lang}->{target_lang}")
            rows.append(
                EvalCase(
                    case_id=row["case_id"],
                    source_lang=source_lang,
                    target_lang=target_lang,
                    source_text=row["source_text"],
                    reference_text=row["reference_text"],
                    suggested_category=row.get("suggested_category", "everyday"),
                    category_final=row.get("category_final", ""),
                    notes=row.get("notes", ""),
                    source_row_id=row.get("source_row_id", ""),
                )
            )
    return rows
