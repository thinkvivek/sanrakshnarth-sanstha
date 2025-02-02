import os
import pandas as pd
from lxml import etree

NAMESPACE_MAP = {
    "2010": "http://schemas.microsoft.com/sqlserver/reporting/2010/01/reportdefinition",
    "2016": "http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition"
}

def detect_rdl_version(root):
    """Identify RDL version from root element"""
    for ns in NAMESPACE_MAP.values():
        if ns in root.tag:
            return ns
    raise ValueError("Unsupported RDL namespace")

def parse_rdl(file_path):
    """Parse both RDL versions with namespace awareness"""
    result = {
        'DataSources': [],
        'DataSets': [],
        'Errors': []
    }

    try:
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(file_path, parser)
        root = tree.getroot()
        namespace = detect_rdl_version(root)
        nsmap = {'ns': namespace}

        # Extract DataSources (both embedded and shared)
        for ds in root.findall('.//ns:DataSources/ns:DataSource', namespaces=nsmap):
            try:
                ds_name = ds.get('Name')
                conn_str = ds.find('.//ns:ConnectString', namespaces=nsmap)
                result['DataSources'].append({
                    'Name': ds_name,
                    'Connection': conn_str.text if conn_str is not None else 'Shared'
                })
            except Exception as e:
                result['Errors'].append(f"DataSourceError: {str(e)}")

        # Extract Datasets with full CommandText
        for ds in root.findall('.//ns:DataSets/ns:DataSet', namespaces=nsmap):
            try:
                ds_name = ds.get('Name')
                query = ds.find('.//ns:Query', namespaces=nsmap)
                command_type = query.find('.//ns:CommandType', namespaces=nsmap) if query is not None else None
                command_text = query.find('.//ns:CommandText', namespaces=nsmap) if query is not None else None

                result['DataSets'].append({
                    'Name': ds_name,
                    'CommandType': command_type.text if command_type is not None else 'Text',
                    'CommandText': ''.join(command_text.itertext()).strip() if command_text is not None else ''
                })
            except Exception as e:
                result['Errors'].append(f"DataSetError: {str(e)}")

    except Exception as e:
        result['Errors'].append(f"FileError: {str(e)}")

    return result

def process_reports(repo_path):
    """Process all reports with version-aware parsing"""
    results = []
    
    for category in os.listdir(os.path.join(repo_path, 'Reports')):
        category_path = os.path.join(repo_path, 'Reports', category)
        if not os.path.isdir(category_path):
            continue

        for rdl_file in os.listdir(category_path):
            if not rdl_file.lower().endswith('.rdl'):
                continue

            file_path = os.path.join(category_path, rdl_file)
            report_data = parse_rdl(file_path)

            # Collect results even if partial data exists
            for ds in report_data['DataSources']:
                for dataset in report_data['DataSets']:
                    results.append({
                        'Category': category,
                        'Report': rdl_file,
                        'DataSource': ds['Name'],
                        'Connection': ds['Connection'],
                        'DataSet': dataset['Name'],
                        'CommandType': dataset['CommandType'],
                        'Query': dataset['CommandText']
                    })

            # Log errors
            if report_data['Errors']:
                print(f"Errors in {rdl_file}:")
                for error in report_data['Errors']:
                    print(f"  - {error}")

    return pd.DataFrame(results)

# Configuration
REPO_PATH = '/path/to/your/repo'
OUTPUT_CSV = 'ssrs_report_analysis.csv'

# Execute and save
df = process_reports(REPO_PATH)
df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
print(f"Processed {len(df)} records from {len(df['Report'].unique())} reports")
