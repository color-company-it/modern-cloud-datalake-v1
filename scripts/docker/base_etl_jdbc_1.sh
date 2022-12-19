#!/bin/bash

# Determine the pipeline type
if [ $EDL_TYPE == "extract" ]; then
  echo "Running Extract Pipeline"
  python3 "${SCRIPT_NAME}" \
    --extract_type "${EXTRACT_TYPE}" \
    --engine "${ENGINE}" \
    --extract_table "${EXTRACT_TABLE}" \
    --db_host "${DB_HOST}" \
    --db_port "${DB_PORT}" \
    --aws_secret_arn "${AWS_SECRET_ARN}" \
    --hwm_col_name "${HWM_COL_NAME}" \
    --hwm_value "${HWM_VALUE}" \
    --lwm_value "${LWM_VALUE}" \
    --partition_column "${PARTITION_COLUMN}" \
    --num_partitions "${NUM_PARTITIONS}" \
    --lower_bound "${LOWER_BOUND}" \
    --upper_bound "${UPPER_BOUND}" \
    --fetchsize "${FETCHSIZE}" \
    --repartition_dataframe "${REPARTITION_DATAFRAME}" \
    --extract_s3_uri "${EXTRACT_S3_URI}" \
    --aws_region "$AWS_REGION"
elif [ $EDL_TYPE == "transform" ]; then
  echo "Running Transform Pipeline"
elif [ $EDL_TYPE == "load" ]; then
  echo "Running Load Pipeline"
else
  echo "No EDL_TYPE specified"
fi
