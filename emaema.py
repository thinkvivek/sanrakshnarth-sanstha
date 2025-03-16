import smtplib
import pandas as pd
import cx_Oracle
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Database connection details
ORACLE_DSN = cx_Oracle.makedsn("your_host", "your_port", service_name="your_service")
ORACLE_USER = "your_username"
ORACLE_PASSWORD = "your_password"

# Email configuration
SMTP_SERVER = "smtp.yourmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "your_email@example.com"
EMAIL_PASSWORD = "your_email_password"
EMAIL_RECEIVER = "receiver@example.com"

# SQL file path
SQL_FILE_PATH = "x.sql"

def read_sql_file(file_path):
    """Read the SQL query from a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def fetch_data(query):
    """Fetch data from the Oracle database and return as a DataFrame."""
    connection = cx_Oracle.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
    cursor = connection.cursor()
    
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]  # Extract column names
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return pd.DataFrame(rows, columns=columns)

def convert_to_html(df):
    """Convert DataFrame to a well-formatted HTML table."""
    html_table = df.to_html(index=False, escape=False, border=1)
    return f"""
    <html>
    <head>
        <style>
            table {{border-collapse: collapse; width: 100%;}}
            th, td {{border: 1px solid black; padding: 8px; text-align: left;}}
            th {{background-color: #f2f2f2;}}
        </style>
    </head>
    <body>
        <h2>Report Failure Alerts</h2>
        {html_table}
    </body>
    </html>
    """

def send_email(html_content):
    """Send an email with the HTML table."""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = "Report Failure Alert"

    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    sql_query = read_sql_file(SQL_FILE_PATH)
    data = fetch_data(sql_query)
    
    if not data.empty:
        html_content = convert_to_html(data)
        send_email(html_content)
    else:
        print("No failed reports found.")
