import subprocess

def download_file_from_sftp(hostname, username, password, remote_filepath, local_filepath):
    # Create a temporary script file for sftp commands
    with open('sftp_batch.txt', 'w') as batch_file:
        batch_file.write(f'get {remote_filepath} {local_filepath}\n')
        batch_file.write('bye\n')
    
    # Use subprocess to call the sftp command with the batch file
    result = subprocess.run(
        ['sftp', '-oBatchMode=no', '-b', 'sftp_batch.txt', f'{username}@{hostname}'],
        input=f'{password}\n',
        encoding='ascii',
        capture_output=True
    )
    
    # Clean up the temporary batch file
    subprocess.run(['rm', 'sftp_batch.txt'])

    if result.returncode == 0:
        print(f'Successfully downloaded {remote_filepath} to {local_filepath}')
    else:
        print(f'Failed to download {remote_filepath}')
        print(result.stderr)

# Example usage
hostname = 'sftp.example.com'
username = 'your_username'
password = 'your_password'
remote_filepath = '/path/to/remote/file.txt'
local_filepath = '/path/to/local/file.txt'

download_file_from_sftp(hostname, username, password, remote_filepath, local_filepath)
