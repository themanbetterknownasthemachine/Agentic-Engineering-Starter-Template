---
paths:
  - "models/**/*.sql"
  - "**/*.sql"
---

# SQL / dbt rules

- Staging models: `stg_<source>__<entity>` (double underscore).
- Column names UPPER_SNAKE_CASE. No `SELECT *`.
- Every mart/output table needs a `not_null` + `unique` test on its key.
- Time intelligence always via DIM_DATE; `AT = 1` = Pistor working-day logic.
- Transformations in dbt only; never manual DDL in Snowsight.
- CSV file formats: use `DATE_FORMAT`, not `DATE_INPUT_FORMAT`.
- Large loads: Stage + `COPY INTO` (Snowsight "Load Data" ignores custom file formats).
