#!/bin/bash

# Determine the pipeline type
if [ "$EDL_TYPE" == "extract" ]; then
  echo "Running Extract Pipeline"
  if [ -z "$FETCHSIZE" ]; then
    FETCHSIZE="1000"
  fi

  spark-submit "${SCRIPT_NAME}" \
    --extract_type "${EXTRACT_TYPE}" \
    --db_engine "${DB_ENGINE}" \
    --db_secret "${DB_SECRET}" \
    --db_port "${DB_PORT}" \
    --db_name "${DB_NAME}" \
    --partition_column "${PARTITION_COLUMN}" \
    --lower_bound "${LOWER_BOUND}" \
    --upper_bound "${UPPER_BOUND}" \
    --num_partitions "${NUM_PARTITIONS}" \
    --fetchsize "${FETCHSIZE}" \
    --extract_table "${EXTRACT_TABLE}" \
    --extract_type "${EXTRACT_TYPE}" \
    --hwm_col_name "${HWM_COL_NAME}" \
    --lwm_value "${LWM_VALUE}" \
    --hwm_value "${HWM_VALUE}" \
    --hwm_column_type "${HWM_COLUMN_TYPE}" \
    --repartition_dataframe "${REPARTITION_DATAFRAME}" \
    --extract_s3_partitions "${EXTRACT_S3_PARTITIONS}" \
    --extract_s3_uri "${EXTRACT_S3_URI}" \
    --reingest "${REINGEST}" \
    --tracking_table_name "${TRACKING_TABLE_NAME}" \
    --jars ./jars/mysql-connector-j-8.0.31.jar,./jars/postgresql-42.5.1.jar

elif [ $EDL_TYPE == "transform" ]; then
  echo "Running Transform Pipeline"

elif [ $EDL_TYPE == "load" ]; then
  echo "Running Load Pipeline"

else
  echo "No EDL_TYPE specified"

fi
