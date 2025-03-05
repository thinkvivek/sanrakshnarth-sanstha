import cx_Oracle
import configparser
import sys
import pandas as pd
from pathlib import Path

def read_config(config_file):
    """Read Oracle connection details from a config file."""
    config = configparser.ConfigParser()
    config.read(config_file)
    
    try:
        username = config['ORACLE']['username']
        password = config['ORACLE']['password']
        dsn = config['ORACLE']['dsn']
        return username, password, dsn
    except KeyError as e:
        print(f"Error: Missing key {e} in {config_file}")
        sys.exit(1)

def connect_and_execute(sql_file, output_to_csv=False):
    """Connect to Oracle DB and execute the SQL script using cx_Oracle."""
    # Read config
    config_file = "ora.config"
    username, password, dsn = read_config(config_file)
    
    try:
        # Establish connection
        connection = cx_Oracle.connect(
            user=username,
            password=password,
            dsn=dsn
        )
        print("Connected to Oracle database successfully.")
        
        # Create a cursor
        cursor = connection.cursor()
        
        # Read SQL script
        sql_file_path = Path(sql_file)
        if not sql_file_path.exists():
            raise FileNotFoundError(f"SQL file '{sql_file}' not found.")
        
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
        
        # Execute SQL script
        cursor.execute(sql_script)
        
        # Check if it's a query (SELECT) or a DML/DDL statement
        if sql_script.strip().upper().startswith("SELECT"):
            # Fetch results
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            if output_to_csv:
                # Save to CSV using pandas
                df = pd.DataFrame(rows, columns=columns)
                csv_file = sql_file_path.stem + "_output.csv"
                df.to_csv(csv_file, index=False)
                print(f"Output saved to {csv_file}")
            else:
                # Check if result is True (assuming a single row with a boolean-like value)
                if rows and len(rows) == 1 and len(rows[0]) == 1:
                    result = rows[0][0]
                    is_true = str(result).upper() in ("TRUE", "1", "Y", "YES")
                    print(f"Result is {'True' if is_true else 'False'}")
                else:
                    print("Result: ", rows)
        else:
            # For non-SELECT statements, commit the transaction
            connection.commit()
            print(f"SQL script '{sql_file}' executed successfully (no output).")
        
    except cx_Oracle.Error as error:
        print(f"Error connecting to Oracle or executing SQL: {error}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    # Check command-line arguments
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python run_oracle_sql_cx.py <sql_file> [output_to_csv]")
        print("  <sql_file>: Path to the SQL file to execute")
        print("  [output_to_csv]: 'csv' to save output to CSV, omit to check True/False")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    output_to_csv = len(sys.argv) == 3 and sys.argv[2].lower() == "csv"
    
    # Execute the script
    connect_and_execute(sql_file, output_to_csv)
