import unittest

from codebase.etl import MIN_VALUES
from codebase.etl.extract import (
    convert_db_namespaces,
    get_sql_where_condition,
    get_pushdown_query,
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
