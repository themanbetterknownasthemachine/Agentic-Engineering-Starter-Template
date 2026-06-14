---
name: criteria
description: Define precise, machine-checkable evaluation criteria (Definition of Done) before building. Use when starting work that needs a quality bar, or when the user runs /criteria.
---

# Criteria builder

Before we start, outline precisely the evaluation criteria that ensure a high-quality result:
1. Set the criteria up front and measurable (MAPE threshold, bias near zero,
   no negative values, plausibility within 3 SD).
2. Propose how a second model (the `review` skill or a subagent) can critique the result.
3. Name the external signal we can pull in (holdout actuals, prior-year value -364 days).
Write the criteria as a checkable list that becomes the Definition of Done in CLAUDE.md.
