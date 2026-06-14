# Architecture

> TODO: Architektur dieses Projekts beschreiben (Data Vault Layer, Schemas, Modell-Fluss,
> Forecast-Pipeline, Power-BI-Konsum). Diese Datei wird von der CLAUDE.md per @import referenziert.

## Schichten
- Raw Vault -> Business Vault -> Gold / Marts (Snowflake, Data Vault 2.0)
- ML: BUT_LANDING.{ML, ML_REGISTRY, ML_INFERENCE, ML_MONITORING}

## Forecast-Pipeline
- TODO: Training, Inferenz, Output-Views, Airflow-DAG, Monitoring.
