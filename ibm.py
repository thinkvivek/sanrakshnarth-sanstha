import ibm_db

# DB2 Connection Details
db_host = "your_db_host"  # e.g., "db2.example.com"
db_port = "50001"         # SSL port
db_name = "your_db_name"
db_user = "your_username"
db_password = "your_password"

# Path to SSL Certificate KDB file
ssl_kdb_path = "/path/to/certificate.kdb"

# Connection String with SSL
conn_str = f"DATABASE={db_name}; HOSTNAME={db_host}; PORT={db_port}; PROTOCOL=TCPIP; UID={db_user}; PWD={db_password}; Security=SSL; SSLServerCertificate={ssl_kdb_path};"

# Establish Connection
try:
    conn = ibm_db.connect(conn_str, "", "")
    print("Connected to DB2 successfully!")

    # Read Query from x.sql
    with open("x.sql", "r") as sql_file:
        sql_query = sql_file.read()

    # Execute Query
    stmt = ibm_db.exec_immediate(conn, sql_query)
    
    # Fetch and Print Results
    result = ibm_db.fetch_assoc(stmt)
    while result:
        print(result)  # Print each row
        result = ibm_db.fetch_assoc(stmt)

    # Close Connection
    ibm_db.close(conn)
    print("Connection closed.")

except Exception as e:
    print(f"Error connecting to DB2: {str(e)}")
