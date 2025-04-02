import xml.etree.ElementTree as ET
from datetime import datetime

def generate_sql_from_ssis(xml_path):
    # Parse XML with namespace handling
    namespaces = {
        'DTS': 'www.microsoft.com/SqlServer/Dts',
        'SQLTask': 'www.microsoft.com/sqlserver/dts/tasks/sqltask',
        'dataflow': 'www.microsoft.com/sqlserver/dts/dataflow'
    }
    
    tree = ET.parse(xml_path)
    root = tree.getroot()

    components = {
        'sql_queries': [],
        'merge_joins': [],
        'sorts': [],
        'derived_columns': [],
        'outputs': []
    }

    # Extract SQL queries from ExecuteSQL tasks and OLE DB sources
    for task in root.findall('.//DTS:Executable[@DTS:ExecutableType="Microsoft.ExecuteSQLTask"]', namespaces):
        sql = task.find('.//SQLTask:SqlStatement', namespaces)
        if sql is not None:
            components['sql_queries'].append(sql.text)

    # Data Flow components
    dataflow = root.find('.//DTS:Executable[@DTS:ExecutableType="Microsoft.Pipeline"]', namespaces)
    if dataflow is not None:
        # Find merge joins
        for merge in dataflow.findall('.//dataflow:MergeJoin', namespaces):
            join_info = {
                'left_input': merge.get('LeftInputPath'),
                'right_input': merge.get('RightInputPath'),
                'join_type': merge.get('JoinType'),
                'keys': [col.get('Name') for col in merge.findall('.//dataflow:JoinKey', namespaces)]
            }
            components['merge_joins'].append(join_info)

        # Find sort components
        for sort in dataflow.findall('.//dataflow:Sort', namespaces):
            sort_info = {
                'columns': [col.get('Name') for col in sort.findall('.//dataflow:SortColumn', namespaces)],
                'order': [col.get('Descending') for col in sort.findall('.//dataflow:SortColumn', namespaces)]
            }
            components['sorts'].append(sort_info)

    # Generate SQL script
    sql_script = f'''-- Generated from SSIS package on {datetime.now().strftime('%Y-%m-%d')}
SET NOCOUNT ON;

{generate_temp_tables(components)}
{generate_merge_joins(components)}
'''

    return sql_script

def generate_temp_tables(components):
    tables = []
    for i, query in enumerate(components['sql_queries'], 1):
        tables.append(f'''
-- Source query {i}
SELECT *
INTO #tempSource{i}
FROM ({query}) src
''')
    return '\n'.join(tables)

def generate_merge_joins(components):
    joins = []
    for i, merge in enumerate(components['merge_joins'], 1):
        joins.append(f'''
-- Merge Join {i} ({merge['join_type']})
SELECT *
INTO #mergeResult{i}
FROM #tempSource{merge['left_input']} L
{merge['join_type'].upper()} JOIN #tempSource{merge['right_input']} R
    ON {' AND '.join([f'L.{k} = R.{k}' for k in merge['keys']])}
''')
    return '\n'.join(joins)

# Usage
xml_path = 'YourPackage.dtsx'  # Replace with actual path
try:
    print(generate_sql_from_ssis(xml_path))
except FileNotFoundError:
    print("Error: SSIS package file not found")
except Exception as e:
    print(f"Error processing package: {str(e)}")
