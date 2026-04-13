# `packages/eval`

Local evaluation tooling for the Jejueo translator MVP.

This package is designed for the current MVP path:

- provisional launch quant: `Q4_K_M`
- fixed held-out evaluation set derived from the Kakao Brain Jejueo bilingual corpus
- current verified local inference via `llama-completion --device none`
- intended service-side runtime target remains `llama-cpp-python`

## What this package does

1. Builds a fixed eval-set CSV from a local bilingual corpus file.
2. Runs local inference on that fixed eval set with `Q4_K_M`.
3. Writes machine-readable run artifacts for later manual review.

## What it does not do

- download the Kakao Brain dataset automatically
- commit raw dataset files into the repo
- score quality automatically

The dataset is expected to be downloaded by the user and passed in as a local file path.

## Expected dataset shape

The builder supports either:

1. A local CSV, TSV, or JSONL file containing both Korean and Jejueo text columns.
2. A pair of aligned plain-text files such as the Kakao Brain Jejueo corpus splits:
   - `ko.train` / `je.train`
   - `ko.dev` / `je.dev`
   - `ko.test` / `je.test`

Default column names:

- Korean: `korean`
- Jejueo: `jejueo`

You can override those names with CLI flags.

## Install

From the repo root:

```bash
python3 -m pip install -e packages/eval
python3 -m pip install -e "packages/eval[llama]"
```

## Build an eval set

```bash
python3 packages/eval/scripts/build_eval_set.py \
  --input /path/to/jejueo.csv \
  --output packages/eval/data/eval-set.csv \
  --ko-col korean \
  --jejueo-col jejueo \
  --limit 180
```

This creates a fixed CSV with stable case IDs for both directions.

For the Kakao Brain plain-text split files:

```bash
python3 packages/eval/scripts/build_eval_set.py \
  --ko-file dataset/ko.test \
  --je-file dataset/je.test \
  --output packages/eval/data/eval-set.csv \
  --limit 180
```

## Run local `Q4_K_M` evaluation

```bash
python3 packages/eval/scripts/run_q4_eval.py \
  --model /path/to/alan-q4_k_m.gguf \
  --eval-set packages/eval/data/eval-set.csv \
  --output-dir packages/eval/results/q4-run-001
```

If `llama-cpp-python` has backend issues on macOS, use `llama-completion` instead:

```bash
python3 packages/eval/scripts/run_q4_eval.py \
  --backend llama_cli \
  --llama-cli-path /opt/homebrew/bin/llama-completion \
  --device none \
  --model /path/to/alan-q4_k_m.gguf \
  --eval-set packages/eval/data/eval-set.csv \
  --output-dir packages/eval/results/q4-run-001
```

The runner writes:

- `predictions.jsonl`
- `review.csv`
- `run-summary.json`

## Notes

- The runner uses a strict translation-only prompt.
- Manual review is still required for meaning and dialect quality.
- The verified local smoke-test path on this machine currently uses the CLI backend rather than `llama-cpp-python`.
- Keep raw corpus files outside the public repo if licensing requires that posture.
