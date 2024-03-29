def generate_extract_config(config) -> list:
    """
    Take the config file and set it up into a flat structure
    for the event payload for the extract pipelines.

    We also check to see if there is transform configs in the
    configuration file, to determine if the transformation step needs to be run.
    """
    extract = config["extract"]
    transform = config.get("transform", {})
    source_name = config["source_name"]
    source_type = config["source_type"]
    defaults = extract["default_arguments"]

    event_arguments = []

    def default(item):
        """
        The tracking_table_config will always overwrite the default argument.
        """
        if table_config.get(item, False):
            return table_config[item]
        return defaults[item]

    for table_name, table_config in extract["tables"].items():
        # Handle the event object based on the source type that is provided
        if source_type == "jdbc":
            config = {
                "source_name": source_name,
                "extract_table": table_name,
                "job_type": extract["job_type"],
                "source_type": source_type,
                "db_engine": extract["db_engine"],
                "db_secret": extract["db_secret"],
                "db_port": f'{extract["db_port"]}',
                "db_name": extract["db_name"],
                # opt for default arguments
                "partition_column": default("partition_column"),
                "lower_bound": default("lower_bound"),
                "upper_bound": default("upper_bound"),
                "extract_type": default("extract_type"),
                "hwm_col_name": default("hwm_col_name"),
                "hwm_column_type": default("hwm_column_type"),
                "lwm_value": default("lwm_value"),
                "hwm_value": default("hwm_value"),
                "repartition_dataframe": default("repartition_dataframe"),
                "extract_s3_partitions": default("extract_s3_partitions"),
                "num_partitions": default("num_partitions"),
                "fetchsize": default("fetchsize"),
                "worker_no": int(
                    default("worker_no")
                ),  # needs to be int for sf payload
                "worker_type": default("worker_type"),
                "run_transform": "true"
                if transform
                else "false",  # determine if a transform job needs to be run
            }
        else:
            raise KeyError(
                f"The source_type: {source_type} provided in the configuration is not supported"
            )

        event_arguments.append(config)

    return event_arguments
