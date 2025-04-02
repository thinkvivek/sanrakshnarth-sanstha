import xml.etree.ElementTree as ET

def extract_sql_queries(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Define namespaces
    namespaces = {'DTS': 'www.microsoft.com/SqlServer/Dts', 'SQLTask': 'www.microsoft.com/SqlServer/Dts/Tasks'}
    
    sql_queries = []
    merge_joins = []
    sorts = []
    derived_columns = []
    
    # Extract SQL queries
    for sql_task in root.findall(".//DTS:Executable/DTS:ObjectData/SQLTask:SQLTaskData", namespaces):
        query = sql_task.get("SQLTask:SqlStatementSource")
        if query:
            sql_queries.append(query)
    
    # Extract components like Merge Joins, Sorts, Derived Columns
    for component in root.findall(".//component"):
        for prop in component.findall("./properties/property"):
            if prop.get("description") == "The SQL command to be executed." and prop.text:
                sql_queries.append(prop.text)
        
        # Identify Merge Joins
        if 'MergeJoin' in component.get("name", ""):
            merge_joins.append(component)
        
        # Identify Sorts
        if 'Sort' in component.get("name", ""):
            sorts.append(component)
        
        # Identify Derived Columns
        if 'DerivedColumn' in component.get("name", ""):
            derived_columns.append(component)
    
    return sql_queries, merge_joins, sorts, derived_columns


def generate_sql_script(sql_queries, merge_joins, sorts, derived_columns):
    sql_script = """-- Generated SQL Server Script\n\n"""
    
    temp_table_count = 1
    temp_tables = []
    
    # Convert extracted SQL queries into temporary tables
    for query in sql_queries:
        temp_table = f"#TempTable{temp_table_count}"
        temp_tables.append(temp_table)
        sql_script += f"SELECT * INTO {temp_table} FROM ({query}) AS SourceQuery;\n\n"
        temp_table_count += 1
    
    # Handle Merge Joins
    for merge in merge_joins:
        left_table = temp_tables.pop(0)
        right_table = temp_tables.pop(0)
        join_type = 'LEFT JOIN' if 'Left' in merge.get('name', '') else 'RIGHT JOIN'
        result_table = f"#TempTable{temp_table_count}"
        sql_script += f"SELECT * INTO {result_table} FROM {left_table} {join_type} {right_table} ON ...;\n\n"
        temp_tables.append(result_table)
        temp_table_count += 1
    
    # Handle Sorts
    for sort in sorts:
        input_table = temp_tables.pop(0)
        result_table = f"#TempTable{temp_table_count}"
        sql_script += f"SELECT * INTO {result_table} FROM {input_table} ORDER BY ...;\n\n"
        temp_tables.append(result_table)
        temp_table_count += 1
    
    # Handle Derived Columns
    for derived in derived_columns:
        input_table = temp_tables.pop(0)
        result_table = f"#TempTable{temp_table_count}"
        sql_script += f"SELECT *, -- Derived column expressions\nINTO {result_table}\nFROM {input_table};\n\n"
        temp_tables.append(result_table)
        temp_table_count += 1
    
    # Final Output
    sql_script += f"SELECT * FROM {temp_tables[-1]};\n"
    
    return sql_script


def main(xml_file):
    sql_queries, merge_joins, sorts, derived_columns = extract_sql_queries(xml_file)
    sql_script = generate_sql_script(sql_queries, merge_joins, sorts, derived_columns)
    
    with open("output.sql", "w") as f:
        f.write(sql_script)
    
    print("SQL script generated and saved as output.sql")


if __name__ == "__main__":
    xml_file = "ssis_package.dtsx"  # Replace with your actual file path
    main(xml_file)
