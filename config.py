"""
Central configuration for Sheet2SQL-Sync.

Edit the values below to point this tool at your own Google Sheet and
MySQL table — nothing else in the codebase needs to change.
"""

# --- Google Sheets ---
CREDS_FILE = "database_Creds.json"
SHEET_NAME = "Project SQL UI"
WORKSHEET_INDEX = 0  # 0 = first tab (what gspread calls "sheet1")
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# --- MySQL table schema ---
TABLE_NAME = "task"
PRIMARY_KEY = "id"
TIMESTAMP_COLUMN = "updated_at"
DATA_COLUMNS = ["task_name", "full_name"]  # every column except id/updated_at

# Built automatically from the pieces above — don't edit this one directly.
ALL_COLUMNS = [PRIMARY_KEY] + DATA_COLUMNS + [TIMESTAMP_COLUMN]

# --- Backups ---
BACKUP_DIR = "backups"