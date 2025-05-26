import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

@st.cache_data(ttl=300)  
def load_azure_database():
    """Load preview data from Azure SQL Database with data type information"""
    try:
        server = os.getenv("DB_SERVER")
        database = os.getenv("DB_DATABASE") 
        username = os.getenv("DB_USERNAME")
        password = os.getenv("DB_PASSWORD")
        
        if not all([server, database, username, password]):
            st.error("❌ Database connection details are missing. Please check your environment variables.")
            st.info("Required: DB_SERVER, DB_DATABASE, DB_USERNAME, DB_PASSWORD")
            return {}
        
        connection_string = f"""
        DRIVER={{ODBC Driver 17 for SQL Server}};
        SERVER={server};
        DATABASE={database};
        UID={username};
        PWD={password};
        Encrypt=yes;
        TrustServerCertificate=no;
        Connection Timeout=30;
        """
        
        with st.spinner("🔗 Connecting to Azure SQL Database..."):
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                AND TABLE_SCHEMA = 'dbo'
                ORDER BY TABLE_NAME
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            if not tables:
                st.warning("⚠️ No tables found in the database.")
                return {}

            sheets = {}
            for table_name in tables:
                try:
                    cursor.execute("""
                        SELECT 
                            COLUMN_NAME,
                            DATA_TYPE,
                            IS_NULLABLE,
                            CHARACTER_MAXIMUM_LENGTH
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = ? 
                        AND TABLE_SCHEMA = 'dbo'
                        ORDER BY ORDINAL_POSITION
                    """, table_name)
                    
                    column_info = cursor.fetchall()
                    
                    query = f"SELECT TOP 3 * FROM [{table_name}]"
                    df = pd.read_sql(query, conn)
                    
                    preview = df.to_dict('records')
                    
                    column_types = {}
                    for col_name, data_type, is_nullable, max_length in column_info:
                        column_types[col_name] = {
                            'data_type': data_type,
                            'is_nullable': is_nullable,
                            'max_length': max_length
                        }
                    
                    enhanced_preview = []
                    for row in preview:
                        enhanced_row = {}
                        for col_name, value in row.items():
                            col_type = column_types.get(col_name, {}).get('data_type', 'unknown')
                            # Add type hint to the preview
                            enhanced_row[f"{col_name} ({col_type})"] = value
                        enhanced_preview.append(enhanced_row)
                    
                    sheets[table_name] = enhanced_preview
                    
                except Exception as e:
                    print(f"Error loading table {table_name}: {e}")
                    sheets[table_name] = []

            conn.close()
            
            # Show success message
            table_count = len([t for t in tables if sheets.get(t)])
            st.success(f"✅ Connected to Azure SQL Database! Found {table_count} tables.")
            
            return sheets
            
    except pyodbc.Error as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        st.info("Please check your database credentials and ensure the server is accessible.")
        return {}
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return {}

def get_azure_connection():
    """Get Azure SQL Database connection"""
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_DATABASE")
    username = os.getenv("DB_USERNAME") 
    password = os.getenv("DB_PASSWORD")
    
    connection_string = f"""
    DRIVER={{ODBC Driver 17 for SQL Server}};
    SERVER={server};
    DATABASE={database};
    UID={username};
    PWD={password};
    Encrypt=yes;
    TrustServerCertificate=no;
    Connection Timeout=30;
    """
    
    return pyodbc.connect(connection_string)

def get_table_schema(table_name):
    """Get detailed schema information for a specific table"""
    try:
        conn = get_azure_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION,
                NUMERIC_SCALE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ? 
            AND TABLE_SCHEMA = 'dbo'
            ORDER BY ORDINAL_POSITION
        """, table_name)
        
        schema = cursor.fetchall()
        conn.close()
        
        return schema
        
    except Exception as e:
        print(f"Error getting schema for {table_name}: {e}")
        return []