import difflib
import logging
from typing import Dict, Any, Tuple

import mysql.connector
import psycopg2
from pyspark.sql.types import *

from codebase.etl import DATA_TYPE_MAPPING, MIN_VALUES


def convert_db_namespaces(extract_table: str, db_name: str, db_engine: str) -> str:
    """
    Converts the database namespaces in the specified extract table based on the database engine.

    :params extract_table: a string representing the extract table whose namespaces are to be converted.
    :params db_name: a string representing the name of the database.
    :params db_engine: a string representing the database engine (e.g. "postgres", "mysql").

    :returns: A string representing the converted database namespaces for the specified extract table.
    """
    if db_engine == "postgres":
        result = '"."'.join(extract_table.split("."))
        db_namespaces = f'"{db_name}"."{result}"'
    elif db_engine == "mysql":
        result = "`.`".join(extract_table.split("."))
        db_namespaces = f"`{db_name}`.`{result}`"
    else:
        raise EnvironmentError(f"The db_engine: {db_engine} is not supported")

    logging.info(
        f"Converted db_namespaces using extract_table: "
        f"{extract_table}, db_name: {db_name}, and db_engine: {db_engine}.\n"
        f"To db_namespaces: {db_namespaces}"
    )
    return db_namespaces


def get_sql_where_condition(
    extract_type, lwm_value, hwm_col_name, hwm_value, hwm_column_type, reingest
):
    if extract_type == "FE":
        sql_where_condition = ""
    elif extract_type == "PE":
        if reingest:
            try:
                logging.warning(
                    "Source is being reingested, all original data may be overwritten!"
                )
                sql_where_condition = (
                    f"WHERE {hwm_col_name} > '{MIN_VALUES[hwm_column_type]}'"
                )
            except KeyError as err:
                raise KeyError(
                    f"The provided hwm_column_type: {hwm_column_type} is not a valid option"
                ) from err
        else:
            # if hwm is -1 it means we need to pull in all newest data
            if hwm_value == "-1":
                sql_where_condition = f"WHERE {hwm_col_name} > '{lwm_value}'"
            else:
                sql_where_condition = f"WHERE {hwm_col_name} > '{lwm_value}' and {hwm_col_name} <= '{hwm_value}'"
    else:
        raise EnvironmentError(f"The _extract_type: {extract_type} is not supported")

    logging.info(f"Got SQL WHERE condition: {sql_where_condition}")
    return sql_where_condition


def get_pushdown_query(
    extract_table: str, sql_where_condition: str, db_name: str
) -> str:
    """
    Get a pushdown query to extract data from a database table.

    :params extract_table (str): The name of the table to extract data from.
    :params sql_where_condition (str): The WHERE clause to use in the SELECT statement.
    :params db_name (str): The name of the database.
    :returns: A string representing the pushdown query.
    """
    pushdown_query = (
        f"(SELECT * FROM {extract_table} {sql_where_condition}) {db_name}_alias"
    )
    logging.info(f"Got pushdown query: {pushdown_query}")
    return pushdown_query


def get_jdbc_url(db_host: str, db_port: int, db_name: str, db_engine: str) -> str:
    """
    Returns a JDBC URL based on the specified database engine.

    :params db_host: a string representing the hostname of the database.
    :params db_port: an integer representing the port number of the database.
    :params db_name: a string representing the name of the database.
    :params db_engine: a string representing the database engine (e.g. "postgres", "mysql").
    :returns: A string representing the JDBC URL for the specified database.
    """
    if db_engine == "postgres":
        jdbc_url = f"jdbc:postgresql://{db_host}:{db_port}/{db_name}"
    elif db_engine == "mysql":
        jdbc_url = f"jdbc:mysql://{db_host}:{db_port}/{db_name}"
    else:
        raise EnvironmentError(f"The engine: {db_engine} is not supported")
    logging.info(f"Got JDBC URL: {jdbc_url}")
    return jdbc_url


def get_column_data_types(
    engine: str,
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    table_name: str,
) -> Dict[str, str]:
    """
    Get the data types of the columns in a database table.

    :params engine (str): The database engine.
    :params host (str): The hostname of the database server.
    :params port (int): The port number of the database server.
    :params database (str): The name of the database.
    :params user (str): The username to use for connecting to the database.
    :params password (str): The password to use for connecting to the database.
    :params table_name (str): The name of the table.
    :returns: A dictionary mapping column names to data types.
    """

    if engine == "postgres":
        conn = psycopg2.connect(
            host=host, port=port, database=database, user=user, password=password
        )
        query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
    elif engine == "mysql":
        conn = mysql.connector.connect(
            host=host, port=port, database=database, user=user, password=password
        )
        query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
    else:
        raise EnvironmentError(f"The engine: {engine} is not supported")

    cursor = conn.cursor()

    # Query the database to get the column names and data types
    cursor.execute(query)

    # Fetch the results of the query
    column_data_types = cursor.fetchall()

    # Create a dictionary to store the column names and data types
    column_data_type_dict = {}

    # Iterate through the column data types and add them to the dictionary
    for column_data_type in column_data_types:
        column_name, data_type = column_data_type
        column_data_type_dict[column_name] = data_type

    return column_data_type_dict


def create_db_table_schema(
    db_engine: str,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_password: str,
    extract_table: str,
) -> StructType:
    """
    Create the schema for a database table by inferring the data types of the columns.

    :params db_engine (str): The database engine.
    :params db_host (str): The hostname of the database server.
    :params db_port (int): The port number of the database server.
    :params db_name (str): The name of the database.
    :params db_user (str): The username to use for connecting to the database.
    :params db_password (str): The password to use for connecting to the database.
    :params extract_table (str): The name of the table to extract.
    :returns: A StructType object representing the schema of the table.
    """
    logging.info(f"Getting {extract_table} schema for inferring datatypes.")
    db_table = extract_table.split(".")[-1]

    # Convert the DataFrame to a dictionary
    source_schema: dict = get_column_data_types(
        engine=db_engine,
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password,
        table_name=db_table,
    )
    spark_schema: dict = DATA_TYPE_MAPPING[db_engine]
    logging.info(f"Source Schema: {source_schema}")
    new_schema_struct = []
    for source_column, source_type in source_schema.items():
        closest_match = difflib.get_close_matches(source_type, spark_schema.keys())
        if closest_match:
            try:
                logging.info(
                    f"Casting column: {source_column} from {source_type} to {spark_schema[closest_match[0]]}"
                )
                new_schema_struct.append(
                    StructField(source_column, spark_schema[closest_match[0]], True)
                )
            except KeyError as error:
                logging.info(
                    "Casting column: {source_column} not found in mapping, defaulting to StringType"
                )
                new_schema_struct.append(StructField(source_column, StringType(), True))
        else:
            logging.info(
                f"Casting column: {source_column} from {source_type} to StringType"
            )
            new_schema_struct.append(StructField(source_column, StringType(), True))

    return StructType(new_schema_struct)


def determine_extract_plan(
    provided_hwm_value: Any,
    provided_lwm_value: Any,
    extract_type: str,
    tracking_table: Dict[str, Any],
) -> Tuple[Any, Any]:
    """
    Determines the extract plan based on the provided extract type. If the extract type is 'FE',
    the provided high and low watermark values are returned. If the extract type is 'PE', the
    tracking table is checked for the high and low watermark values. If the tracking table is
    empty, the provided high and low watermark values are returned. If the extract type is not
    'FE' or 'PE', a ValueError is raised.

    :params provided_hwm_value (Any): The provided high watermark value.
    :params provided_lwm_value (Any): The provided low watermark value.
    :params extract_type (str): The type of extract. Can be either 'FE' or 'PE'.
    :params tracking_table (Dict[str, Any]): A dictionary containing the tracking table for the extract.
                                      The keys 'hwm_value' and 'lwm_value' should contain the
                                      high and low watermark values, respectively.

    :returns: Tuple[Any, Any]: A tuple containing the high and low watermark values to use for the extract.
    """
    # return the provided values if FE and that's it
    if extract_type == "FE":
        return provided_hwm_value, provided_lwm_value

    # determine if this is a new run, then return the provided values or ddb values
    elif extract_type == "PE":
        if tracking_table:
            return tracking_table["hwm_value"]["S"], tracking_table["lwm_value"]["S"]
        return provided_hwm_value, provided_lwm_value

    else:
        raise ValueError(f"Extract type {extract_type} is not supported")
