from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives.serialization import Encoding
import sys

# Define input and output file names
pfx_file = "certificate.pfx"  # Input .pfx file
crt_file = "certificate.crt"  # Output .crt file
pfx_password = b"your_password_here"  # Replace with your .pfx password

# Read the .pfx file
with open(pfx_file, "rb") as f:
    pfx_data = f.read()

# Load the .pfx contents
private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(pfx_data, pfx_password)

# Write the extracted certificate to a .crt file
if certificate:
    with open(crt_file, "wb") as f:
        f.write(certificate.public_bytes(Encoding.PEM))
    print(f"Successfully extracted: {crt_file}")
else:
    print("No certificate found in the PFX file.", file=sys.stderr)




import ibm_db

dsn = (
    "DATABASE=YOUR_DB;"
    "HOSTNAME=your.db2.server;"
    "PORT=50001;"
    "PROTOCOL=TCPIP;"
    "UID=your_user;"
    "PWD=your_password;"
    "SECURITY=SSL;"
    "SSLCLIENTKEYSTOREDB=/path/to/your_keystore.kdb;"
    "SSLCLIENTKEYSTASH=/path/to/your_keystore.sth;"
)

try:
    conn = ibm_db.connect(dsn, "", "")
    print("Connected successfully!")
except Exception as e:
    print(f"Connection failed: {e}")



import ibm_db

# Database connection details
DATABASE = "YOUR_DATABASE"
HOSTNAME = "YOUR_HOSTNAME"
PORT = "50001"  # Default SSL port, change if necessary
USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"
SSL_KDB_FILE = "/path/to/your/certificate.kdb"

# Connection string using SSL
conn_str = (
    f"DATABASE={DATABASE};"
    f"HOSTNAME={HOSTNAME};"
    f"PORT={PORT};"
    f"PROTOCOL=TCPIP;"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    f"SECURITY=SSL;"
    f"SSLServerCertificate={SSL_KDB_FILE};"
)

try:
    # Establish connection
    conn = ibm_db.connect(conn_str, "", "")
    
    if conn:
        print("Connected to DB2 successfully!")
    
        # Run a test query
        sql = "SELECT CURRENT TIMESTAMP FROM SYSIBM.SYSDUMMY1"
        stmt = ibm_db.exec_immediate(conn, sql)
        result = ibm_db.fetch_assoc(stmt)
        print("Current Timestamp:", result)

        # Close connection
        ibm_db.close(conn)
    else:
        print("Connection failed.")

except Exception as e:
    print(f"Error: {e}")

