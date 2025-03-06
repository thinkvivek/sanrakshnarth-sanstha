import cx_Oracle
import configparser
import sys
from pathlib import Path

def read_config(config_file):
    """Reads database credentials and file paths from the config file."""
    config = configparser.ConfigParser()
    config.read(config_file)

    try:
        return {
            "username": config["ORACLE"]["username"],
            "password": config["ORACLE"]["password"],
            "dsn": config["ORACLE"]["dsn"],
            "sql_path": Path(config["PATHS"]["sql_path"]),
            "txt_path": Path(config["PATHS"]["txt_path"])
        }
    except KeyError as e:
        sys.exit(f"Error: Missing key {e} in {config_file}")

def execute_sql(sql_file_name, output_file_name=None):
    """Connects to Oracle DB, executes the SQL script, and handles output."""
    config_file = "ora.config"
    config = read_config(config_file)

    # Validate SQL file existence
    sql_file_path = config["sql_path"] / sql_file_name
    if not sql_file_path.exists():
        sys.exit(f"Error: SQL file '{sql_file_path}' not found.")

    try:
        with cx_Oracle.connect(user=config["username"], password=config["password"], dsn=config["dsn"]) as connection:
            print("Connected to Oracle database successfully.")

            with open(sql_file_path, 'r') as file:
                sql_script = file.read().strip()

            with connection.cursor() as cursor:
                cursor.execute(sql_script)

                # If it's a SELECT query, process results
                if sql_script.upper().startswith("SELECT"):
                    rows = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]

                    if output_file_name:
                        save_results_to_file(config["txt_path"], output_file_name, columns, rows)
                    else:
                        display_boolean_result(rows)
                else:
                    connection.commit()
                    print(f"SQL script '{sql_file_path}' executed successfully (no output).")

    except cx_Oracle.DatabaseError as error:
        sys.exit(f"Database error: {error}")
    except Exception as e:
        sys.exit(f"Unexpected error: {e}")

def save_results_to_file(txt_path, output_file_name, columns, rows):
    """Saves query results to a text file with '~' delimiter."""
    txt_file_path = txt_path / output_file_name
    txt_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(txt_file_path, 'w') as f:
        f.write("~".join(columns) + "\n")
        for row in rows:
            f.write("~".join(str(val) if val is not None else "" for val in row) + "\n")

    print(f"Output saved to {txt_file_path}")

def display_boolean_result(rows):
    """Determines and displays a boolean result if applicable."""
    if rows and len(rows) == 1 and len(rows[0]) == 1:
        is_true = str(rows[0][0]).strip().upper() in {"TRUE", "1", "Y", "YES"}
        print(f"Result is {'True' if is_true else 'False'}")
    else:
        print("Query result:", rows)

if __name__ == "__main__":
    if len(sys.argv) not in {2, 3}:
        sys.exit("Usage: python run_oracle_sql.py <sql_file_name> [output_file.txt]")

    sql_file_name = sys.argv[1]
    output_file_name = sys.argv[2] if len(sys.argv) == 3 else None

    if output_file_name and not output_file_name.endswith(".txt"):
        sys.exit("Error: Output file name must end with '.txt'")

    execute_sql(sql_file_name, output_file_name)
