import pymssql
from datetime import datetime

server   = 'your_server_name_or_ip'      # e.g. 'localhost' or '10.0.0.5'
database = 'your_database'
username = 'your_username'
password = 'your_password'
port     = 1433                          # default; change if custom

try:
    conn = pymssql.connect(
        server=server,
        user=username,
        password=password,
        database=database,
        port=port,
        tds_version='7.4'   # modern default; adjust only if you hit protocol errors
    )
    print("✅ Connected with pymssql!")

    with conn.cursor() as cur:
        cur.execute("SELECT @@VERSION AS version, GETDATE() AS now")
        vers, now = cur.fetchone()
        print("SQL Server version:", vers.split('\n')[0])
        print("Server time      :", now.strftime('%Y-%m-%d %H:%M:%S'))

    conn.close()

except pymssql.Error as e:
    print("❌ Connection failed")
    print("Details:", e)
