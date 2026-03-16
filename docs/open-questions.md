# Open Questions and Decisions

This document tracks the few remaining decisions that still matter after the v1 architecture reset.

## Decisions Already Locked

1. Product scope
- Decision: translation-only app for `ko -> ko-jeju` and `ko-jeju -> ko`.

2. Model and runtime
- Decision: `est-ai/alan-llm-jeju-dialect-v1-4b` via GGUF on `llama-cpp-python`.

3. Hosting
- Decision: Cloudflare Pages + Pages Functions in front of Modal.

4. Abuse protection
- Decision: Turnstile + rate limiting + secret-authenticated upstream.

5. Output behavior
- Decision: translation-only responses, no explanations.

## Remaining Decisions

1. Hard input cap
- Needed before implementation to finalize `413` behavior and benchmark fairness.

2. Quant winner
- Needed after benchmarking `Q4_K_M` vs `Q5_K_M`.

3. Demo posture for cold starts
- Decide when to accept scale-to-zero cold starts and when to temporarily use `min_containers=1`.

4. Human review process
- Decide who scores the initial eval set and how many samples must be reviewed before launch.

## Questions to Resolve Through Documentation, Not Guesswork

1. Model/data licensing details for the public demo
2. Exact attribution wording for README and app footer
3. Benchmark corpus provenance and storage rules
