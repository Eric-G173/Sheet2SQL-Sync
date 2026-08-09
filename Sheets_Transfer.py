import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import os
from Database_Load import load_table, get_sheet
from Backup import backup_table
import warnings

import config

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

    columns_sql = ", ".join(config.ALL_COLUMNS)
    placeholders = ", ".join(["%s"] * len(config.ALL_COLUMNS))
    insert_sql = f"INSERT INTO {config.TABLE_NAME} ({columns_sql}) VALUES ({placeholders})"

    set_clause = ", ".join(f"{col} = %s" for col in config.DATA_COLUMNS + [config.TIMESTAMP_COLUMN])
    update_sql = f"UPDATE {config.TABLE_NAME} SET {set_clause} WHERE {config.PRIMARY_KEY} = %s"

    delete_sql = f"DELETE FROM {config.TABLE_NAME} WHERE {config.PRIMARY_KEY} = %s"

    # INSERT new rows
    for _, row in updates.iterrows():
        values = [row[col] for col in [config.PRIMARY_KEY] + config.DATA_COLUMNS]
        values.append(normalize_timestamp(row[config.TIMESTAMP_COLUMN]))
        cur.execute(insert_sql, tuple(values))

    # UPDATE changed rows
    for _, row in changes.iterrows():
        values = [row[f"{col}_sheet"] for col in config.DATA_COLUMNS]
        values.append(normalize_timestamp(row[f"{config.TIMESTAMP_COLUMN}_sheet"]))
        values.append(row[config.PRIMARY_KEY])
        cur.execute(update_sql, tuple(values))

    # DELETE removed rows
    for _, row in deletes.iterrows():
        cur.execute(delete_sql, (row[config.PRIMARY_KEY],))

    conn.commit()
    cur.close()
    conn.close()


def detect_changes(sheet_records, sql_records):
    sheet_df = pd.DataFrame(sheet_records)
    sql_df = pd.DataFrame(sql_records)

    sheet_df[config.PRIMARY_KEY] = sheet_df[config.PRIMARY_KEY].astype(int)
    sql_df[config.PRIMARY_KEY] = sql_df[config.PRIMARY_KEY].astype(int)

    inserts = sheet_df[~sheet_df[config.PRIMARY_KEY].isin(sql_df[config.PRIMARY_KEY])]
    deletes = sql_df[~sql_df[config.PRIMARY_KEY].isin(sheet_df[config.PRIMARY_KEY])]

    merged = sheet_df.merge(sql_df, on=config.PRIMARY_KEY, suffixes=("_sheet", "_sql"))

    is_different = pd.Series(False, index=merged.index)
    for col in config.DATA_COLUMNS + [config.TIMESTAMP_COLUMN]:
        is_different = is_different | (merged[f"{col}_sheet"] != merged[f"{col}_sql"])

    changes = merged[is_different]

    return inserts, changes, deletes


def normalize_timestamp(value):
    return value if value not in ("", None) else None


if __name__ == "__main__":
    sheet = get_sheet()

    list_of_records = sheet.get_all_records()
    for row in list_of_records:
        if row[config.TIMESTAMP_COLUMN] == "":
            row[config.TIMESTAMP_COLUMN] = None

    sql_df = load_table()
    sql_records = sql_df.to_dict(orient="records")

    if list_of_records != sql_records:
        print("Not matching")
        updates, changes, deletes = detect_changes(list_of_records, sql_records)
        backup_table(sql_df)  # snapshot DB before writing anything
        apply_sheet_to_db(updates, changes, deletes)
    else:
        print("Matching")