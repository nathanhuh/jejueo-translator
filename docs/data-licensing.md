# Data and Licensing Checklist

## Why this matters

Licensing ambiguity can block launch even if product quality is strong. Resolve this early.

Project posture: portfolio/research demo first.

## Licensing Checklist (Public Beta Prerequisite)

| ID | Check | Evidence Required | Owner | Status |
|---|---|---|---|---|
| L-01 | Confirm license terms for JIT dataset usage | Written source/license reference + internal note | Nathan | Todo |
| L-02 | Confirm attribution requirements | Attribution text prepared for app/docs | Nathan | Todo |
| L-03 | Confirm commercial/non-commercial constraints | Explicit legal interpretation on intended launch type | Nathan | Todo |
| L-04 | Confirm rights for supplemental dictionary data | Source-specific permission and citation notes | Nathan | Todo |
| L-05 | Confirm base model usage terms | Model card/license reviewed for deployment and output rights | Nathan | Todo |
| L-06 | Confirm GGUF quant provenance and redistribution terms | Source links and license notes for chosen quant file | Nathan | Todo |
| L-06 | Confirm data retention policy | Documented retention + deletion policy | Nathan | Todo |
| L-07 | Confirm user feedback data consent language | UI text and policy approved | Nathan | Todo |
| L-08 | Complete go/no-go legal signoff | Named approver signoff recorded | Nathan | Todo |

## Current Planning Notes

- Planned base model: `est-ai/alan-llm-jeju-dialect-v1-4b`
- Planned license expectation to verify: `Apache-2.0`
- Planned launch artifact: existing GGUF quant `Q4_K_M` as the provisional MVP default

These notes are planning assumptions until the exact source documents are reviewed and recorded.

## Portfolio Launch Mode (Fast, Lower-Risk)

Use this mode for public portfolio visibility before full production/legal hardening.

- Publish architecture, code, and demo output examples.
- Do NOT publish raw JIT data or dataset mirrors in this repository.
- Include demo-only disclaimer and attribution on README/demo page.
- Keep deployment labeled as research/portfolio preview.
- Avoid commercial claims until checklist items `L-01`, `L-03`, and `L-05` are completed.

Demo disclaimer template:

"This is a portfolio/research demo for Jejueo translation exploration. Outputs may be inaccurate, and this service is not intended for production or commercial use."

## Attribution Template (Draft)

Use in documentation/about page after legal confirmation:

"This project uses Jejueo-Korean language resources including the Jejueo datasets published by Park, Choe, and Ham (LREC 2020)."

## Initial Decisions You Should Make

1. Launch type at MVP
- Decision needed: research preview only, or public production beta?
- Why: licensing obligations can differ significantly.

2. Who signs legal release approval?
- Recommendation: as a solo builder, you are the approver; add a written self-check record before launch.

3. What is the policy for user-contributed corrections?
- Decision needed: whether corrections are used for retraining and under what consent terms.
