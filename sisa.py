import xml.etree.ElementTree as ET

def get_namespaces(ssis_file):
    """Extracts XML namespaces from the SSIS package."""
    namespaces = {}
    for event, elem in ET.iterparse(ssis_file, events=['start-ns']):
        prefix, uri = elem
        namespaces[prefix] = uri
    return namespaces

def extract_sql_queries(ssis_file):
    """Parses SSIS XML and extracts SQL queries from Execute SQL Tasks and Data Flow components."""
    tree = ET.parse(ssis_file)
    root = tree.getroot()
    
    namespaces = get_namespaces(ssis_file)  # Dynamically get namespaces
    
    sql_statements = []
    
    # Find Execute SQL Tasks (Extract queries)
    for sql_task in root.findall(".//{*}Executable[@DTS:ExecutableType='Microsoft.ExecuteSQLTask']", namespaces):
        for sql_property in sql_task.findall(".//{*}ObjectData//{*}SqlStatementSource", namespaces):
            if sql_property.text:
                sql_statements.append(sql_property.text.strip())
    
    # Find Data Flow Task Components (Merge Joins, Sorts, Derived Columns)
    for component in root.findall(".//{*}Component", namespaces):
        component_name = component.get("refId", "Unknown Component")
        
        if "Merge Join" in component_name:
            sql_statements.append(f"-- Merge Join found in {component_name}")
        elif "Sort" in component_name:
            sql_statements.append(f"-- Sorting applied in {component_name}")
        elif "Derived Column" in component_name:
            sql_statements.append(f"-- Derived Column transformation in {component_name}")

    return sql_statements

def generate_sql_script(sql_statements):
    """Generates a SQL Server script from extracted SQL queries and transformations."""
    sql_script = ["-- Generated SQL Script from SSIS Data Flow"]
    
    temp_table_counter = 1
    prev_temp_table = None
    
    for statement in sql_statements:
        if statement.startswith("--"):  
            sql_script.append(statement)  # Keep comments
        else:
            temp_table = f"#temp{temp_table_counter}"
            if prev_temp_table:
                sql_script.append(f"SELECT * INTO {temp_table} FROM ({statement}) AS derived_table;")
            else:
                sql_script.append(statement.replace(" INTO ", f" INTO {temp_table} "))  # Modify INTO statements
        
            prev_temp_table = temp_table
            temp_table_counter += 1
    
    sql_script.append("-- Final Output Selection")
    if prev_temp_table:
        sql_script.append(f"SELECT * FROM {prev_temp_table};")

    return "\n".join(sql_script)

# Usage
ssis_file = "path/to/your/package.dtsx"  # Replace with actual path
sql_statements = extract_sql_queries(ssis_file)
sql_script = generate_sql_script(sql_statements)

# Save to file
with open("converted_ssis_script.sql", "w") as file:
    file.write(sql_script)

print("SQL script generated successfully!")
