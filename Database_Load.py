import mysql.connector
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from dotenv import load_dotenv
import os
import warnings

import config

warnings.filterwarnings("ignore", message=".*only supports SQLAlchemy.*")
load_dotenv()

USERNAME = os.getenv("DB_USER")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DATABASE_NAME = os.getenv("DB_NAME")
PASSWORD = os.getenv("DB_PASSWORD")


def get_sheet():
    """Authenticates with Google Sheets and returns the worksheet.
    Only runs when called — not at import time."""
    creds = Credentials.from_service_account_file(config.CREDS_FILE, scopes=config.SCOPES)
    client = gspread.authorize(creds)
    return client.open(config.SHEET_NAME).get_worksheet(config.WORKSHEET_INDEX)


def load_table():
    conn = mysql.connector.connect(
        host=HOST,
        database=DATABASE_NAME,
        user=USERNAME,
        password=PASSWORD,
        port=PORT
    )
    df = pd.read_sql(f"SELECT * FROM {config.TABLE_NAME};", conn)
    conn.close()
    print(df.columns)
    return df


def df_to_sheets(df):
    header = list(df.columns)
    rows = df.values.tolist()
    return [header] + rows

if __name__ == "__main__":
    df = load_table()
    values = df_to_sheets(df)
    sheet = get_sheet()
    sheet.clear()
    sheet.update(values, "A1")