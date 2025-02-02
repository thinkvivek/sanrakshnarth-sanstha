import os
import xml.etree.ElementTree as ET
import pandas as pd
from lxml import etree  # Better XML handling

def get_namespaces(root):
    """Extract namespaces from XML root"""
    return {k: v for k, v in root.attrib.items() if k.startswith('xmlns:')}

def parse_rdl(file_path):
    """Parse RDL with namespace awareness and full CommandText extraction"""
    result = {
        'DataSources': [],
        'DataSets': [],
        'Errors': []
    }

    try:
        # Use lxml parser for better error handling
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(file_path, parser)
        root = tree.getroot()
        namespaces = get_namespaces(root)

        # Find all data sources (including shared ones)
        for ds in root.findall('.//{http://schemas.microsoft.com/sqlserver/reporting/2010/01/reportdefinition}DataSource', namespaces=namespaces):
            try:
                ds_name = ds.get('Name')
                conn_str = ds.find('.//{http://schemas.microsoft.com/sqlserver/reporting/2010/01/reportdefinition}ConnectString', namespaces=namespaces)
                result['DataSources'].append({
                    'Name': ds_name,
                    'ConnectionString': conn_str.text if conn_str is not None else 'Shared/External'
                })
            except Exception as ds_error:
                result['Errors'].append(f"DataSourceError: {str(ds_error)}")

        # Find all datasets with full command text
        for dataset in root.findall('.//{http://schemas.microsoft.com/sqlserver/reporting/2010/01/reportdefinition}DataSet', namespaces=namespaces):
            try:
                ds_name = dataset.get('Name')
                query = dataset.find('.//{http://schemas.microsoft.com/sqlserver/reporting/2010/01/reportdefinition}Query', namespaces=namespaces)
                
                if query is not None:
                    command_type = query.find('.//{http://schemas.microsoft.com/sqlserver/reporting/2010/01/reportdefinition}CommandType', namespaces=namespaces)
                    command_text = query.find('.//{http://schemas.microsoft.com/sqlserver/reporting/2010/01/reportdefinition}CommandText', namespaces=namespaces)
                    
                    # Extract full CommandText with CDATA handling
                    cmd_text = ''
                    if command_text is not None:
                        cmd_text = ''.join(command_text.itertext()).strip()
                        
                    result['DataSets'].append({
                        'Name': ds_name,
                        'CommandType': command_type.text if command_type is not None else 'Text',
                        'CommandText': cmd_text
                    })
            except Exception as ds_error:
                result['Errors'].append(f"DataSetError: {str(ds_error)}")

    except Exception as e:
        result['Errors'].append(f"FileParseError: {str(e)}")

    return result

def process_reports(repo_path):
    """Process all RDLs with detailed logging"""
    results = []
    stats = {'processed': 0, 'errors': 0}

    for category in os.listdir(os.path.join(repo_path, 'Reports')):
        category_path = os.path.join(repo_path, 'Reports', category)
        if not os.path.isdir(category_path):
            continue

        for rdl_file in os.listdir(category_path):
            if not rdl_file.lower().endswith('.rdl'):
                continue

            file_path = os.path.join(category_path, rdl_file)
            stats['processed'] += 1
            
            try:
                report_data = parse_rdl(file_path)
                
                # Record even if partial data exists
                for ds in report_data['DataSources']:
                    for dataset in report_data['DataSets']:
                        results.append({
                            'Category': category,
                            'Report': rdl_file,
                            'DataSource': ds['Name'],
                            'Connection': ds['ConnectionString'],
                            'DataSet': dataset['Name'],
                            'CommandType': dataset['CommandType'],
                            'Query': dataset['CommandText']
                        })
                
                if report_data['Errors']:
                    stats['errors'] += 1
                    print(f"Partial parse: {rdl_file}")
                    for error in report_data['Errors']:
                        print(f"  - {error}")

            except Exception as e:
                stats['errors'] += 1
                print(f"Failed: {rdl_file} - {str(e)}")

    print(f"\nProcessing Complete: {stats['processed']} files, {stats['errors']} errors")
    return pd.DataFrame(results)

# Configuration
REPO_PATH = '/path/to/repo'
OUTPUT_CSV = 'ssrs_analysis.csv'

# Execute
df = process_reports(REPO_PATH)
df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
