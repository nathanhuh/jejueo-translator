# Risk Register

## How to use

- Severity model: `Exposure = Likelihood (1-5) x Impact (1-5)`.
- Escalate any risk with exposure >= 16.
- Each risk must have one explicit owner.

## Risk Table

| ID | Category | Risk | Likelihood | Impact | Exposure | Trigger Signal | Mitigation | Owner | Status |
|---|---|---|---:|---:|---:|---|---|---|---|
| R-01 | Quality | Chosen quant is too lossy for acceptable dialect quality | 3 | 5 | 15 | Human eval shows noticeable meaning or dialect degradation | Benchmark `Q4_K_M` vs `Q5_K_M` before launch; document decision rule | Nathan | Open |
| R-02 | Performance | Cold starts exceed acceptable first-response latency | 4 | 4 | 16 | First response > `10s` in staging or production | Use Modal Volume, Memory Snapshot, and optionally `min_containers=1` during demos | Nathan | Open |
| R-03 | Security | Browser or attacker reaches model endpoint without proxy auth | 3 | 5 | 15 | Direct requests to Modal succeed | Secret-authenticated upstream, restricted exposure, no browser-direct endpoint | Nathan | Open |
| R-04 | Abuse | Public endpoint is abused and burns free-tier budget | 4 | 4 | 16 | Spike in request volume or repeated failed challenges | Turnstile, Cloudflare rate limiting, strict edge validation | Nathan | Open |
| R-05 | Quality | Model adds explanations or notes instead of pure translation | 3 | 5 | 15 | Eval set shows non-translation output | Lock prompt contract; use translation-only compliance as hard gate | Nathan | Open |
| R-06 | Quality | Formatting and line breaks are lost | 3 | 3 | 9 | Multiline eval samples fail or users report mangled formatting | Add fixed formatting-preservation cases to eval and regression tests | Nathan | Open |
| R-07 | Legal | Model/data licensing ambiguity blocks public release | 3 | 5 | 15 | No written license chain for model and data | Complete license checklist before launch; keep repo free of raw data | Nathan | Open |
| R-08 | Process | Scope creep delays launch | 4 | 3 | 12 | New features added before v1 is live | Enforce translation-only scope until launch checklist is complete | Nathan | Open |

## Critical Blocker Categories

- wrong meaning
- hallucinated content
- publicly callable upstream inference endpoint

These are release blockers for v1.

## Review Cadence

- Weekly review during active implementation
- Immediate escalation for any risk with exposure >= `16`
- Do not mark a risk closed without a measurable check or written decision record
