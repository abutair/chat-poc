# load_file.py

import os
import sqlite3

def load_filetype(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == '.db':
        return load_sqlite_db(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

def load_sqlite_db(file_path):
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    # Load a preview (first 3 rows) for each table
    sheets = {}
    for table_name in tables:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        preview = [dict(zip(columns, row)) for row in rows]
        sheets[table_name] = preview

    conn.close()
    return sheets
