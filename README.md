# Sovereign Debt Observatory

An end-to-end ELT pipeline ingesting World Bank external debt data across 130+ countries from 1998 to 2025, transforming it into analysis-ready models in BigQuery and visualizing global debt trends in Looker Studio.

## Problem Statement

Global external debt data is published by the World Bank across multiple databases but has no ready-made analytical layer on top of it. Answering even basic questions like which countries are most exposed to short-term debt, or how Africa's public sector debt burden has shifted post-COVID, requires manually downloading scattered Excel files, cleaning inconsistent formats, and stitching together multiple tables.

This project builds a fully reproducible ELT pipeline that answers five core analytical questions:

1. How is gross external debt distributed across public, publicly guaranteed, private nonguaranteed, and multilateral sectors per country?
2. Which countries carry the highest short-term external debt exposure and how has that changed since 2010?
3. What share of external debt is foreign-currency denominated and where is that ratio worsening?
4. How has regional external debt stock evolved from 1998 to 2025 across Africa, Latin America, East Asia, South Asia, Europe and Central Asia, and the Middle East?
5. Which countries face the heaviest debt service pressure relative to their total debt position?

## Architecture

Raw data is extracted from the World Bank API and QEDS Excel bulk downloads using PySpark jobs running in Docker containers. The raw Parquet files land in Google Cloud Storage partitioned by extraction date. BigQuery external tables point directly at the GCS Parquet files. dbt Cloud runs staging models that clean and unpivot the raw data, then mart models that compute debt ratios, YoY changes, and regional aggregates. Apache Airflow on Docker Compose orchestrates the full pipeline on a quarterly schedule. Terraform provisions all GCP infrastructure from scratch.

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Infrastructure | Terraform | Provision GCS bucket and BigQuery datasets |
| Ingestion | PySpark + Docker | Extract from World Bank API, write Parquet to GCS |
| Orchestration | Apache Airflow (Docker Compose) | Quarterly batch pipeline orchestration |
| Data Lake | Google Cloud Storage | Raw Parquet files partitioned by extracted_date |
| Data Warehouse | BigQuery | External tables + staging + mart datasets |
| Transformation | dbt Cloud | Staging views + partitioned and clustered mart tables |
| Dashboard | Looker Studio | Two-page interactive dashboard |

## Data Sources

### IDS — International Debt Statistics (World Bank source 2)
- Access: World Bank Indicators API v2 via wbgapi Python library
- Coverage: 130+ countries, 1998–2025, annual
- Series ingested:
  - `DT.DOD.DECT.CD` — Total external debt stocks
  - `DT.DOD.DLXF.CD` — Long-term external debt
  - `DT.DOD.DPNG.CD` — Private nonguaranteed debt
  - `DT.DOD.MIBR.CD` — PPG IBRD loans
  - `DT.DOD.DPPG.CD` — Public and publicly guaranteed debt
  - `DT.DOD.DIMF.CD` — IMF credit
  - `DT.DOD.PVLX.CD` — Present value of external debt
  - `DT.DOD.MWBG.CD` — IBRD loans and IDA credits
  - `DT.DOD.MIDA.CD` — PPG IDA loans

### QEDS SDDS — Quarterly External Debt Statistics (World Bank)
- Access: Direct Excel bulk downloads from World Bank DataBank
- Coverage: 73 SDDS participating countries, quarterly
- Tables ingested:
  - SDDS Table 1.5 — Net external debt position by sector
  - SDDS Table 3 — Debt service payment schedule by sector
  - SDDS Table 3.2 — Debt service by sector and instrument
  - SDDS Table 2.1 — Foreign currency and domestic currency debt
  - SDDS Table 1.6 — Reconciliation of positions and flows

## Project Structure

```
sovereign-debt-observatory/
├── terraform/
│   ├── main.tf              # GCS bucket, BigQuery datasets (raw, staging, mart)
│   ├── variables.tf         # Input variables
│   ├── outputs.tf           # Bucket URL, dataset IDs
│   └── terraform.tfvars     # Your values (gitignored)
├── ingestion/
│   ├── extract_jedh.py      # PySpark: fetch IDS API series, write Parquet to GCS
│   ├── extract_qeds.py      # Pandas + GCS client: download QEDS Excel, write Parquet
│   ├── spark_session.py     # Shared SparkSession with GCS connector config
│   ├── Dockerfile           # eclipse-temurin:17-jdk-jammy + Spark 3.5.1 + GCS connector
│   └── requirements.txt     # wbgapi, pyspark, google-cloud-storage, pandas, pyarrow
├── airflow/
│   ├── dags/
│   │   └── debt_pipeline_dag.py  # Quarterly DAG: JEDH, QEDS, dbt Cloud trigger
│   ├── docker-compose.yml        # Airflow services: webserver, scheduler, worker, triggerer
│   └── .env                      # Airflow and dbt Cloud credentials (gitignored)
├── scripts/
│   └── setup_gcp.sh         # Bootstrap GCP project, APIs, service account, SA key
├── .env.example             # Template for all required environment variables
└── README.md
```

## dbt Models

```
models/
├── staging/
│   ├── sources.yml          # BigQuery external table source definitions
│   ├── stg_jedh.sql         # Unpivot wide year columns to long format, cast types
│   ├── stg_qeds.sql         # Select clean columns, safe_cast quarter values to float64
│   └── schema.yml           # Column descriptions and not_null tests
└── mart/
    ├── mart_debt_stocks.sql     # Partitioned by year, clustered by country + series, YoY change
    ├── mart_regional_debt.sql   # Regional aggregates by series and year
    ├── mart_debt_service.sql    # Debt payment totals and quarterly averages by country
    └── schema.yml               # Column descriptions and not_null tests
```

## Dashboard

Two-page Looker Studio dashboard connected to the three mart tables in BigQuery.

**Page 1 — Global Debt Overview:**
- Total global external debt scorecard (latest year)
- Regional debt trajectory time series 1998–2024
- Top 20 countries by total debt stock bar chart
- Year filter control

**Page 2 — Country Deep-Dive and Debt Sustainability:**
- Scorecards: total debt, public and publicly guaranteed debt, private nonguaranteed debt
- Debt composition stacked bar by sector over time (answers Q1)
- Short-term vulnerability line chart — top countries by private nonguaranteed debt (answers Q2)
- Debt service pressure table with quarterly payment totals (answers Q5)
- Country filter control

Dashboard: [Sovereign Debt Observatory — Looker Studio](https://lookerstudio.google.com/reporting/7fc18e9e-a5c6-4616-b920-b5b4bddf2264)

## Reproducibility Steps

### Prerequisites
- GCP account with billing enabled
- Docker and Docker Compose installed
- Terraform >= 1.3 installed
- gcloud CLI installed and authenticated (`gcloud auth login`)
- dbt Cloud account (free developer plan)

### Step 1 — Clone the repo
```bash
git clone https://github.com/Derrick-Ryan-Giggs/sovereign-debt-observatory.git
cd sovereign-debt-observatory
cp .env.example .env
```

### Step 2 — GCP bootstrap
```bash
BILLING_ACCOUNT=your-billing-account-id bash scripts/setup_gcp.sh
```

Creates the GCP project, enables BigQuery and GCS APIs, creates a service account with `bigquery.admin` and `storage.admin` roles, and downloads the SA key to `credentials/sovereign-debt-sa-key.json`.

### Step 3 — Provision infrastructure
```bash
cd terraform
terraform init
terraform apply
```

Provisions the GCS bucket `sovereign-debt-obs-data-lake` and three BigQuery datasets: `raw`, `staging`, and `mart`.

### Step 4 — Build ingestion image
```bash
cd ../ingestion
docker build -t sovereign-debt-ingestion:v1 .
```

### Step 5 — Run ingestion
```bash
docker run --rm \
  -v $(pwd)/../credentials/sovereign-debt-sa-key.json:/app/credentials/key.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/key.json \
  -e GCS_BUCKET=sovereign-debt-obs-data-lake \
  sovereign-debt-ingestion:v1 python3 extract_jedh.py

docker run --rm \
  -v $(pwd)/../credentials/sovereign-debt-sa-key.json:/app/credentials/key.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/key.json \
  -e GCS_BUCKET=sovereign-debt-obs-data-lake \
  sovereign-debt-ingestion:v1 python3 extract_qeds.py
```

### Step 6 — Create BigQuery external tables

Check the extraction date from GCS:

```bash
gsutil ls gs://sovereign-debt-obs-data-lake/raw/jedh/
```

Create external table definition files — replace `YYYY-MM-DD` with the actual partition date:

```bash
cat > /tmp/jedh_ext.json << EOF
{
  "sourceFormat": "PARQUET",
  "sourceUris": ["gs://sovereign-debt-obs-data-lake/raw/jedh/extracted_date=YYYY-MM-DD/*.parquet"],
  "hivePartitioningOptions": {
    "mode": "AUTO",
    "sourceUriPrefix": "gs://sovereign-debt-obs-data-lake/raw/jedh/"
  }
}
EOF

cat > /tmp/qeds_ext.json << EOF
{
  "sourceFormat": "PARQUET",
  "sourceUris": ["gs://sovereign-debt-obs-data-lake/raw/qeds/extracted_date=YYYY-MM-DD/qeds.parquet"],
  "hivePartitioningOptions": {
    "mode": "AUTO",
    "sourceUriPrefix": "gs://sovereign-debt-obs-data-lake/raw/qeds/"
  }
}
EOF

bq mk --table --external_table_definition=/tmp/jedh_ext.json sovereign-debt-observatory:raw.jedh
bq mk --table --external_table_definition=/tmp/qeds_ext.json sovereign-debt-observatory:raw.qeds
```

### Step 7 — dbt Cloud setup
1. Create a new project at [cloud.getdbt.com](https://cloud.getdbt.com)
2. Connect to BigQuery using the service account key at `credentials/sovereign-debt-sa-key.json`
3. Set dataset prefix to `dbt_yourname` and location to `US`
4. Connect to the dbt GitHub repo
5. Run `dbt run` then `dbt test` — all 5 models should pass

### Step 8 — Start Airflow
```bash
cd ../airflow
cp ../.env.example .env
```

Fill in `DBT_CLOUD_API_TOKEN`, `DBT_CLOUD_ACCOUNT_ID`, and `DBT_CLOUD_JOB_ID` in `.env`, then:

```bash
echo "AIRFLOW_UID=$(id -u)" >> .env
docker compose up airflow-init
docker compose up -d
```

Access the Airflow UI at `http://localhost:8080`. Default credentials: `admin` / `admin`.

Trigger the `sovereign_debt_pipeline` DAG manually or wait for the quarterly schedule — runs on the 1st of January, April, July, and October at 06:00 UTC.

### Step 9 — Looker Studio dashboard
1. Open [lookerstudio.google.com](https://lookerstudio.google.com)
2. Create a new report and add BigQuery as a data source
3. Navigate to `sovereign-debt-observatory` project, `dbt_rgiggs_mart` dataset
4. Add `mart_debt_stocks`, `mart_regional_debt`, and `mart_debt_service` tables
5. Build the two-page dashboard following the structure described above

## Environment Variables

Copy `.env.example` and fill in all values before running:

```
BILLING_ACCOUNT          # Your GCP billing account ID (setup_gcp.sh only)
GCP_PROJECT_ID           # sovereign-debt-observatory
GCS_BUCKET               # sovereign-debt-obs-data-lake
AIRFLOW_UID              # Output of: id -u
DBT_CLOUD_API_TOKEN      # dbt Cloud > Account Settings > API Tokens > Personal tokens
DBT_CLOUD_ACCOUNT_ID     # From the dbt Cloud URL when logged in
DBT_CLOUD_JOB_ID         # From dbt Cloud after creating a production job
```

## Author

Ryan Derrick Giggs

- LinkedIn: [ryan-giggs-a19330265](https://linkedin.com/in/ryan-giggs-a19330265)
- GitHub: [Derrick-Ryan-Giggs](https://github.com/Derrick-Ryan-Giggs)
- Medium: [@derrickryangiggs](https://medium.com/@derrickryangiggs)
- Dev.to: [derrickryangiggs](https://dev.to/derrickryangiggs)
