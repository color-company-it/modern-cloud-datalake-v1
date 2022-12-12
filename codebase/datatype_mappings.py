from pyspark.sql.types import *

JDBC_TO_PYSPARK_TYPES: dict = {
    "VARCHAR": StringType,
    "CHAR": StringType,
    "LONGVARCHAR": StringType,
    "NUMERIC": DecimalType,
    "DECIMAL": DecimalType,
    "BIT": BooleanType,
    "TINYINT": ByteType,
    "SMALLINT": ShortType,
    "INTEGER": IntegerType,
    "BIGINT": LongType,
    "REAL": FloatType,
    "FLOAT": DoubleType,
    "DOUBLE": DoubleType,
    "BINARY": BinaryType,
    "VARBINARY": BinaryType,
    "LONGVARBINARY": BinaryType,
    "DATE": DateType,
    "TIME": TimestampType,
    "TIMESTAMP": TimestampType,
}
