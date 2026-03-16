# Jejueo Translator Planning Docs

This folder contains planning artifacts for building a public Jejueo translator focused on Korean <-> Jejueo text translation.

Current operating posture: ship a narrow, production-style portfolio demo first, then optimize.

## Documents

- `architecture.md`: Cloudflare Pages + Modal architecture, request flow, and security boundaries.
- `implementation-plan.md`: Phase-by-phase delivery plan for the translation-only v1.
- `evaluation-plan.md`: Quant benchmarking and regression plan.
- `open-questions.md`: Remaining decisions that still matter before or during implementation.
- `mvp-decision-record.md`: Current source of truth for scope, hosting, and quality priorities.
- `phase-0-checklist.md`: Phase 0 tasks for freezing contracts, prompts, and eval rules.
- `risk-register.md`: Main delivery, quality, and abuse risks for v1.
- `data-licensing.md`: Model/data/license checklist for a public portfolio deployment.
- `api-spec.md`: Stable `POST /api/translate` contract.
- `implementation-checklist.md`: Build tracker aligned to the new monorepo and hosting layout.

## Scope

- Planning only unless the user explicitly authorizes implementation code.
- v1 is translation-only: `ko -> ko-jeju` and `ko-jeju -> ko`.
- Non-goals for v1: chat, QA, retrieval augmentation, user accounts, document upload, and browser-direct access to model infrastructure.
