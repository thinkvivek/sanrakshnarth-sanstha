import xml.etree.ElementTree as ET

def extract_sql_queries(ssis_file):
    """Parses the SSIS package XML and extracts SQL queries from Data Flow Tasks."""
    tree = ET.parse(ssis_file)
    root = tree.getroot()
    
    namespaces = {'dts': 'www.microsoft.com/SqlServer/Dts'}
    sql_statements = []
    
    # Find Execute SQL Tasks
    for sql_task in root.findall(".//dts:Executable[@DTS:ExecutableType='Microsoft.ExecuteSQLTask']", namespaces):
        for sql_property in sql_task.findall(".//DTS:ObjectData//SQLTask:SqlStatementSource", namespaces):
            sql_statements.append(sql_property.text.strip())
    
    # Find Data Flow Task Components
    for component in root.findall(".//dts:Component", namespaces):
        component_name = component.get("refId")
        
        # Check for Merge Joins, Sorts, Derived Columns
        if "Merge Join" in component_name:
            sql_statements.append(f"-- Merge Join found in {component_name}")
        elif "Sort" in component_name:
            sql_statements.append(f"-- Sorting applied in {component_name}")
        elif "Derived Column" in component_name:
            sql_statements.append(f"-- Derived Column transformation in {component_name}")

    return sql_statements

def generate_sql_script(sql_statements):
    """Generates a SQL Server script using extracted SQL queries and transformations."""
    sql_script = []
    
    sql_script.append("-- Generated SQL Script from SSIS Data Flow")
    
    temp_table_counter = 1
    prev_temp_table = None
    
    for i, statement in enumerate(sql_statements):
        if statement.startswith("--"):
            sql_script.append(statement)  # Comment lines
        else:
            temp_table = f"#temp{temp_table_counter}"
            if prev_temp_table:
                sql_script.append(f"SELECT * INTO {temp_table} FROM ({statement}) AS derived_table;")
            else:
                sql_script.append(statement.replace(" INTO ", f" INTO {temp_table} "))  # Modify INSERT INTO
        
            prev_temp_table = temp_table
            temp_table_counter += 1
    
    sql_script.append("-- Final Output Selection")
    sql_script.append(f"SELECT * FROM {prev_temp_table};")

    return "\n".join(sql_script)

# Usage
ssis_file = "path/to/your/package.dtsx"
sql_statements = extract_sql_queries(ssis_file)
sql_script = generate_sql_script(sql_statements)

# Save to file
with open("converted_ssis_script.sql", "w") as file:
    file.write(sql_script)

print("SQL script generated successfully!")
