import xml.etree.ElementTree as ET

def extract_sql_queries(ssis_file):
    """Parses the SSIS package XML and extracts SQL queries from Execute SQL Tasks and Data Flow components."""
    tree = ET.parse(ssis_file)
    root = tree.getroot()
    
    # SSIS XML namespaces (these are typical for SSIS packages)
    namespaces = {
        'DTS': 'www.microsoft.com/SqlServer/Dts',
        'SQLTask': 'www.microsoft.com/sqlserver/dts/tasks/sqltask',
        'DTSDesign': 'www.microsoft.com/SqlServer/Dts/Design'
    }
    
    sql_statements = []
    
    # Find Execute SQL Tasks
    for sql_task in root.findall(".//DTS:Executable[@DTS:ExecutableType='Microsoft.ExecuteSQLTask']", namespaces):
        # Get the task name for reference
        task_name = sql_task.get('DTS:ObjectName', 'Unnamed SQL Task')
        
        # Find the SQL statement (this might vary based on SSIS version)
        sql_source = sql_task.find(".//SQLTask:SqlStatementSource", namespaces)
        if sql_source is not None and sql_source.text:
            sql_statements.append(f"-- From Execute SQL Task: {task_name}")
            sql_statements.append(sql_source.text.strip())
    
    # Find Data Flow Tasks and their components
    for data_flow in root.findall(".//DTS:Executable[@DTS:ExecutableType='Microsoft.Pipeline']", namespaces):
        data_flow_name = data_flow.get('DTS:ObjectName', 'Unnamed Data Flow')
        sql_statements.append(f"\n-- Data Flow: {data_flow_name}")
        
        # Find OLE DB Sources (common sources of SQL queries)
        for component in data_flow.findall(".//DTS:Component", namespaces):
            component_name = component.get('DTS:ObjectName', 'Unnamed Component')
            component_type = component.get('DTS:ComponentClassID', '')
            
            # OLE DB Source
            if component_type.endswith('OleDbSource'):
                sql_command = component.find(".//DTS:Property[@DTS:Name='SqlCommand']/DTS:PropertyExpression", namespaces)
                if sql_command is not None and sql_command.text:
                    sql_statements.append(f"-- From OLE DB Source: {component_name}")
                    sql_statements.append(sql_command.text.strip())
            
            # Look for other important components
            elif 'Sort' in component_type:
                sql_statements.append(f"-- Sorting applied in component: {component_name}")
            elif 'DerivedColumn' in component_type:
                sql_statements.append(f"-- Derived Column transformation in: {component_name}")
            elif 'Lookup' in component_type:
                sql_statements.append(f"-- Lookup operation in: {component_name}")
    
    return sql_statements

def generate_sql_script(sql_statements):
    """Generates a SQL Server script using extracted SQL queries and transformations."""
    if not sql_statements:
        return "-- No SQL statements found in the SSIS package"
    
    sql_script = ["-- Generated SQL Script from SSIS Package", "SET NOCOUNT ON;", ""]
    
    temp_table_counter = 1
    prev_temp_table = None
    
    for statement in sql_statements:
        if statement.startswith("--"):
            sql_script.append("\n" + statement)  # Comment lines
        else:
            # Basic cleanup of the SQL statement
            clean_stmt = ' '.join(statement.split())
            
            # Handle different types of SQL statements
            if clean_stmt.upper().startswith(('SELECT ', 'WITH ')):
                if prev_temp_table:
                    # Drop previous temp table if exists
                    sql_script.append(f"IF OBJECT_ID('tempdb..{prev_temp_table}') IS NOT NULL DROP TABLE {prev_temp_table};")
                
                temp_table = f"#Temp{temp_table_counter}"
                sql_script.append(f"SELECT * INTO {temp_table} FROM ({clean_stmt}) AS DerivedTable;")
                prev_temp_table = temp_table
                temp_table_counter += 1
                
            elif clean_stmt.upper().startswith(('INSERT ', 'UPDATE ', 'DELETE ', 'MERGE ')):
                sql_script.append(clean_stmt + ";")
            else:
                # For other statements, just include them as-is
                sql_script.append(clean_stmt + ";")
    
    # Add final selection if we created temp tables
    if prev_temp_table:
        sql_script.append("\n-- Final result from the data flow")
        sql_script.append(f"SELECT * FROM {prev_temp_table};")
        sql_script.append(f"IF OBJECT_ID('tempdb..{prev_temp_table}') IS NOT NULL DROP TABLE {prev_temp_table};")
    
    return "\n".join(sql_script)

# Example usage
if __name__ == "__main__":
    ssis_file = "Package.dtsx"  # Replace with your package path
    try:
        sql_statements = extract_sql_queries(ssis_file)
        sql_script = generate_sql_script(sql_statements)
        
        # Save to file
        with open("converted_ssis_script.sql", "w") as file:
            file.write(sql_script)
        
        print("SQL script generated successfully!")
        print(f"Found {len(sql_statements)} SQL statements/components.")
    except FileNotFoundError:
        print(f"Error: SSIS package file not found at {ssis_file}")
    except ET.ParseError:
        print("Error: Failed to parse the SSIS package XML")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
