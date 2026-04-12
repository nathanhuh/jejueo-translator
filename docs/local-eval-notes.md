# Local Eval Notes

## What Failed

### 1. We assumed `huggingface-cli` would exist

- It did not.
- In the current `huggingface_hub` install, the CLI binary is `hf`, not `huggingface-cli`.
- Relying on the older command name wasted time.

## 2. We assumed the conda environment would be active in tool-executed shells

- It was not.
- `python`, `pip`, and `conda` were unavailable in those shells even though the environment existed.
- Directly invoking the environment binaries by absolute path was more reliable.

## 3. We assumed the model had already been downloaded

- It had not.
- The first `run_q4_eval.py` failure was only a placeholder-path error, not an install problem.
- We should have verified the GGUF file path before attempting inference.

## 4. We assumed the Kakao Brain Jejueo dataset was in tabular form

- It was not.
- The dataset added locally was an aligned parallel text corpus:
  - `ko.train`, `ko.dev`, `ko.test`
  - `je.train`, `je.dev`, `je.test`
- The eval builder had to be extended to support aligned plain-text files directly.

## 5. We had a bad category heuristic in the eval-set builder

- The initial implementation marked every sample as `line_breaks`.
- Cause: the heuristic checked for `\n` in a concatenated string that always contained one.
- Fix: check only whether either source or target text actually contains line breaks.

## 6. We assumed `llama-cpp-python` would be the fastest path to local inference

- It was not.
- The Python binding imported successfully, but model loading hard-crashed in native code.
- This was not a script bug; it was a backend/runtime issue.

## 7. We initially blamed the GGUF or Python wrapper without isolating the backend

- That was incomplete debugging.
- Installing current `llama.cpp` and testing the same GGUF with `llama-cli` showed the model itself was loadable.
- The real failure was Metal backend initialization on this machine in the attempted path.

## 8. Metal GPU offload was not usable in the current local setup

- `llama.cpp` reported:
  - `ggml_metal_init: error: failed to create command queue`
  - `failed to initialize backend`
- CPU-only execution with `--device none` worked.
- Conclusion: the unblock path is CPU-only first, Metal later.

## 9. The eval runner was too tightly coupled to `llama-cpp-python`

- That made the whole local evaluation path fragile.
- Adding a CLI backend made the workflow much more debuggable and practical.

## 10. The first CLI integration still failed in two ways

- It stayed interactive after generation.
- The parser captured CLI trailer text instead of the actual model output.
- Fixes:
  - switch to `llama-completion`
  - use `--simple-io` and `--no-display-prompt`
  - strip `<think>...</think>` and `> EOF by user`

## 11. Relative output paths behaved inconsistently during smoke-test iteration

- A reported successful run did not immediately line up with the expected repo-local output directory.
- Using an absolute output path in `/tmp` made verification clearer.
- For debugging native/runtime tooling, absolute paths are easier to reason about.

## Practical Rules Going Forward

- Verify the model file exists before running inference.
- Prefer direct env binary paths over assuming conda activation in automation.
- Treat `hf` as the default Hugging Face CLI command.
- Treat the Kakao Jejueo corpus as aligned plain text unless proven otherwise.
- Start with CPU-only `llama-completion` if `llama-cpp-python` or Metal crashes.
- Use absolute output paths while debugging.
- Do not assume a successful inference backend is production-ready until output parsing is verified.
