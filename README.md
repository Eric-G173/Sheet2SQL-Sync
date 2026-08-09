# Sheet2SQL-Sync

A two-way sync tool between a Google Sheet and a MySQL table: edit either side, run a script, and it detects inserts, updates, deletes, and applies them, with an automatic backup snapshot before every write.

# Features
- Detects new, changed, and deleted rows by comparing a Google Sheet against a MySQL table
- Push Sheet edits into MySQL (Sheets_Transfer.py), or pull the full MySQL table back into the Sheet (Database_Load.py)
- Automatic local JSON backup of the table before any write, with a one-command restore
- Fully configurable via a single config.py — swap in your own table name, columns, and sheet name without touching the core logic
- Tested with pytest, using mocks so tests never touch a real database or Google account
# Tech stack
- **Backend:** Python, mysql-connector-python, pandas
- **Google Sheets:** gspread, google-auth (service account)
- **Testing:** pytest
- **CI/CD:** GitHub Actions
# Architecture: Why connections load lazily, not at import

Earlier versions of this project authenticated to Google Sheets and connected to MySQL as soon as the module was imported. That worked fine locally, but broke in CI: GitHub Actions doesn't have a real database_Creds.json file, so simply importing the module to run a unit test crashed with a FileNotFoundError, before the test itself ever ran.

The fix was to wrap every external connection; Google auth (get_sheet()) and MySQL (load_table(), apply_sheet_to_db()) in its own function, so nothing runs until it's actually called. Importing Database_Load or Sheets_Transfer now has zero side effects allowing for unit tests to properly run without having to access sensitive information

# Configuration

All the project-specific values live in **config.py**, nothing else needs to change to point this tool at a different sheet or table:
```
SHEET_NAME = "Project SQL UI"
TABLE_NAME = "task"
PRIMARY_KEY = "id"
TIMESTAMP_COLUMN = "updated_at"
DATA_COLUMNS = ["task_name", "full_name"]
```
# Running locally
```
git clone https://github.com/yourusername/Sheet2SQL-Sync.git
cd Sheet2SQL-Sync
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Create a .env file in the project root:
```
DB_USER=your-db-username
DB_PASSWORD=your-db-password
HOST=your-db-host
PORT=3306
DB_NAME=your-database-name
```
You'll also need a Google service account key saved as database_Creds.json in the project root, used to authenticate with Google Sheets. An example JSON is shown.

Then run:
```
python Sheets_Transfer.py   # push Sheet edits into MySQL
python Database_Load.py     # pull MySQL into the Sheet
```
To restore the table from a backup:
```
python Backup.py backups/task_backup_<timestamp>.json
```
# Running tests
```
pytest -v
```
