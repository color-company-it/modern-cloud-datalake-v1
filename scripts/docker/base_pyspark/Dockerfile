FROM amazonlinux:2 as aws_layer

MAINTAINER DirkSCGM

# Install Java
RUN yum update -y && yum install -y java-1.8.0-openjdk-devel tar curl unzip python3

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    rm -r awscliv2.zip
RUN ./aws/install

FROM aws_layer as pyspark_layer

# Install PySpark
RUN curl https://archive.apache.org/dist/spark/spark-3.1.1/spark-3.1.1-bin-hadoop2.7.tgz > spark-3.1.1-bin-hadoop2.7.tgz && \
    tar -xvf spark-3.1.1-bin-hadoop2.7.tgz && \
    mv spark-3.1.1-bin-hadoop2.7 /opt/spark && \
    rm -r spark-3.1.1-bin-hadoop2.7.tgz

FROM pyspark_layer as base_pyspark

# Install Python requirments.txt
COPY ../../../requirements.txt ./
RUN pip3 install -r requirements.txt

# Add Hadoop and Spark configuration files
COPY scripts/docker/base_pyspark/hadoop/* /opt/hadoop/etc/hadoop/
COPY scripts/docker/base_pyspark/spark/* /opt/spark/conf/

# Add JDBC Jar Files
COPY scripts/docker/base_pyspark/jars/* /opt/spark/jars/

# Set environment variables
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV SPARK_HOME=/opt/spark
ENV PYSPARK_PYTHON=python3
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin:/opt/spark/bin
ENV CLASSPATH=/opt/spark/jars/*