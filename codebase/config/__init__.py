def generate_extract_config(config) -> list:
    """
    Take the config file and set it up into a flat structure
    for the event payload for the extract pipelines.
    """
    extract = config["extract"]
    defaults = extract["default_arguments"]
    source_name = config["source_name"]
    event_arguments = []

    def default(item):
        """
        The tracking_table_config will always overwrite the default argument.
        """
        if table_config.get(item, False):
            return table_config[item]
        return defaults[item]

    for table_name, table_config in extract["tables"].items():
        config = {
            "--source_name": source_name,
            "--extract_table": table_name,
            "--job_type": extract["job_type"],
            "--source_type": extract["source_type"],
            "--db_engine": extract["db_engine"],
            "--db_secret": extract["db_secret"],
            "--db_port": f'{extract["db_port"]}',
            "--db_name": extract["db_name"],
            # opt for default arguments
            "--partition_column": default("partition_column"),
            "--lower_bound": default("lower_bound"),
            "--upper_bound": default("upper_bound"),
            "--extract_type": default("extract_type"),
            "--hwm_col_name": default("hwm_col_name"),
            "--hwm_column_type": default("hwm_column_type"),
            "--lwm_value": default("lwm_value"),
            "--hwm_value": default("hwm_value"),
            "--repartition_dataframe": default("repartition_dataframe"),
            "--extract_s3_partitions": default("extract_s3_partitions"),
            "--num_partitions": default("num_partitions"),
            "--fetchsize": default("fetchsize"),
            "--worker_no": default("worker_no"),
        }
        event_arguments.append(config)

    return event_arguments
