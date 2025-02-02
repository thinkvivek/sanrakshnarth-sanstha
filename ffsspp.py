import os
import csv
import xml.etree.ElementTree as ET
import re
import subprocess

# Git repository details
GIT_USERNAME = "YOUR_GITHUB_USERNAME"
GIT_PAT = "YOUR_PERSONAL_ACCESS_TOKEN"  # Store this securely, do not hardcode in production
GIT_REPO_URL = "https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME.git"
LOCAL_REPO_PATH = "C:/path/to/your/local/repo"  # Change this to your desired local folder

# The subfolder where SSRS RDL files are stored inside the repo
SSRS_FOLDER = os.path.join(LOCAL_REPO_PATH, "ssrs")  # Change this to your actual folder inside repo

# Output CSV File
OUTPUT_CSV = "rdl_extracted_data.csv"

# SSRS XML Namespaces (2010 & 2016 schemas)
NAMESPACES = {
    'default': 'http://schemas.microsoft.com/sqlserver/reporting/2010/01/reportdefinition',
    'data_source': 'http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition'
}

# Function to clone or pull latest Git repo
def clone_or_pull_repo():
    if os.path.exists(LOCAL_REPO_PATH):
        print("Repository already exists. Pulling latest changes...")
        subprocess.run(["git", "-C", LOCAL_REPO_PATH, "pull"], check=True)
    else:
        print("Cloning the repository...")
        GIT_CLONE_URL = GIT_REPO_URL.replace("https://", f"https://{GIT_USERNAME}:{GIT_PAT}@")
        subprocess.run(["git", "clone", GIT_CLONE_URL, LOCAL_REPO_PATH], check=True)
    print("Repository is up to date.")

# Function to extract RDL details
def extract_rdl_info(rdl_file):
    try:
        with open(rdl_file, "r", encoding="utf-8") as file:
            xml_content = file.read()  # Read full XML as a string
        
        # Parse XML
        tree = ET.ElementTree(ET.fromstring(xml_content))
        root = tree.getroot()

        # Determine correct namespace
        ns = NAMESPACES['default']
        if root.tag.startswith('{http://schemas.microsoft.com/sqlserver/reporting/2016'):
            ns = NAMESPACES['data_source']

        report_data = []

        # Extract DataSets
        for dataset in root.findall(".//{"+ns+"}DataSet"):
            dataset_name = dataset.get("Name", "Unknown DataSet")

            # Extract Query inside DataSet
            query = dataset.find("{"+ns+"}Query")
            if query is not None:
                # Extract DataSource Name
                data_source_name = query.find("{"+ns+"}DataSourceName")
                data_source_name = data_source_name.text.strip() if data_source_name is not None else "Unknown DataSource"

                # Extract CommandType (StoredProcedure or Text)
                command_type = query.find("{"+ns+"}CommandType")
                command_type = command_type.text.strip() if command_type is not None else "Text"

                # Extract CommandText (Full SQL Query)
                command_text = query.find("{"+ns+"}CommandText")
                full_query = ""

                if command_text is not None:
                    # Extract full text content while preserving newlines
                    full_query = "".join(command_text.itertext()).strip()

                    # Decode XML-encoded characters
                    full_query = re.sub(r"&lt;", "<", full_query)
                    full_query = re.sub(r"&gt;", ">", full_query)
                    full_query = re.sub(r"&amp;", "&", full_query)

                    # Normalize Windows-style newlines to Unix-style for consistency
                    full_query = full_query.replace("\r\n", "\n")

                report_data.append({
                    "RDL File": os.path.basename(rdl_file),
                    "DataSource Name": data_source_name,
                    "DataSet Name": dataset_name,
                    "CommandType": command_type,
                    "CommandText": full_query  # Preserve formatting
                })

        return report_data

    except Exception as e:
        print(f"Error processing {rdl_file}: {e}")
        return []

# Function to process all RDL files
def process_rdls():
    rdl_data = []
    
    if not os.path.exists(SSRS_FOLDER):
        print(f"Error: SSRS folder '{SSRS_FOLDER}' not found in repo!")
        return

    for root, dirs, files in os.walk(SSRS_FOLDER):
        for file in files:
            if file.endswith(".rdl"):
                rdl_path = os.path.join(root, file)
                rdl_data.extend(extract_rdl_info(rdl_path))

    # Write to Pipe-Delimited CSV file
    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["RDL File", "DataSource Name", "DataSet Name", "CommandType", "CommandText"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="|", quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writeheader()
        for row in rdl_data:
            # Ensure the CommandText stays in correct format with preserved newlines
            row["CommandText"] = row["CommandText"].replace("\n", "\r\n")  # Excel-friendly newlines
            writer.writerow(row)

    print(f"Extraction completed. CSV file saved as {OUTPUT_CSV}")

# Run the process
if __name__ == "__main__":
    clone_or_pull_repo()  # Clone or update the repo first
    process_rdls()  # Extract RDL data
