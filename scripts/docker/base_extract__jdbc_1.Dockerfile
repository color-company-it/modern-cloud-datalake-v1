FROM python:3.8-slim

RUN apt-get update && apt-get install -y openjdk-11-jre-headless wget
RUN wget -q http://www-us.apache.org/dist/spark/spark-2.4.6/spark-2.4.6-bin-hadoop2.7.tgz
RUN tar xf spark-2.4.6-bin-hadoop2.7.tgz && mv spark-2.4.6-bin-hadoop2.7 /usr/local/spark
RUN pip install pyspark hudi

ENV PATH="/usr/local/spark/bin:${PATH}"

CMD ["pyspark"]