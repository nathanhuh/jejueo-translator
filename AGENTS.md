# AGENTS.md instructions for / (repo root)

## Collaboration Protocol

- Work in hands-off mode by default.
- Implement directly unless the user needs to make a product or architecture decision with non-obvious consequences.
- Only require user intervention when a real decision or external action is needed.
- Plans and tickets should still include core implementation tasks normally.
- Assistant execution should still value testing, validation, tooling, review, and documentation alongside implementation work.
- Planning documents, checklists, decision records, and review feedback may be updated without additional approval.

## Planning Baseline

- Treat the current source of truth as a translation-only v1 product.
- v1 scope is exactly `ko -> ko-jeju` and `ko-jeju -> ko`.
- Do not reintroduce chat mode, QA mode, RAG, accounts, document upload, or browser-direct model access unless the user explicitly changes the plan.
- Default architecture assumptions for planning are:
  - model: `est-ai/alan-llm-jeju-dialect-v1-4b`
  - launch quantization: benchmark existing GGUF `Q4_K_M` vs `Q5_K_M`
  - inference: `llama-cpp-python` / `llama.cpp`
  - inference hosting: Modal
  - frontend and edge proxy: Cloudflare Pages + Pages Functions
  - abuse controls: Cloudflare Turnstile + rate limiting
- For documentation and reviews, prioritize measurable latency, evaluation discipline, and abuse protection over custom quantization or feature expansion.

## Intent

This repo is used for learning and portfolio development. Keep explanations clear and implementation pragmatic.
Default division of labor: assistant can implement directly in hands-off mode while keeping the user involved only for meaningful decisions, external dependencies, or validation that requires their judgment.
