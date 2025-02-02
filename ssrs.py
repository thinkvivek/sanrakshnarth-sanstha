import os
import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict

# Namespace map for SSRS RDL XML
NAMESPACES = {
    'rd': 'http://schemas.microsoft.com/SQLServer/reporting/reportdesigner',
    'df': 'http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition',
    'd': 'http://schemas.microsoft.com/sqlserver/reporting/2010/01/reportdefinition'
}

def parse_rdl(file_path):
    """Parse RDL file and extract metadata"""
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    report_data = defaultdict(list)
    report_name = os.path.basename(file_path)
    
    # Extract Data Sources
    for ds in root.findall('.//d:DataSources/d:DataSource', NAMESPACES):
        ds_name = ds.get('Name')
        conn_str = ds.find('.//d:ConnectString', NAMESPACES).text
        report_data['DataSources'].append({
            'Name': ds_name,
            'ConnectionString': conn_str
        })
    
    # Extract DataSets and Commands
    for dataset in root.findall('.//d:DataSets/d:DataSet', NAMESPACES):
        ds_name = dataset.get('Name')
        command = dataset.find('.//d:Query/d:CommandText', NAMESPACES)
        command_type = dataset.find('.//d:Query/d:CommandType', NAMESPACES)
        
        cmd_text = command.text if command is not None else ''
        cmd_type = command_type.text if command_type is not None else 'Text'
        
        report_data['DataSets'].append({
            'DataSetName': ds_name,
            'CommandType': cmd_type,
            'CommandText': cmd_text.strip() if cmd_text else ''
        })
    
    return report_data

def process_reports_folder(repo_path):
    """Process RDL files in Reports/[subfolders] structure"""
    results = []
    reports_root = os.path.join(repo_path, 'Reports')
    
    if not os.path.exists(reports_root):
        raise ValueError(f"Reports directory not found at {reports_root}")
    
    # Process each subfolder under Reports
    for category in os.listdir(reports_root):
        category_path = os.path.join(reports_root, category)
        
        if not os.path.isdir(category_path):
            continue
            
        # Process all RDL files in this category folder
        for rdl_file in os.listdir(category_path):
            if not rdl_file.lower().endswith('.rdl'):
                continue
                
            file_path = os.path.join(category_path, rdl_file)
            try:
                report_data = parse_rdl(file_path)
                
                # Flatten data for CSV with category
                for ds in report_data.get('DataSources', []):
                    for dataset in report_data.get('DataSets', []):
                        results.append({
                            'Category': category,
                            'ReportName': rdl_file,
                            'DataSource': ds['Name'],
                            'ConnectionString': ds['ConnectionString'],
                            'DataSetName': dataset['DataSetName'],
                            'CommandType': dataset['CommandType'],
                            'CommandText': dataset['CommandText'][:500] + '...' if dataset['CommandText'] else ''
                        })
            except ET.ParseError as e:
                print(f"Error parsing {file_path}: {str(e)}")
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
    
    return pd.DataFrame(results)

# Configuration
REPO_PATH = '/path/to/your/git/repository'
OUTPUT_CSV = 'ssrs_report_metadata.csv'

# Process reports and save to CSV
df = process_reports_folder(REPO_PATH)
df.to_csv(OUTPUT_CSV, index=False)
print(f"Processed {len(df)} records from {len(df['Category'].unique())} categories. Saved to {OUTPUT_CSV}")
