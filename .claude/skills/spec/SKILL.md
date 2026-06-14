---
name: spec
description: Interview the user to define a small, well-scoped spec for a new piece of work before coding. Use at the start of a new feature, model, or forecast, or when the user runs /spec.
---

# Spec builder

Interview me to find the real goal of this work. Bias toward small, compartmentalized specs.
Make me verify key decisions explicitly so nothing is missed.

Steps:
1. Uncover the goal: what should concretely be better at the end (business / logistics / BI)?
2. Be agile: ask how I work and which constraints apply
   (Snowflake roles, schemas, Airflow schedule, Power BI consumption).
3. Be precise: write a short spec to `docs/specs/active/<topic>.md` with
   target(s), features, holdout window, acceptance criterion (e.g. MAPE threshold),
   and the name of the output view. Mark open decisions I still need to make.
