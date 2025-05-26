import pyodbc
import os
from dotenv import load_dotenv

# Load .env file if you're using one
load_dotenv()

# Azure SQL credentials (fallback to env variables)
server = 'chabot-poc.database.windows.net'
database = os.getenv("DB_DATABASE", "chatbotdbv1")
username = os.getenv("DB_USERNAME", "sqladmin")
password = os.getenv("DB_PASSWORD", "P@ssword123!")

# Connection string (must be one line!)
connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
    f"Connection Timeout=30;"
)

try:
    print("🔗 Connecting to Azure SQL Database...")
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    # Test: Query top 5 rows from any table (change if needed)
    test_query = "SELECT TOP 5 * FROM kpc_data"
    cursor.execute(test_query)
    rows = cursor.fetchall()

    print("✅ Connection successful!")
    print("📊 Sample data:")
    for row in rows:
        print(row)

    conn.close()

except Exception as e:
    print("❌ Connection failed.")
    print(str(e))
