"""
Export SQLite data to JSON for migration to PostgreSQL.
"""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "transparency.db"
OUTPUT_PATH = Path(__file__).parent / "export.json"


def export_data():
    """Export all tables to JSON."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    data = {}
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        columns = [description[0] for description in cursor.description]
        rows = [dict(row) for row in cursor.fetchall()]
        data[table] = rows
    
    conn.close()
    
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"Exported {len(data)} tables to {OUTPUT_PATH}")
    for table, rows in data.items():
        print(f"  {table}: {len(rows)} rows")


if __name__ == "__main__":
    export_data()
