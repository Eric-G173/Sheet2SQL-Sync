import pandas as pd
from unittest.mock import patch, MagicMock

# --- Database_Load ---

def test_load_table():
    mock_df = pd.DataFrame({"id": [1], "task_name": ["A"], "full_name": ["Alice"], "updated_at": ["2024-01-01"]})
    with patch("mysql.connector.connect") as mock_conn, patch("pandas.read_sql", return_value=mock_df):
        from Database_Load import load_table
        result = load_table()
    assert isinstance(result, pd.DataFrame)
    mock_conn.return_value.close.assert_called_once()

def test_df_to_sheets():
    from Database_Load import df_to_sheets
    df = pd.DataFrame({"id": [1], "task_name": ["A"], "full_name": ["Alice"], "updated_at": ["2024-01-01"]})
    result = df_to_sheets(df)
    assert result[0] == ["id", "task_name", "full_name", "updated_at"]
    assert result[1] == [1, "A", "Alice", "2024-01-01"]

# --- Sheets_Transfer ---

def test_detect_changes():
    from Sheets_Transfer import detect_changes
    sheet = [{"id": 1, "task_name": "New", "full_name": "Alice", "updated_at": "2024-06-01"}]
    sql   = [{"id": 1, "task_name": "Old", "full_name": "Alice", "updated_at": "2024-01-01"}]
    inserts, changes, deletes = detect_changes(sheet, sql)
    assert len(changes) == 1
    assert len(inserts) == 0
    assert len(deletes) == 0

def test_apply_sheet_to_db():
    from Sheets_Transfer import apply_sheet_to_db
    mock_conn = MagicMock()
    with patch("mysql.connector.connect", return_value=mock_conn):
        apply_sheet_to_db(pd.DataFrame(), pd.DataFrame(), pd.DataFrame([{"id": 99}]))
    sql = mock_conn.cursor.return_value.execute.call_args[0][0]
    assert "DELETE FROM task" in sql
    mock_conn.commit.assert_called_once()