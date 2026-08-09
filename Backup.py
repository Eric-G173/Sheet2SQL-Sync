import json
import os
import sys
from datetime import datetime

import mysql.connector
from dotenv import load_dotenv

from Database_Load import load_table
import config

load_dotenv()


def backup_table(df=None):
    """
    Snapshots the current state of the table to a local JSON file
    before any writes, so a bad sync can be rolled back with restore_table().
    """
    os.makedirs(config.BACKUP_DIR, exist_ok=True)

    if df is None:
        df = load_table()

    records = df.to_dict(orient="records")
    for row in records:
        for key, value in row.items():
            if hasattr(value, "isoformat"):
                row[key] = value.isoformat()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(config.BACKUP_DIR, f"{config.TABLE_NAME}_backup_{timestamp}.json")

    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)

    print(f"Backup saved to {backup_path}")
    return backup_path


def restore_table(backup_path):
    """Restores the table from a backup file, replacing all current rows."""
    with open(backup_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    conn = mysql.connector.connect(
        host=os.getenv("HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("PORT")
    )
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {config.TABLE_NAME}")

    columns_sql = ", ".join(config.ALL_COLUMNS)
    placeholders = ", ".join(["%s"] * len(config.ALL_COLUMNS))
    insert_sql = f"INSERT INTO {config.TABLE_NAME} ({columns_sql}) VALUES ({placeholders})"

    for row in records:
        values = tuple(row.get(col) for col in config.ALL_COLUMNS)
        cur.execute(insert_sql, values)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Restored {len(records)} row(s) from {backup_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python Backup.py <path_to_backup_file>")
    else:
        restore_table(sys.argv[1])