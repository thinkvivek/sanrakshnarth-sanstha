import cx_Oracle
import configparser
import sys
from pathlib import Path

def read_config(config_file):
    """Read all parameters from the config file."""
    config = configparser.ConfigParser()
    config.read(config_file)
    
    try:
        # Database connection details
        username = config['ORACLE']['username']
        password = config['ORACLE']['password']
        dsn = config['ORACLE']['dsn']
        
        # File paths
        sql_path = config['PATHS']['sql_path']
        txt_path = config['PATHS']['txt_path']
        
        return username, password, dsn, sql_path, txt_path
    except KeyError as e:
        print(f"Error: Missing key {e} in {config_file}")
        sys.exit(1)

def connect_and_execute(sql_file_name, is_txt=False):
    """Connect to Oracle DB and execute the SQL script."""
    # Read all parameters from config
    config_file = "ora.config"
    username, password, dsn, sql_path, txt_path = read_config(config_file)
    
    # Construct full SQL file path
    sql_file_path = Path(sql_path) / sql_file_name
    if not sql_file_path.exists():
        print(f"Error: SQL file '{sql_file_path}' not found.")
        sys.exit(1)
    
    try:
        # Establish connection
        connection = cx_Oracle.connect(
            user=username,
            password=password,
            dsn=dsn
        )
        print("Connected to Oracle database successfully.")
        
        # Read SQL script
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
        
        # Create a cursor
        cursor = connection.cursor()
        
        # Execute SQL script
        cursor.execute(sql_script)
        
        # Check if it's a query (SELECT) or a DML/DDL statement
        if sql_script.strip().upper().startswith("SELECT"):
            # Fetch results
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            if is_txt:
                # Save to text file with ~ delimiter
                txt_file_path = Path(txt_path) / f"{sql_file_name.split('.')[0]}_output.txt"
                txt_file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
                
                with open(txt_file_path, 'w') as f:
                    # Write header
                    f.write('~'.join(columns) + '\n')
                    # Write rows
                    for row in rows:
                        # Convert each value to string, handle None
                        row_str = '~'.join(str(val) if val is not None else '' for val in row)
                        f.write(row_str + '\n')
                print(f"Output saved to {txt_file_path}")
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
            print(f"SQL script '{sql_file_path}' executed successfully (no output).")
        
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
        print("Usage: python run_oracle_sql_full_config.py <sql_file_name> [is_txt]")
        print("  <sql_file_name>: Name of the SQL file (e.g., query.sql)")
        print("  [is_txt]: 'txt' to save output to text file with ~ delimiter, omit to check True/False")
        sys.exit(1)
    
    sql_file_name = sys.argv[1]
    is_txt = len(sys.argv) == 3 and sys.argv[2].lower() == "txt"
    
    # Execute the script
    connect_and_execute(sql_file_name, is_txt)
