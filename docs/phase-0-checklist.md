# Phase 0 Checklist

## Why this exists

Phase 0 is where projects either become predictable or chaotic. This checklist forces clarity before coding.

## How to use

- Add an owner and due date to each item.
- Only mark done when the `Done Criteria` is satisfied.
- Keep blockers visible in a weekly review.
- Planning assumption: solo side project (part-time cadence).

## Checklist

| ID | Task | Why It Matters | Owner | Due | Done Criteria | Status |
|---|---|---|---|---|---|---|
| P0-00 | Lock collaboration protocol for the active working mode | Keeps repo instructions aligned with how implementation is actually happening | Nathan | 2026-02-22 | Protocol recorded in decision record + AGENTS.md | Done |
| P0-01 | Confirm translation-only scope for both directions | Prevents hidden scope creep | Nathan | 2026-02-24 | Scope sentence approved in writing | Done |
| P0-02 | Freeze MVP decision record for Modal + Cloudflare stack | Keeps all planning docs aligned | Nathan | 2026-02-24 | `mvp-decision-record.md` signed off | Done |
| P0-03 | Define latency SLOs | Avoids vague "fast enough" debates later | Nathan | 2026-02-26 | warm/cold targets documented in API + architecture docs | Done |
| P0-04 | Freeze translation-only prompt contract | Prevents API and eval drift | Nathan | 2026-02-26 | Prompt instructions written and accepted | Done |
| P0-05 | Confirm model, quant candidates, and baseline decoding settings | Reproducibility starts here | Nathan | 2026-03-01 | Model/quant memo recorded | Done |
| P0-06 | Draft licensing sign-off path | Launches fail here if delayed | Nathan | 2026-03-05 | Legal checklist with approver names | Todo |
| P0-07 | Define immutable eval set | Prevents accidental benchmark leakage | Nathan | 2026-03-08 | Fixed v1 eval composition, case-ID rules, and storage posture are documented in `docs/evaluation-plan.md` | Done |
| P0-08 | Choose human review workflow | Needed for meaning and dialect checks | Nathan | 2026-03-10 | Review rubric, reviewer model, sample minimums, and release thresholds are documented in `docs/evaluation-plan.md` | Done |
| P0-09 | Finalize API contract v1 | Enables FE/BE parallel work | Nathan | 2026-03-12 | `api-spec.md` records the `500`-character cap, stable response shape, and v1 error taxonomy | Done |
| P0-10 | Confirm observability events | Needed to debug latency and regressions | Nathan | 2026-03-14 | Required logs/metrics list approved | Todo |

## Early Decisions

1. What is the exact v1 input cap?
- Recommendation: set one hard cap early and reject larger inputs with `413`.

2. Which quant ships first?
- Recommendation: `Q4_K_M` unless `Q5_K_M` wins clearly on the eval set.

3. When is `min_containers=1` justified?
- Recommendation: only for demos if cold starts miss the published target.

4. What is the first no-go release condition?
- Recommendation: wrong meaning, hallucinated output, or an unprotected upstream endpoint.

## Decisions Locked During This Phase

- The v1 evaluation set is fixed at `180` examples across both directions and special-case categories.
- Nathan is the primary required reviewer for quant benchmarking and pre-launch signoff.
- `wrong_meaning`, `hallucination`, and `non_translation_output` are hard blockers in release review.
- The public API is capped at `500` Unicode characters for v1, with `413` for oversized input.

## Exit Criteria for Phase 0

- All P0 items have owner + due date.
- `P0-01` through `P0-09` completed except explicitly deferred launch/legal items.
- Remaining risks are documented with explicit mitigation owners.
