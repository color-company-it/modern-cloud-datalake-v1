FROM base_pyspark

# Add Codebase & Copy scripts into Work Dir
WORKDIR app/
COPY scripts/docker/etl_jdbc/base_etl_jdbc_1.sh ./
COPY ../../../codebase/ codebase/
COPY ../../../scripts/spark/* ./

ENTRYPOINT ["bash", "base_etl_jdbc_1.sh"]