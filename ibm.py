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

