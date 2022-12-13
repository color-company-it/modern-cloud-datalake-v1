from codebase.infrastructure_mappings import EXTRACT_TYPES


def generate_sql_where_condition(
    hwm_col_name: str, lwm_value: str, hwm_value: str, extract_type: str
) -> str:
    """
    Generate a SQL WHERE condition that filters records by a high watermark column.

    :param hwm_col_name: The name of the high watermark column.
    :param lwm_value: The low watermark value for the high watermark column.
    :param hwm_value: The high watermark value for the high watermark column.
    :param extract_type: Either `FE` for full extract, or `PE` for partial extract.
    :returns: A string containing the generated SQL WHERE condition.
    """

    if extract_type == "FE":
        return ""
    if extract_type == "PE":
        return f"""
    WHERE {hwm_col_name} > {lwm_value} and {hwm_col_name} <= {hwm_value}
    """.strip()

    raise ValueError(
        f"The provided extract_type: {extract_type} is not a supported one"
        f"of {EXTRACT_TYPES} for the generate_sql_where_condition method"
    )


def generate_sql_pushdown_query(extract_table: str, sql_where_condition: str) -> str:
    """
    Generate a SQL Pushdown query using a FROM clause, WHERE condition, and table name.

    :param extract_table: The namespace of the table being extracted, such as
                          db_name.db_schema.db_table or whatever other namespace is
                          applicable.
    :param sql_where_condition: SQL WHERE condition to be used in the query
    :returns: A string representing the generated SQL Pushdown query
    """
    return f"""
    (SELECT * FROM {extract_table} {sql_where_condition}) {extract_table.split('.')[-1]}_alias
    """.strip()


def parse_extract_table(extract_table: str) -> dict:
    """
    Parse the extract_table variable and return a dictionary containing the database name, schema, and table name.

    :param extract_table: A string representing the database, schema, and table to be extracted in the format of
    "<db_name>.<db_schema>.<db_table>" or "<db_name>.<db_table>" or "<db_table>"
    :returns: A dictionary containing the database name, schema, and table name
    :raises ValueError: If the extract_table variable does not have one of the three formats mentioned above
    """
    parts = extract_table.split(".")

    # Return a dictionary containing the database name, schema, and table name
    # The value of each key is set to None if not specified in the extract_table variable
    return {
        "db_name": parts[0] if len(parts) >= 1 else None,
        "db_schema": parts[1] if len(parts) >= 2 else None,
        "db_table": parts[2] if len(parts) >= 3 else None,
    }
