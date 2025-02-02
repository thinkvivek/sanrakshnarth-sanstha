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
    root = tree.getroot()import os
import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict

# Enhanced namespace handling
NAMESPACES = {
    'rd': 'http://schemas.microsoft.com/SQLServer/reporting/reportdesigner',
    'd': 'http://schemas.microsoft.com/sqlserver/reporting/2010/01/reportdefinition',
    'df': 'http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition'
}

def safe_find(element, path, namespace_key='d'):
    """Safely find XML elements with fallback namespaces"""
    try:
        return element.find(path, NAMESPACES)
    except KeyError:
        # Try alternative namespace if primary fails
        return element.find(path.replace(namespace_key, 'df'))

def parse_rdl(file_path):
    """Parse RDL file with enhanced error handling"""
    report_data = defaultdict(list)
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Handle different namespace versions
        namespaces = {'d': NAMESPACES['d']}
        if 'Report' in root.tag:
            for prefix, uri in root.attrib.items():
                if prefix.startswith('xmlns:'):
                    namespaces[prefix[6:]] = uri

        # Extract Data Sources with null checks
        for ds in root.findall('.//d:DataSources/d:DataSource', namespaces):
            ds_name = ds.get('Name')
            conn_element = safe_find(ds, './/d:ConnectString')
            
            report_data['DataSources'].append({
                'Name': ds_name,
                'ConnectionString': conn_element.text if conn_element is not None else 'Shared Data Source'
            })

        # Extract DataSets with comprehensive checks
        for dataset in root.findall('.//d:DataSets/d:DataSet', namespaces):
            ds_name = dataset.get('Name')
            query = safe_find(dataset, './/d:Query')
            
            if query is not None:
                command = safe_find(query, './/d:CommandText')
                command_type = safe_find(query, './/d:CommandType')
            else:
                command = None
                command_type = None

            report_data['DataSets'].append({
                'DataSetName': ds_name,
                'CommandType': command_type.text if command_type is not None else 'Text',
                'CommandText': command.text.strip() if command is not None and command.text else ''
            })

    except ET.ParseError as e:
        print(f"XML Parse Error in {file_path}: {str(e)}")
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
    
    return report_data

def process_reports_folder(repo_path):
    """Process RDL files with debug logging"""
    results = []
    reports_root = os.path.join(repo_path, 'Reports')
    
    for category in os.listdir(reports_root):
        category_path = os.path.join(reports_root, category)
        if not os.path.isdir(category_path):
            continue

        print(f"Processing category: {category}")
        
        for rdl_file in os.listdir(category_path):
            if not rdl_file.lower().endswith('.rdl'):
                continue
                
            file_path = os.path.join(category_path, rdl_file)
            print(f"  Parsing: {rdl_file}")
            
            report_data = parse_rdl(file_path)
            
            # Skip files with parsing errors
            if not report_data:
                continue
                
            for ds in report_data.get('DataSources', []):
                for dataset in report_data.get('DataSets', []):
                    results.append({
                        'Category': category,
                        'ReportName': rdl_file,
                        'DataSource': ds.get('Name', 'Unknown'),
                        'ConnectionString': ds.get('ConnectionString', 'Not Specified'),
                        'DataSetName': dataset.get('DataSetName', 'Unknown'),
                        'CommandType': dataset.get('CommandType', 'Text'),
                        'CommandText': (dataset.get('CommandText', '')[:500] + '...') 
                                      if dataset.get('CommandText') else ''
                    })

    return pd.DataFrame(results)

# Configuration
REPO_PATH = '/path/to/your/git/repository'
OUTPUT_CSV = 'ssrs_report_metadata.csv'

# Execute
df = process_reports_folder(REPO_PATH)
df.to_csv(OUTPUT_CSV, index=False)
print(f"Successfully processed {len(df)} records")
    
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
