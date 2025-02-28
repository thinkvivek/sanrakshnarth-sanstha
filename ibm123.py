import ibm_db

# Database connection details
db2_host = "your_db2_host"
db2_port = "your_db2_port"
db2_database = "your_db2_database"
db2_user = "your_db2_username"
db2_password = "your_db2_password"

# Path to the SQL file containing your query
sql_file_path = "x.sql"
# Path to the file where you want to save the results
output_file_path = "query_results.txt"

# Read the SQL query from the .sql file
with open(sql_file_path, "r") as sql_file:
    sql_query = sql_file.read()

# Try to establish a connection to the DB2 database
try:
    # Create the connection string
    conn_str = f"DATABASE={db2_database};HOSTNAME={db2_host};PORT={db2_port};PROTOCOL=TCPIP;UID={db2_user};PWD={db2_password}"
    
    # Connect to the database
    conn = ibm_db.connect(conn_str, "", "")
    print("Connection successful!")

    # Execute the query
    stmt = ibm_db.prepare(conn, sql_query)
    ibm_db.execute(stmt)

    # Fetch and write the results to the output file
    with open(output_file_path, "w") as output_file:
        result_row = ibm_db.fetch_assoc(stmt)
        while result_row:
            # Write each row in the result to the output file
            output_file.write(str(result_row) + "\n")
            result_row = ibm_db.fetch_assoc(stmt)

    print(f"Query results have been written to {output_file_path}")

except Exception as e:
    print(f"Error occurred: {e}")

finally:
    # Close the DB2 connection
    if conn:
        ibm_db.close(conn)
        print("Connection closed.")
