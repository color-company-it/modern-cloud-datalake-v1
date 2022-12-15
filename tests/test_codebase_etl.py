import unittest

from codebase.etl import (
    get_jdbc_url,
    calculate_worker_nodes,
    convert_memory_to_gb,
    calculate_partitions_and_worker_nodes,
)
from codebase.etl.extract import (
    generate_sql_where_condition,
    generate_sql_pushdown_query,
    parse_extract_table,
)


class TestJdbcUtils(unittest.TestCase):
    def test_get_jdbc_url(self):
        # Set up test data
        engine = "postgres"
        jdbc_params = {
            "host": "localhost",
            "port": 5432,
            "database": "mydb",
            "user": "myuser",
            "password": "mypassword",
        }
        expected_url = "jdbc:postgresql://localhost:5432/mydb"

        # Call the get_jdbc_url method
        url = get_jdbc_url(engine, jdbc_params)

        # Assert that the returned value is the expected URL
        self.assertEqual(url, expected_url)

    def test_get_jdbc_url_invalid(self):
        # Set up test data
        engine = "postgres"
        jdbc_params = {
            "host": "localhost",
            "port": 5432,
            "database": "mydb",
            "user": "myuser",
            "password": "mypassword",
        }
        expected_url = "jdbc:postgresql://bad:5432/mydb"

        # Call the get_jdbc_url method
        url = get_jdbc_url(engine, jdbc_params)

        # Assert that the returned value is the expected URL
        self.assertNotEqual(url, expected_url)


class TestRepartitionDataframe(unittest.TestCase):
    # ToDo: set this up in a SparkDocker environment
    # def setUp(self):
    #     # create a SparkSession
    #     self.spark = SparkSession.builder.appName('test').getOrCreate()
    #
    #     # create a DataFrame with 10 rows and 2 columns
    #     self.data = [(i, i * 2) for i in range(10)]
    #     self.data_frame = self.spark.createDataFrame(self.data, ['col1', 'col2'])
    #
    # def test_repartition_dataframe(self):
    #     # set the default parallelism to 5
    #     self.spark.sparkContext.defaultParallelism = 5
    #
    #     # call the repartition_dataframe function
    #     repartitioned_df, num_partitions = repartition_dataframe(self.spark, self.data_frame)
    #
    #     # assert that the number of partitions is 2
    #     self.assertEqual(num_partitions, 2)
    #
    #     # assert that the data in the repartitioned DataFrame is the same as the original
    #     self.assertEqual(repartitioned_df.collect(), self.data_frame.collect())
    #
    # def tearDown(self):
    #     # stop the SparkSession
    #     self.spark.stop()
    pass


class TestCalculateWorkerNodes(unittest.TestCase):
    def test_calculate_worker_nodes(self):
        # test with the default values
        self.assertEqual(calculate_worker_nodes(100000, 2), 3)

        # test with custom values
        self.assertEqual(calculate_worker_nodes(6000000, 10, 100000), 8)

        # test with even more custom values
        self.assertEqual(calculate_worker_nodes(10000000, 5, 200000), 12)

    def test_calculate_worker_nodes_with_rounding(self):
        # test with a number that needs to be rounded up
        self.assertEqual(calculate_worker_nodes(200000, 5, 100000), 3)

        # test with another number that needs to be rounded up
        self.assertEqual(calculate_worker_nodes(250000, 6, 100000), 3)


class TestConvertMemoryToGb(unittest.TestCase):
    def test_convert_memory_to_gb(self):
        # test converting KB to GB
        self.assertEqual(convert_memory_to_gb(1024, "KB"), 0.0009765625)

        # test converting MB to GB
        self.assertEqual(convert_memory_to_gb(1024, "MB"), 1)

        # test converting GB to GB
        self.assertEqual(convert_memory_to_gb(1, "GB"), 1)

        # test converting TB to GB
        self.assertEqual(convert_memory_to_gb(1, "TB"), 1024)

    def test_convert_memory_to_gb_with_invalid_unit(self):
        # test with an invalid unit
        with self.assertRaises(ValueError):
            convert_memory_to_gb(1, "PB")


class TestCalculatePartitionsAndWorkerNodes(unittest.TestCase):
    def test_calculate_partitions_and_worker_nodes(self):
        # Test with the minimum possible values for the input arguments
        row_count = 1
        db_cpu = 1
        db_memory = 1
        target_rows_per_worker_node = 1
        target_rows_per_cpu = 1
        target_rows_per_gb_memory = 1
        expected_output = (1, 1)
        self.assertEqual(
            calculate_partitions_and_worker_nodes(
                row_count,
                db_cpu,
                db_memory,
                target_rows_per_worker_node,
                target_rows_per_cpu,
                target_rows_per_gb_memory,
            ),
            expected_output,
        )

        # Test with larger input values
        row_count = 100000
        db_cpu = 10
        db_memory = 5
        target_rows_per_worker_node = 10
        target_rows_per_cpu = 10
        target_rows_per_gb_memory = 10
        expected_output = (1000, 200)
        self.assertEqual(
            calculate_partitions_and_worker_nodes(
                row_count,
                db_cpu,
                db_memory,
                target_rows_per_worker_node,
                target_rows_per_cpu,
                target_rows_per_gb_memory,
            ),
            expected_output,
        )

        # Test with even larger input values
        row_count = 1000000
        db_cpu = 100
        db_memory = 50
        target_rows_per_worker_node = 100
        target_rows_per_cpu = 100
        target_rows_per_gb_memory = 100
        expected_output = (100, 2)
        self.assertEqual(
            calculate_partitions_and_worker_nodes(
                row_count,
                db_cpu,
                db_memory,
                target_rows_per_worker_node,
                target_rows_per_cpu,
                target_rows_per_gb_memory,
            ),
            expected_output,
        )


class TestExtract(unittest.TestCase):
    def test_fe_extract(self):
        result: object = generate_sql_where_condition(
            "hwm_col", "lwm_value", "hwm_value", "FE"
        )
        self.assertEqual(result, "")

    def test_pe_extract(self):
        result = generate_sql_where_condition("hwm_col", "lwm_value", "hwm_value", "PE")
        self.assertEqual(result, "WHERE hwm_col > lwm_value and hwm_col <= hwm_value")

    def test_invalid_extract(self):
        with self.assertRaises(ValueError):
            generate_sql_where_condition(
                "hwm_col", "lwm_value", "hwm_value", "invalid_type"
            )

    def test_query_generation(self):
        sql_where_condition = "WHERE hwm_col > lwm_value and hwm_col <= hwm_value"
        result = generate_sql_pushdown_query(
            "db_name.db_schema.db_table", sql_where_condition
        )
        self.assertEqual(
            result,
            "(SELECT * FROM db_name.db_schema.db_table WHERE hwm_col > lwm_value and hwm_col <= hwm_value) db_table_alias",
        )

    def test_parse_extract_table_full_namespace(self):
        result = parse_extract_table("db_name.db_schema.db_table")
        self.assertDictEqual(
            result,
            {"db_name": "db_name", "db_schema": "db_schema", "db_table": "db_table"},
        )

    def test_parse_extract_table_partial_namespace(self):
        result = parse_extract_table("db_name.db_table")
        print(result)
        self.assertDictEqual(
            result, {"db_name": "db_name", "db_schema": None, "db_table": "db_table"}
        )

    def test_parse_extract_table_no_namespace(self):
        result = parse_extract_table("db_table")
        self.assertDictEqual(
            result, {"db_name": None, "db_schema": None, "db_table": "db_table"}
        )

    def test_parse_extract_table_invalid_namespace(self):
        with self.assertRaises(ValueError):
            parse_extract_table("db_name.db_schema.db_table.invalid")
