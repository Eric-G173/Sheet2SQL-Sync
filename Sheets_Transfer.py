import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import os
from Database_Load import load_table, get_sheet
import warnings
warnings.filterwarnings("ignore", message=".*only supports SQLAlchemy.*")
load_dotenv()
USERNAME = os.getenv("DB_USER")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DATABASE_NAME = os.getenv("DB_NAME")
PASSWORD = os.getenv("DB_PASSWORD")

    
def apply_sheet_to_db(updates, changes, deletes):
    conn = mysql.connector.connect(
        host=os.getenv("HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("PORT")
    )
    cur = conn.cursor()
  

    # INSERT new rows
    for _, row in updates.iterrows():
        cur.execute("""
            INSERT INTO task (id, task_name, full_name, updated_at)
            VALUES (%s, %s, %s, %s)
        """, (
            row["id"],
            row["task_name"],
            row["full_name"],
            normalize_timestamp(row["updated_at"])
        ))

    # UPDATE changed rows
    for _, row in changes.iterrows():
        cur.execute("""
            UPDATE task
            SET task_name = %s,
                full_name = %s,
                updated_at = %s
            WHERE id = %s
        """, (
            row["task_name_sheet"],
            row["full_name_sheet"],
            normalize_timestamp(row["updated_at_sheet"]),
            row["id"]
        ))

    # DELETE removed rows
    for _, row in deletes.iterrows():
        cur.execute("DELETE FROM task WHERE id = %s", (row["id"],))

    conn.commit()
    cur.close()
    conn.close()


def detect_changes(sheet_records, sql_records):
    sheet_df = pd.DataFrame(sheet_records)
    sql_df = pd.DataFrame(sql_records)

    sheet_df["id"] = sheet_df["id"].astype(int)
    sql_df["id"] = sql_df["id"].astype(int)

    inserts = sheet_df[~sheet_df["id"].isin(sql_df["id"])]
    deletes = sql_df[~sql_df["id"].isin(sheet_df["id"])]

    merged = sheet_df.merge(sql_df, on="id", suffixes=("_sheet", "_sql"))

    changes = merged[
        (merged["task_name_sheet"] != merged["task_name_sql"]) |
        (merged["full_name_sheet"] != merged["full_name_sql"]) |
        (merged["updated_at_sheet"] != merged["updated_at_sql"])
    ]

    return inserts, changes, deletes

def normalize_timestamp(value):
    return value if value not in ("", None) else None


if __name__ == "__main__":   
    sheet = get_sheet()

    list_of_records = sheet.get_all_records()
    for row in list_of_records:
        if row["updated_at"] == "":
            row["updated_at"] = None

    sql_df = load_table()
    sql_records = sql_df.to_dict(orient="records")

    if list_of_records != sql_records:
        print("Not matching")
        updates, changes, deletes = detect_changes(list_of_records, sql_records)
        apply_sheet_to_db(updates, changes, deletes)
    else:
        print("Matching")