import time

JDBC_URLS: dict = {
    "postgresql": "jdbc:postgresql://{host}:{port}/{database}",
    "mysql": "jdbc:mysql://{host}:{port}/{database}",
    "oracle": "jdbc:oracle:thin:{user}/{password}@{host}:{port}:{database}",
    "mssql": "jdbc:sqlserver://{host}:{port};database={database}",
}

JDBC_DRIVERS: dict = {
    "postgresql": "org.postgresql.Driver",
    "mysql": "com.mysql.cj.jdbc.Driver",
    "oracle": "oracle.jdbc.OracleDriver",
    "mssql": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
}


def get_jdbc_url(engine: str, jdbc_params: dict) -> str:
    """
    To create a map of database engines and their corresponding JDBC URLs a dictionary
    is used where the keys are the names of the database engines and the values are
    the JDBC URLs with placeholders for the connection parameters.
    :param engine: JDBC Engine Name
    :param jdbc_params: A dictionary object of the required params, example being:
                        params = {
                                    "host": "localhost",
                                    "port": 5432,
                                    "database": "mydb",
                                    "user": "myuser",
                                    "password": "mypassword",
                                }
    :return: JDBC Connection string.
    """

    if engine in JDBC_URLS:
        url = JDBC_URLS[engine]
        return url.format(jdbc_params)
    raise ValueError(f"The provided engine: {engine} is not supported. " f"{JDBC_URLS}")
