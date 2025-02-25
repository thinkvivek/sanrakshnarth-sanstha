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



import paramiko
from datetime import datetime

# SFTP Server Details
SFTP_HOST = "your.sftp.server"
SFTP_PORT = 22  # Default SFTP port
SFTP_USERNAME = "your_username"
SFTP_PASSWORD = "your_password"  # Use key-based authentication for better security
REMOTE_PATH = "/remote/path/to/check/"
ARCHIVE_PATH = "/remote/path/to/archive/"
TARGET_FILE = "file_to_check.txt"

# Get current timestamp in MMDDYYYYHHMM format
timestamp = datetime.now().strftime("%m%d%Y%H%M")
RENAMED_FILE = f"file_to_check_{timestamp}.txt"

def connect_sftp():
    """Establishes an SFTP connection using Paramiko."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SFTP_HOST, port=SFTP_PORT, username=SFTP_USERNAME, password=SFTP_PASSWORD)
        sftp = ssh.open_sftp()
        return ssh, sftp
    except Exception as e:
        print(f"Error connecting to SFTP: {e}")
        exit(1)

def check_file_exists(sftp):
    """Checks if the target file exists in the remote directory."""
    try:
        sftp.stat(f"{REMOTE_PATH}{TARGET_FILE}")
        print(f"{TARGET_FILE} found in {REMOTE_PATH}. Proceeding with renaming...")
        return True
    except FileNotFoundError:
        print(f"Warning: {TARGET_FILE} not found in {REMOTE_PATH}. Skipping rename step.")
        return False

def rename_and_move_file(sftp):
    """Renames and moves the file. Fails if rename fails."""
    try:
        sftp.rename(f"{REMOTE_PATH}{TARGET_FILE}", f"{ARCHIVE_PATH}{RENAMED_FILE}")
        print(f"File successfully renamed and moved to: {ARCHIVE_PATH}{RENAMED_FILE}")
    except Exception as e:
        print(f"Error renaming/moving the file: {e}")
        exit(1)

# Main execution
if __name__ == "__main__":
    ssh, sftp = connect_sftp()
    
    if check_file_exists(sftp):
        rename_and_move_file(sftp)
    
    # Close connections
    sftp.close()
    ssh.close()

