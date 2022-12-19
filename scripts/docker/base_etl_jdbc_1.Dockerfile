# docker build -t jdbc_etl -f scripts/docker/base_etl_jdbc_1.Dockerfile .
# docker run -e EDL_TYPE=extract -e SCRIPT_NAME=pipeline_extract_dev_jdbc_1.py -e ENGINE=postgres -e EXTRACT_TABLE=postgres.Customers -e DB_HOST=localhost -e DB_PORT=__ -e AWS_SECRET_ARN=__ -e HWM_COL_NAME=__ -e hwm_value=__ -e lwm_value=__ -e partition_column=__ -e num_partitions=__ -e lower_bound=__ -e upper_bound=__ -e fetchsize=__ -e repartition_dataframe=__ -e extract_s3_uri=__ -e aws_region="eu-west-1" jdbc_etl
FROM openjdk:8

# Install Hadoop
RUN wget https://archive.apache.org/dist/spark/spark-3.3.0/spark-3.3.0-bin-hadoop3.tgz
RUN tar xzf spark-3.3.0-bin-hadoop3.tgz
RUN mv spark-3.3.0-bin-hadoop3 /usr/local/spark

# Install Python 3.9
RUN apt-get update && apt-get install -y python3.9 python3-pip

# Install requirements.txt
COPY ../../requirements.txt /
RUN pip3 install -r requirements.txt

# Set environment variables
ENV HADOOP_HOME /usr/local/hadoop
ENV SPARK_HOME /usr/local/spark
ENV PATH $PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin

# Add Codebase & Copy scripts into Work Dir
WORKDIR app/
COPY ../../scripts/docker/base_etl_jdbc_1.sh ./
COPY ../../codebase/ codebase/
COPY ../../scripts/spark/jdbc/* ./

ENTRYPOINT ["bash", "base_etl_jdbc_1.sh"]
