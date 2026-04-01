from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
import os

default_args = {
    "owner": "sovereign-debt-observatory",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

dbt_job_id_raw = os.environ.get("DBT_CLOUD_JOB_ID", "0")
dbt_job_id = int(dbt_job_id_raw) if dbt_job_id_raw.isdigit() else 0

credentials_mount = Mount(
    target="/app/credentials/key.json",
    source="/mnt/storage/Desktop/sovereign-debt-observatory/credentials/sovereign-debt-sa-key.json",
    type="bind",
    read_only=True,
)

with DAG(
    dag_id="sovereign_debt_pipeline",
    default_args=default_args,
    description="Quarterly ELT pipeline — World Bank IDS + QEDS to BigQuery via GCS",
    schedule_interval="0 6 1 1,4,7,10 *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["sovereign-debt", "elt", "worldbank"],
) as dag:

    extract_load_jedh = DockerOperator(
        task_id="extract_load_jedh",
        image="sovereign-debt-ingestion:v1",
        command="python3 extract_jedh.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        environment={
            "GOOGLE_APPLICATION_CREDENTIALS": "/app/credentials/key.json",
            "GCS_BUCKET": os.environ.get("GCS_BUCKET", "sovereign-debt-obs-data-lake"),
        },
        mounts=[credentials_mount],
        auto_remove="success",
        mount_tmp_dir=False,
    )

    extract_load_qeds = DockerOperator(
        task_id="extract_load_qeds",
        image="sovereign-debt-ingestion:v1",
        command="python3 extract_qeds.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        environment={
            "GOOGLE_APPLICATION_CREDENTIALS": "/app/credentials/key.json",
            "GCS_BUCKET": os.environ.get("GCS_BUCKET", "sovereign-debt-obs-data-lake"),
        },
        mounts=[credentials_mount],
        auto_remove="success",
        mount_tmp_dir=False,
    )

    extract_load_jedh >> extract_load_qeds
