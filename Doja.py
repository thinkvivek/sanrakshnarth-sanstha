import cx_Oracle
import configparser
import sys
import time
from pathlib import Path

def read_config(config_file):
    """Read database credentials and SQL file path from the config file."""
    config = configparser.ConfigParser()
    config.read(config_file)

    try:
        return {
            "username": config["ORACLE"]["username"],
            "password": config["ORACLE"]["password"],
            "dsn": config["ORACLE"]["dsn"],
            "sql_file_path": config["PATHS"]["sql_file_path"]
        }
    except KeyError as e:
        print(f"Error: Missing key {e} in {config_file}")
        sys.exit(1)

def execute_sql(sql_file):
    """Executes the SQL query and checks if the result is True or False."""
    config = read_config("settings.config")
    
    sql_file_path = Path(config["sql_file_path"]) / sql_file
    if not sql_file_path.exists():
        print(f"Error: SQL file '{sql_file_path}' not found.")
        sys.exit(1)

    try:
        with cx_Oracle.connect(
            user=config["username"],
            password=config["password"],
            dsn=config["dsn"]
        ) as connection:
            with connection.cursor() as cursor:
                with open(sql_file_path, "r") as file:
                    sql_script = file.read()

                cursor.execute(sql_script)
                rows = cursor.fetchall()

                if rows and len(rows) == 1 and len(rows[0]) == 1:
                    result = rows[0][0]
                    return str(result).upper() in ("TRUE", "1", "Y", "YES")

                return False  # Default to False if unexpected result format

    except cx_Oracle.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)

def retry_logic(sql_file):
    """Runs the SQL every 5 minutes for an hour if the condition is False."""
    timeout = 60 * 60  # 1 hour
    interval = 5 * 60  # 5 minutes
    elapsed_time = 0

    while elapsed_time < timeout:
        if execute_sql(sql_file):
            print("Condition met, exiting successfully.")
            sys.exit(0)

        print(f"Condition not met, retrying in 5 minutes... ({elapsed_time // 60} minutes elapsed)")
        time.sleep(interval)
        elapsed_time += interval

    print("Condition not met even after 1 hour. Failing script.")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python execute_sql_loop.py <sql_file>")
        sys.exit(1)

    sql_file = sys.argv[1]
  
