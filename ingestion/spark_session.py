import os
from pyspark.sql import SparkSession


def get_spark_session(app_name: str) -> SparkSession:
    gcs_connector_jar = "/opt/spark/jars/gcs-connector-hadoop3-latest.jar"

    spark = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.jars", gcs_connector_jar)
        .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
        .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
        .config("spark.hadoop.google.cloud.auth.service.account.enable", "true")
        .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")
    return spark
