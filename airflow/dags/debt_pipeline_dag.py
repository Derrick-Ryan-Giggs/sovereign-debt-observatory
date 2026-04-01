from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from airflow.models import Variable
import os

default_args = {
    "owner": "sovereign-debt-observatory",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="sovereign_debt_pipeline",
    default_args=default_args,
    description="Quarterly ELT pipeline — World Bank JEDH + QEDS to BigQuery via GCS",
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
            "GOOGLE_APPLICATION_CREDENTIALS": "/app/credentials/sovereign-debt-sa-key.json",
            "GCS_BUCKET": os.environ.get("GCS_BUCKET", "sovereign-debt-obs-data-lake"),
        },
        volumes=["/mnt/storage/Desktop/sovereign-debt-observatory/credentials:/app/credentials"],
        auto_remove=True,
    )

    extract_load_qeds = DockerOperator(
        task_id="extract_load_qeds",
        image="sovereign-debt-ingestion:v1",
        command="python3 extract_qeds.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        environment={
            "GOOGLE_APPLICATION_CREDENTIALS": "/app/credentials/sovereign-debt-sa-key.json",
            "GCS_BUCKET": os.environ.get("GCS_BUCKET", "sovereign-debt-obs-data-lake"),
        },
        volumes=["/mnt/storage/Desktop/sovereign-debt-observatory/credentials:/app/credentials"],
        auto_remove=True,
    )

    transform_dbt = DbtCloudRunJobOperator(
        task_id="transform_dbt_cloud",
        dbt_cloud_conn_id="dbt_cloud_default",
        job_id=int(os.environ.get("DBT_CLOUD_JOB_ID", 0)),
        check_interval=30,
        timeout=3600,
    )

    [extract_load_jedh, extract_load_qeds] >> transform_dbt
