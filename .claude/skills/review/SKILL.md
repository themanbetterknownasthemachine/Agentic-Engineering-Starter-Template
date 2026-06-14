---
name: review
description: Act as a second-AI critic. Review a change or output against the project's Definition of Done and evaluation criteria, and report concrete issues. Use before deploy, or when the user runs /review.
---

# Review (second-AI critic)

Review the current change or output critically against the Definition of Done in CLAUDE.md
and the criteria in `docs/specs/active/`. Do not rubber-stamp.

Check specifically:
- Does the verifier pass (`python eval/eval_forecast.py`, exit 0)?
- Any feature leakage or a coefficient that is semantically implausible?
- For Power BI measures: do they return only numeric or BLANK(), never a Variant type?
- Tests, lint, and type checks green? Docs updated? No secrets committed?

Report issues as a short, prioritized, actionable list. If something is unclear, ask before approving.
