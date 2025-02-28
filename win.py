import paramiko

# Windows Server details
server = "ServerA"  # Replace with Windows Server IP or hostname
username = "your_user"  # Windows SSH user
key_path = "/path/to/your/private/key/id_rsa"  # Private key location

# Path of the .exe file on Windows
exe_path = r"C:\Path\To\Your\program.exe"

# Create SSH client
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect using SSH key
    client.connect(server, username=username, key_filename=key_path)
    
    # Execute .exe remotely
    command = f'"{exe_path}"'
    stdin, stdout, stderr = client.exec_command(command)
    
    print("Output:\n", stdout.read().decode())
    print("Errors:\n", stderr.read().decode())

finally:
    client.close()
