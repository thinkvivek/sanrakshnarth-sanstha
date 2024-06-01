import cx_Oracle

def connect_to_db(username, password, dsn):
    """
    Connect to the Oracle database.
    """
    connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
    return connection

def fetch_table_structure(cursor, table_name):
    """
    Fetch the structure of the table.
    """
    query = f"""
    SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH
    FROM ALL_TAB_COLUMNS
    WHERE TABLE_NAME = '{table_name.upper()}'
    """
    cursor.execute(query)
    columns = cursor.fetchall()
    return columns

def fetch_constraints(cursor, table_name):
    """
    Fetch the constraints of the table.
    """
    query = f"""
    SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE, SEARCH_CONDITION, R_CONSTRAINT_NAME
    FROM ALL_CONSTRAINTS
    WHERE TABLE_NAME = '{table_name.upper()}'
    """
    cursor.execute(query)
    constraints = cursor.fetchall()
    return constraints

def fetch_indexes(cursor, table_name):
    """
    Fetch the indexes of the table.
    """
    query = f"""
    SELECT INDEX_NAME, COLUMN_NAME
    FROM ALL_IND_COLUMNS
    WHERE TABLE_NAME = '{table_name.upper()}'
    """
    cursor.execute(query)
    indexes = cursor.fetchall()
    return indexes

def create_temp_table(cursor, original_table, temp_table, columns):
    """
    Create a new table with the "_Temp" suffix.
    """
    create_query = f"CREATE TABLE {temp_table} ("
    column_defs = []
    for column in columns:
        column_def = f"{column[0]} {column[1]}"
        if column[1].upper() == 'VARCHAR2':
            column_def += f"({column[2]})"
        column_defs.append(column_def)
    create_query += ", ".join(column_defs) + ")"
    cursor.execute(create_query)

def create_constraints(cursor, temp_table, constraints):
    """
    Create constraints on the new table.
    """
    for constraint in constraints:
        if constraint[1] == 'P':  # Primary key
            query = f"ALTER TABLE {temp_table} ADD CONSTRAINT {constraint[0]} PRIMARY KEY ({constraint[2]})"
        elif constraint[1] == 'R':  # Foreign key
            query = f"ALTER TABLE {temp_table} ADD CONSTRAINT {constraint[0]} FOREIGN KEY ({constraint[2]}) REFERENCES {constraint[3]}"
        elif constraint[1] == 'U':  # Unique key
            query = f"ALTER TABLE {temp_table} ADD CONSTRAINT {constraint[0]} UNIQUE ({constraint[2]})"
        elif constraint[1] == 'C':  # Check constraint
            query = f"ALTER TABLE {temp_table} ADD CONSTRAINT {constraint[0]} CHECK ({constraint[2]})"
        cursor.execute(query)

def create_indexes(cursor, temp_table, indexes):
    """
    Create indexes on the new table.
    """
    for index in indexes:
        query = f"CREATE INDEX {index[0]} ON {temp_table} ({index[1]})"
        cursor.execute(query)

def copy_data(original_cursor, temp_cursor, original_table, temp_table):
    """
    Copy data from the original table to the new table.
    """
    select_query = f"SELECT * FROM {original_table}"
    original_cursor.execute(select_query)
    rows = original_cursor.fetchall()
    if rows:
        columns = [desc[0] for desc in original_cursor.description]
        insert_query = f"INSERT INTO {temp_table} ({', '.join(columns)}) VALUES ({', '.join([':' + str(i + 1) for i in range(len(columns))])})"
        temp_cursor.executemany(insert_query, rows)

def main():
    # Connection details for the source database (PPP)
    ppp_username = 'your_ppp_username'
    ppp_password = 'your_ppp_password'
    ppp_dsn = 'your_ppp_dsn'

    # Connection details for the target database (VBD)
    vbd_username = 'your_vbd_username'
    vbd_password = 'your_vbd_password'
    vbd_dsn = 'your_vbd_dsn'

    original_table = 'XYZ'
    temp_table = original_table + '_Temp'

    # Connect to the source database
    ppp_conn = connect_to_db(ppp_username, ppp_password, ppp_dsn)
    ppp_cursor = ppp_conn.cursor()

    # Connect to the target database
    vbd_conn = connect_to_db(vbd_username, vbd_password, vbd_dsn)
    vbd_cursor = vbd_conn.cursor()

    try:
        # Fetch the structure of the original table
        columns = fetch_table_structure(ppp_cursor, original_table)
        # Fetch constraints and indexes of the original table
        constraints = fetch_constraints(ppp_cursor, original_table)
        indexes = fetch_indexes(ppp_cursor, original_table)

        # Create the new table with the "_Temp" suffix in the target database
        create_temp_table(vbd_cursor, original_table, temp_table, columns)
        # Create constraints on the new table
        create_constraints(vbd_cursor, temp_table, constraints)
        # Create indexes on the new table
        create_indexes(vbd_cursor, temp_table, indexes)

        # Copy data from the original table to the new table
        copy_data(ppp_cursor, vbd_cursor, original_table, temp_table)

        # Commit the changes in the target database
        vbd_conn.commit()

        print(f"Table {temp_table} created and data copied successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        vbd_conn.rollback()
    finally:
        # Close the cursors and connections
        ppp_cursor.close()
        ppp_conn.close()
        vbd_cursor.close()
        vbd_conn.close()

if __name__ == "__main__":
    main()
