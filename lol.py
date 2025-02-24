import subprocess
from datetime import datetime

# SFTP Server Details
SFTP_HOST = "your.sftp.server"
SFTP_USERNAME = "your_username"
REMOTE_PATH = "/remote/path/to/check/"  # Directory where the file is located
ARCHIVE_PATH = "/remote/path/to/archive/"  # Directory where renamed files will be moved
TARGET_FILE = "file_to_check.txt"  # File you are searching for

# Get current date and time in MMDDYYYYHHMM format
timestamp = datetime.now().strftime("%m%d%Y%H%M")

# Construct the new filename
RENAMED_FILE = f"file_to_check_{timestamp}.txt"

# Define the SFTP batch commands
sftp_commands = f"""
cd {REMOTE_PATH}
ls {TARGET_FILE}
rename {TARGET_FILE} {RENAMED_FILE}
mv {RENAMED_FILE} {ARCHIVE_PATH}
exit
"""

# Run the SFTP command using subprocess
try:
    result = subprocess.run(
        ["sftp", "-b", "-", f"{SFTP_USERNAME}@{SFTP_HOST}"],  # -b takes batch commands from stdin
        input=sftp_commands,
        text=True,
        capture_output=True,
        check=True
    )
    print(f"File renamed to: {RENAMED_FILE}")
    print("SFTP Operation Successful:\n", result.stdout)
except subprocess.CalledProcessError as e:
    print("Error during SFTP operation:\n", e.stderr)
