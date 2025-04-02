import pandas as pd
import cx_Oracle
import pymssql
import configparser
import os

# Load database configuration
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "../config/db_config.config"))

class DBExecutor:
    def __init__(self, db_type="oracle"):
        self.db_type = db_type
        self.connection = self._create_connection()

    def _create_connection(self):
        """Creates a database connection based on db_config.config."""
        db_config = config[self.db_type]

        if self.db_type == "oracle":
            dsn = cx_Oracle.makedsn(db_config["host"], db_config.getint("port"), service_name=db_config["service_name"])
            conn = cx_Oracle.connect(user=db_config["user"], password=db_config["password"], dsn=dsn)

        elif self.db_type == "sqlserver":
            conn = pymssql.connect(
                server=db_config["host"],
                port=db_config.getint("port"),
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"]
            )

        return conn

    def execute_query(self, query=None, file_path=None):
        """Executes an SQL query or reads a query from a file and returns a DataFrame."""
        if file_path:
            with open(file_path, "r") as file:
                query = file.read()

        if not query:
            raise ValueError("No SQL query provided!")

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

        df = pd.DataFrame(rows, columns=columns)
        return df

    def close_connection(self):
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
