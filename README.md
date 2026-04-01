# Sovereign Debt Observatory

An end-to-end ELT pipeline ingesting World Bank external debt data across 130+ countries from 1998 to 2025, transforming it into analysis-ready models in BigQuery and visualizing global debt trends in Looker Studio.

## Problem Statement

Global external debt data is published by the World Bank across multiple databases but has no ready-made analytical layer. This project builds a reproducible ELT pipeline that answers five core questions:

1. How is gross external debt distributed across government, central bank, and private sectors per country?
2. Which countries carry the highest short-term external debt exposure and how has that changed since 2010?
3. What share of external debt is foreign-currency denominated and where is that ratio worsening?
4. How has regional external debt stock evolved quarterly from 2010 to 2025?
5. Which countries face the heaviest debt service pressure relative to total debt position?

## Architecture

World Bank API (IDS source 2) and QEDS SDDS Excel bulk downloads feed into PySpark jobs running in Docker containers. Raw Parquet files land in Google Cloud Storage, get loaded into BigQuery, transformed by dbt Cloud into staging and mart models, and visualized in Looker Studio. Apache Airflow on Docker Compose orchestrates the full pipeline quarterly. Terraform provisions all GCP infrastructure.

## Tech Stack

| Layer | Tool |
|---|---|
| Infrastructure | Terraform |
| Ingestion | PySpark on Docker |
| Orchestration | Apache Airflow (Docker Compose) |
| Data Lake | Google Cloud Storage |
| Data Warehouse | BigQuery |
| Transformation | dbt Cloud |
| Dashboard | Looker Studio |

## Data Sources

- **IDS (International Debt Statistics)** - World Bank source 2, 9 debt stock series, 130+ countries, 1998-2025
- **QEDS SDDS** - World Bank Quarterly External Debt Statistics, debt payment schedules by sector and maturity

## Project Structure
```
sovereign-debt-observatory/
    terraform/       - GCS bucket + BigQuery datasets + IAM
    ingestion/       - PySpark extract + load scripts + Dockerfile
    airflow/         - DAGs + Docker Compose
        dags/        - debt_pipeline_dag.py
    scripts/         - GCP bootstrap script
    .env.example     - Environment variable template
    README.md
```

## Quickstart

### 1. GCP setup
```bash
BILLING_ACCOUNT=your-billing-id bash scripts/setup_gcp.sh
```

### 2. Provision infrastructure
```bash
cd terraform
terraform init
terraform apply
```

### 3. Run ingestion
```bash
docker build -t sovereign-debt-ingestion:v1 ./ingestion

docker run --rm \
  -v /path/to/credentials/key.json:/app/credentials/key.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/key.json \
  -e GCS_BUCKET=sovereign-debt-obs-data-lake \
  sovereign-debt-ingestion:v1 python3 extract_jedh.py

docker run --rm \
  -v /path/to/credentials/key.json:/app/credentials/key.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/key.json \
  -e GCS_BUCKET=sovereign-debt-obs-data-lake \
  sovereign-debt-ingestion:v1 python3 extract_qeds.py
```

### 4. Start Airflow
```bash
cd airflow
cp ../.env.example .env
echo "AIRFLOW_UID=$(id -u)" >> .env
docker compose up airflow-init
docker compose up -d
```

### 5. dbt Cloud
Connect dbt Cloud to BigQuery and this GitHub repo. Run staging and mart models.

## Dashboard

Looker Studio dashboard link added after deployment.

## Author

Ryan Derrick Giggs
- LinkedIn: https://linkedin.com/in/ryan-giggs-a19330265
- GitHub: https://github.com/Derrick-Ryan-Giggs
