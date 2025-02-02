import cx_Oracle
import pandas as pd

# Oracle DB Connection Details
ORACLE_USER = "your_username"
ORACLE_PASSWORD = "your_password"
ORACLE_DSN = "your_db_host:port/service_name"

# RDL Extracted Data CSV File
RDL_CSV_PATH = "rdl_extracted_data.csv"

# Output Merged File
OUTPUT_CSV_PATH = "merged_output.csv"


def query_oracle():
    """Fetch x, y, z columns from Oracle table1"""
    connection = cx_Oracle.connect(ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN)
    query = "SELECT rdl_name, x, y, z FROM table1"  # Ensure rdl_name is the join key
    df = pd.read_sql(query, connection)
    connection.close()
    return df


def merge_datasets(oracle_df):
    """Merge Oracle data with RDL Extracted Data and write to CSV"""
    # Load RDL extracted data
    rdl_df = pd.read_csv(RDL_CSV_PATH, delimiter="|")  # Pipe-delimited input

    # Ensure the column used for joining exists in both dataframes
    merged_df = pd.merge(rdl_df, oracle_df, on="rdl_name", how="inner")

    # Write the final merged dataset to a new CSV file (pipe-delimited)
    merged_df.to_csv(OUTPUT_CSV_PATH, sep="|", index=False)
    print(f"✅ Merged data saved to {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    oracle_data = query_oracle()
    merge_datasets(oracle_data)
