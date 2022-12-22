import unittest
from unittest import mock

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
)

from codebase.etl import MIN_VALUES
from codebase.etl.extract import (
    convert_db_namespaces,
    get_sql_where_condition,
    get_pushdown_query,
    get_jdbc_url,
    get_column_data_types,
    create_db_table_schema,
    determine_extract_plan,
)


class TestConvertDbNamespaces(unittest.TestCase):
    def test_postgres_conversion(self):
        extract_table = "schema.table"
        db_name = "database"
        db_engine = "postgres"

        expected_result = '"database"."schema"."table"'
        result = convert_db_namespaces(extract_table, db_name, db_engine)
        self.assertEqual(result, expected_result)

    def test_mysql_conversion(self):
        extract_table = "schema.table"
        db_name = "database"
        db_engine = "mysql"

        expected_result = "`database`.`schema`.`table`"
        result = convert_db_namespaces(extract_table, db_name, db_engine)
        self.assertEqual(result, expected_result)

    def test_unsupported_db_engine(self):
        extract_table = "schema.table"
        db_name = "database"
        db_engine = "unsupported"

        with self.assertRaises(EnvironmentError):
            convert_db_namespaces(extract_table, db_name, db_engine)


class TestGetSqlWhereCondition(unittest.TestCase):
    def test_fe_extract_type(self):
        extract_type = "FE"
        lwm_value = "123"
        hwm_col_name = "hwm_column"
        hwm_value = "456"
        hwm_column_type = "IntegerType"
        reingest = False

        expected_result = ""
        result = get_sql_where_condition(
            extract_type, lwm_value, hwm_col_name, hwm_value, hwm_column_type, reingest
        )
        self.assertEqual(result, expected_result)

    def test_pe_extract_type_with_reingest(self):
        extract_type = "PE"
        lwm_value = "123"
        hwm_col_name = "hwm_column"
        hwm_value = "456"
        hwm_column_type = "IntegerType"
        reingest = True

        expected_result = f"WHERE {hwm_col_name} > '{MIN_VALUES[hwm_column_type]}'"
        result = get_sql_where_condition(
            extract_type, lwm_value, hwm_col_name, hwm_value, hwm_column_type, reingest
        )
        self.assertEqual(result, expected_result)

    def test_pe_extract_type_with_hwm_value_minus_one(self):
        extract_type = "PE"
        lwm_value = "123"
        hwm_col_name = "hwm_column"
        hwm_value = "-1"
        hwm_column_type = "IntegerType"
        reingest = False

        expected_result = f"WHERE {hwm_col_name} > '{lwm_value}'"
        result = get_sql_where_condition(
            extract_type, lwm_value, hwm_col_name, hwm_value, hwm_column_type, reingest
        )
        self.assertEqual(result, expected_result)

    def test_pe_extract_type_with_valid_hwm_value(self):
        extract_type = "PE"
        lwm_value = "123"
        hwm_col_name = "hwm_column"
        hwm_value = "456"
        hwm_column_type = "IntegerType"
        reingest = False

        expected_result = (
            f"WHERE {hwm_col_name} > '{lwm_value}' and {hwm_col_name} <= '{hwm_value}'"
        )
        result = get_sql_where_condition(
            extract_type, lwm_value, hwm_col_name, hwm_value, hwm_column_type, reingest
        )
        self.assertEqual(result, expected_result)

    def test_pe_extract_type_with_invalid_hwm_type(self):
        extract_type = "PE"
        lwm_value = "123"
        hwm_col_name = "hwm_column"
        hwm_value = "456"
        hwm_column_type = "WrongType"
        reingest = True

        with self.assertRaises(KeyError):
            get_sql_where_condition(
                extract_type,
                lwm_value,
                hwm_col_name,
                hwm_value,
                hwm_column_type,
                reingest,
            )


class TestGetPushdownQuery(unittest.TestCase):
    def test_without_where_clause(self):
        extract_table = "table"
        sql_where_condition = ""
        db_name = "database"

        expected_result = "(SELECT * FROM table ) database_alias"
        result = get_pushdown_query(extract_table, sql_where_condition, db_name)
        self.assertEqual(result, expected_result)

    def test_with_where_clause(self):
        extract_table = "table"
        sql_where_condition = "WHERE col = 'value'"
        db_name = "database"

        expected_result = "(SELECT * FROM table WHERE col = 'value') database_alias"
        result = get_pushdown_query(extract_table, sql_where_condition, db_name)
        self.assertEqual(result, expected_result)


class TestGetJdbcUrl(unittest.TestCase):
    def test_postgres_jdbc_url(self):
        db_host = "localhost"
        db_port = 5432
        db_name = "database"
        db_engine = "postgres"

        expected_result = "jdbc:postgresql://localhost:5432/database"
        result = get_jdbc_url(db_host, db_port, db_name, db_engine)
        self.assertEqual(result, expected_result)

    def test_mysql_jdbc_url(self):
        db_host = "localhost"
        db_port = 3306
        db_name = "database"
        db_engine = "mysql"

        expected_result = "jdbc:mysql://localhost:3306/database"
        result = get_jdbc_url(db_host, db_port, db_name, db_engine)
        self.assertEqual(result, expected_result)

    def test_unsupported_db_engine(self):
        db_host = "localhost"
        db_port = 3306
        db_name = "database"
        db_engine = "unsupported"

        with self.assertRaises(EnvironmentError):
            get_jdbc_url(db_host, db_port, db_name, db_engine)


class TestGetColumnDataTypes(unittest.TestCase):
    @mock.patch("psycopg2.connect")
    def test_postgres_column_data_types(self, mock_connect):
        mock_cursor = mock.MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            ("col1", "IntegerType"),
            ("col2", "StringType"),
            ("col3", "TimestampType"),
        ]

        engine = "postgres"
        host = "localhost"
        port = 5432
        database = "database"
        user = "user"
        password = "password"
        table_name = "table"

        expected_result = {
            "col1": "IntegerType",
            "col2": "StringType",
            "col3": "TimestampType",
        }
        result = get_column_data_types(
            engine, host, port, database, user, password, table_name
        )
        self.assertEqual(result, expected_result)

    @mock.patch("mysql.connector.connect")
    def test_mysql_column_data_types(self, mock_connect):
        mock_cursor = mock.MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            ("col1", "IntegerType"),
            ("col2", "StringType"),
            ("col3", "TimestampType"),
        ]

        engine = "mysql"
        host = "localhost"
        port = 5432
        database = "database"
        user = "user"
        password = "password"
        table_name = "table"

        expected_result = {
            "col1": "IntegerType",
            "col2": "StringType",
            "col3": "TimestampType",
        }
        result = get_column_data_types(
            engine, host, port, database, user, password, table_name
        )
        self.assertEqual(result, expected_result)


class TestCreateDbTableSchema(unittest.TestCase):
    @mock.patch("difflib.get_close_matches")
    @mock.patch("codebase.etl.extract.get_column_data_types")
    def test_postgres_schema(self, mock_get_column_data_types, mock_get_close_matches):
        mock_get_column_data_types.return_value = {
            "col1": "integer",
            "col2": "text",
            "col3": "timestamp",
        }
        mock_get_close_matches.side_effect = ["integer", "string", "timestamp"]

        db_engine = "postgres"
        db_host = "localhost"
        db_port = 5432
        db_name = "database"
        db_user = "user"
        db_password = "password"
        extract_table = "schema.table"

        expected_result = StructType(
            [
                StructField("col1", StringType(), True),
                StructField("col2", StringType(), True),
                StructField("col3", StringType(), True),
            ]
        )
        result = create_db_table_schema(
            db_engine, db_host, db_port, db_name, db_user, db_password, extract_table
        )
        self.assertEqual(result, expected_result)

    @mock.patch("difflib.get_close_matches")
    @mock.patch("codebase.etl.extract.get_column_data_types")
    def test_mysql_schema(self, mock_get_column_data_types, mock_get_close_matches):
        mock_get_column_data_types.return_value = {
            "col1": "int",
            "col2": "varchar(255)",
            "col3": "datetime",
        }
        mock_get_close_matches.side_effect = ["integer", "string", "timestamp"]

        db_engine = "mysql"
        db_host = "localhost"
        db_port = 5432
        db_name = "database"
        db_user = "user"
        db_password = "password"
        extract_table = "schema.table"

        expected_result = StructType(
            [
                StructField("col1", StringType(), True),
                StructField("col2", StringType(), True),
                StructField("col3", StringType(), True),
            ]
        )

        result = create_db_table_schema(
            db_engine, db_host, db_port, db_name, db_user, db_password, extract_table
        )
        self.assertEqual(result, expected_result)


class TestDetermineExtractPlan(unittest.TestCase):
    def test_fe_extract(self):
        provided_hwm_value = "2022-01-01"
        provided_lwm_value = "2022-01-01"
        extract_type = "FE"
        tracking_table = {}

        expected_result = ("2022-01-01", "2022-01-01")
        result = determine_extract_plan(
            provided_hwm_value, provided_lwm_value, extract_type, tracking_table
        )
        self.assertEqual(result, expected_result)

    def test_pe_extract_new_run(self):
        provided_hwm_value = "2022-01-01"
        provided_lwm_value = "2022-01-01"
        extract_type = "PE"
        tracking_table = {}

        expected_result = ("2022-01-01", "2022-01-01")
        result = determine_extract_plan(
            provided_hwm_value, provided_lwm_value, extract_type, tracking_table
        )
        self.assertEqual(result, expected_result)

    def test_pe_extract_continuation(self):
        provided_hwm_value = "2022-01-01"
        provided_lwm_value = "2022-01-01"
        extract_type = "PE"
        tracking_table = {
            "hwm_value": {"S": "2022-02-01"},
            "lwm_value": {"S": "2022-01-01"},
        }

        expected_result = ("2022-02-01", "2022-01-01")
        result = determine_extract_plan(
            provided_hwm_value, provided_lwm_value, extract_type, tracking_table
        )
        self.assertEqual(result, expected_result)


# ToDo Set up testing in a container for spark
# class TestGetNumPartitions(unittest.TestCase):
#     def setUp(self):
#         self.spark = SparkSession.builder.appName("test").getOrCreate()
#
#     def test_get_num_partitions(self):
#         # Create a sample DataFrame with 1000 rows and 2 partitions
#         schema = StructType([
#             StructField("id", LongType(), True),
#             StructField("name", StringType(), True)
#         ])
#         data = [(i, f"name{i}") for i in range(1000)]
#         df = self.spark.createDataFrame(data, schema).repartition(2)
#
#         # Test that the correct number of partitions is returned when rows_per_partition is 1000
#         self.assertEqual(get_num_partitions(df), 2)
#
#         # Test that the correct number of partitions is returned when rows_per_partition is 500
#         self.assertEqual(get_num_partitions(df, 500), 4)
#
#         # Test that the correct number of partitions is returned when rows_per_partition is 2000
#         self.assertEqual(get_num_partitions(df, 2000), 1)
#
#         # Test that the correct number of partitions is returned when the DataFrame is empty
#         self.assertEqual(get_num_partitions(self.spark.createDataFrame([], schema)), 1)
