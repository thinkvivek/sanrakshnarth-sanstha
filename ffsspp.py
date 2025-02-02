import git
import os
import xml.etree.ElementTree as ET
import csv

# GitHub Repository Details
GIT_USERNAME = "your_username"
GIT_PAT = "your_personal_access_token"
GIT_REPO_URL = "https://github.com/your_org_or_user/your_repo.git"
LOCAL_CLONE_PATH = "cloned_repo"

# Clone the Git repository (if it doesn't exist)
if not os.path.exists(LOCAL_CLONE_PATH):
    repo_url = f"https://{GIT_USERNAME}:{GIT_PAT}@github.com/your_org_or_user/your_repo.git"
    print("Cloning repository...")
    git.Repo.clone_from(repo_url, LOCAL_CLONE_PATH)
else:
    print("Repository already cloned. Pulling latest changes...")
    repo = git.Repo(LOCAL_CLONE_PATH)
    repo.remotes.origin.pull()

# Path where SSRS reports (.rdl) are stored inside the cloned repo
SSRS_FOLDER = os.path.join(LOCAL_CLONE_PATH, "SSRS")

# Function to extract required details from .rdl files
def extract_rdl_details(rdl_path):
    try:
        tree = ET.parse(rdl_path)
        root = tree.getroot()
        namespace = {"rdl": "http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition"}

        rdl_filename = os.path.basename(rdl_path)
        data_sources = [ds.find("rdl:DataSourceName", namespace).text for ds in root.findall(".//rdl:DataSource", namespace)]
        data_sets = root.findall(".//rdl:DataSet", namespace)

        extracted_data = []
        for dataset in data_sets:
            dataset_name = dataset.find("rdl:Name", namespace).text if dataset.find("rdl:Name", namespace) else "Unknown"
            command_type = dataset.find(".//rdl:CommandType", namespace)
            command_text = dataset.find(".//rdl:CommandText", namespace)

            extracted_data.append({
                "RDL Filename": rdl_filename,
                "DataSource Name": ", ".join(data_sources),
                "DataSet Name": dataset_name,
                "CommandType": command_type.text.strip() if command_type is not None else "Unknown",
                "CommandText": command_text.text.strip() if command_text is not None else "Unknown"
            })

        return extracted_data
    except Exception as e:
        print(f"Error parsing {rdl_path}: {e}")
        return []

# Collect all .rdl files
rdl_files = []
for root_dir, _, files in os.walk(SSRS_FOLDER):
    for file in files:
        if file.endswith(".rdl"):
            rdl_files.append(os.path.join(root_dir, file))

# Extract data from all .rdl files
all_data = []
for rdl_file in rdl_files:
    all_data.extend(extract_rdl_details(rdl_file))

# Write to pipe (`|`) delimited CSV
csv_filename = "rdl_report.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["RDL Filename", "DataSource Name", "DataSet Name", "CommandType", "CommandText"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="|", quotechar='"', quoting=csv.QUOTE_MINIMAL)

    writer.writeheader()
    for row in all_data:
        writer.writerow(row)

print(f"✅ Extraction completed. Data saved in {csv_filename}")
