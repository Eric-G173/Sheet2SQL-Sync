# Sheet2SQL Sync
This project converts google sheets into a UI that can be used for postgreSQL databases. The idea behind this project is to allow those with less SQL experience to take something familiar (Google Sheets) and use it to make database updates and additions without the need for SQL knowledge.

Each file acts as a command that executes different functions such as loading the database or sending data.
## Features
- ID‑Based Record Matching - Uses a stable id column to match rows between Sheets and SQL, preventing duplicates or mismatches.
- Two‑Way Data Sync - Synchronizes data between Google Sheets and a PostgreSQL database, ensuring both stay up‑to‑date.
- Database_Load.py - This file will load your postgreSQL database into google sheets.
- Sheets_Transfer.py - This file will send changes made in google sheets to your database.

## Planned Features
- Column creation/editing
- Security additions
- Conflict resolution for multiple requests
- Rate limiting
- Backup database or tracking of changes incase of reverting

## Tech Stack
### Languages
- Python
- SQL
### Backend / Database
- PostgreSQL
- psycopg2
- pandas
### Google Integration
- Google Sheets API
- gspread (Sheets client library)
- Google Cloud Service Account (OAuth2)
