# AGENTS.md instructions for / (repo root)

## Collaboration Protocol

- The user is the primary implementer for this project.
- Do not create or modify implementation/source code unless the user explicitly authorizes coding in that turn.
- Before generating any code changes, ask for explicit permission.
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

This repo is used for learning and portfolio development. Prioritize guidance, planning, and code review over autonomous coding.
