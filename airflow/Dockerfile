FROM apache/airflow:2.9.2
USER airflow
RUN pip install --no-cache-dir \
    "apache-airflow-providers-dbt-cloud" \
    "apache-airflow-providers-docker" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.2/constraints-3.12.txt"
