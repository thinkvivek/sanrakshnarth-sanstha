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
    
    return {
        'ReportName': report_name,
        'DataSources': report_data['DataSources'],
        'DataSets': report_data['DataSets']
    }

def process_reports_folder(repo_path):
    """Process all RDL files in repository"""
    results = []
    
    for root_dir, _, files in os.walk(os.path.join(repo_path, 'SSRS')):
        for file in files:
            if file.lower().endswith('.rdl'):
                file_path = os.path.join(root_dir, file)
                try:
                    report_data = parse_rdl(file_path)
                    
                    # Flatten data for CSV
                    for ds in report_data['DataSources']:
                        for dataset in report_data['DataSets']:
                            results.append({
                                'ReportName': report_data['ReportName'],
                                'DataSource': ds['Name'],
                                'ConnectionString': ds['ConnectionString'],
                                'DataSetName': dataset['DataSetName'],
                                'CommandType': dataset['CommandType'],
                                'CommandText': dataset['CommandText'][:500] + '...' if dataset['CommandText'] else ''  # Truncate long queries
                            })
                except ET.ParseError as e:
                    print(f"Error parsing {file_path}: {str(e)}")
    
    return pd.DataFrame(results)

# Configuration
REPO_PATH = '/path/to/your/git/repository'
OUTPUT_CSV = 'ssrs_report_metadata.csv'

# Process reports and save to CSV
df = process_reports_folder(REPO_PATH)
df.to_csv(OUTPUT_CSV, index=False)
print(f"Processed {len(df)} records. Saved to {OUTPUT_CSV}")
