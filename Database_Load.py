import mysql.connector
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from dotenv import load_dotenv
import os
import warnings
warnings.filterwarnings("ignore", message=".*only supports SQLAlchemy.*")
load_dotenv()
USERNAME = os.getenv("DB_USER")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DATABASE_NAME = os.getenv("DB_NAME")
PASSWORD = os.getenv("DB_PASSWORD")
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("database_Creds.json", scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open("Project SQL UI").sheet1


def load_table():
    conn = mysql.connector.connect(
        host=HOST,
        database=DATABASE_NAME,
        user=USERNAME,
        password=PASSWORD,
        port=PORT
    )
    df = pd.read_sql("SELECT * FROM task;", conn)
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
    sheet.clear()
    sheet.update(values, "A1")