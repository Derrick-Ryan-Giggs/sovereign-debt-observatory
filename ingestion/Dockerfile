FROM eclipse-temurin:17-jdk-jammy

WORKDIR /app

RUN apt-get update && apt-get install -y     curl     procps     python3     python3-pip     && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/opt/java/openjdk
ENV SPARK_VERSION=3.5.1
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark

RUN curl --progress-bar -L     https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz     -o /tmp/spark.tgz     && tar -xzf /tmp/spark.tgz -C /opt     && mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME}     && rm /tmp/spark.tgz

RUN mkdir -p ${SPARK_HOME}/jars &&     curl --progress-bar -L     https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar     -o ${SPARK_HOME}/jars/gcs-connector-hadoop3-latest.jar

ENV PATH=$PATH:${SPARK_HOME}/bin
ENV PYSPARK_PYTHON=python3

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
