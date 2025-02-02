import cx_Oracle
import pandas as pd

# Oracle DB Connection Details
ORACLE_USER = "your_username"
ORACLE_PASSWORD = "your_password"
ORACLE_DSN = "your_db_host:port/service_name"

# File Paths
RDL_CSV_PATH = "rdl_extracted_data.csv"
OUTPUT_CSV_PATH = "merged_output.csv"


def query_oracle():
    """Fetch x, y, z columns from Oracle table1"""
    connection = cx_Oracle.connect(ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN)
    query = "SELECT rdl_name, x, y, z FROM table1"  # Ensure rdl_name is the join key
    df = pd.read_sql(query, connection)
    connection.close()

    # Normalize rdl_name (Remove everything before the last "/")
    df["rdl_name"] = df["rdl_name"].str.replace(r".*/", "", regex=True)
    return df


def merge_datasets(oracle_df):
    """Merge Oracle data with RDL Extracted Data and write to CSV"""
    # Load RDL extracted data
    rdl_df = pd.read_csv(RDL_CSV_PATH, delimiter="|")  # Pipe-delimited input

    # Normalize RDL extracted data (Remove ".rdl" extension)
    rdl_df["rdl_name"] = rdl_df["rdl_name"].str.replace(r"\.rdl$", "", regex=True)

    # Perform join after normalizing rdl_name
    merged_df = pd.merge(oracle_df, rdl_df, on="rdl_name", how="inner")

    # Reorder columns: Move Oracle table columns first
    table_columns = ["x", "y", "z"]  # Columns from Oracle
    other_columns = [col for col in merged_df.columns if col not in table_columns]
    merged_df = merged_df[table_columns + other_columns]  # Reorder

    # Write to CSV (pipe-delimited, preserving newlines in SQL queries)
    merged_df.to_csv(OUTPUT_CSV_PATH, sep="|", index=False, quoting=3)  # quoting=3 ensures multi-line SQL queries are preserved

    print(f"✅ Merged data saved to {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    oracle_data = query_oracle()
    merge_datasets(oracle_data)
