def get_namespaces(ssis_file):
    """Extracts XML namespaces from the SSIS package."""
    namespaces = {}
    for event, elem in ET.iterparse(ssis_file, events=['start-ns']):
        prefix, uri = elem
        namespaces[prefix] = uri
    print("Extracted Namespaces:", namespaces)  # Debugging step
    return namespaces


for sql_task in root.findall(".//{*}Executable", namespaces):  
    if sql_task.get("DTS:ExecutableType") == "Microsoft.ExecuteSQLTask":  # Check attribute
        for sql_property in sql_task.findall(".//{*}SqlStatementSource", namespaces):
            if sql_property.text:
                sql_statements.append(sql_property.text.strip())

