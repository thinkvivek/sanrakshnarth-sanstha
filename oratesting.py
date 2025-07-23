import cx_Oracle

# === CONFIGURATION ===
username = 'your_username'
password = 'your_password'
dsn = 'your_host:your_port/your_service_name'  # e.g., 'localhost:1521/XEPDB1'
sql_file_path = 'query.sql'
output_file_path = 'results.txt'

def read_sql_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def run_query_and_save_results():
    try:
        # Read SQL from file
        sql_query = read_sql_file(sql_file_path)

        # Connect to Oracle DB
        connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(sql_query)

        # Fetch all rows
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        # Write results to a text file
        with open(output_file_path, 'w') as f:
            # Write header
            f.write('\t'.join(columns) + '\n')
            f.write('-' * 80 + '\n')
            # Write rows
            for row in rows:
                f.write('\t'.join(str(col) for col in row) + '\n')

        print(f"Query results written to {output_file_path}")

    except Exception as e:
        print("Error:", e)

    finally:
        # Cleanup
        try:
            cursor.close()
            connection.close()
        except:
            pass

if __name__ == '__main__':
    run_query_and_save_results()
