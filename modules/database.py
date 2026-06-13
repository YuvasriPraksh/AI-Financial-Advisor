"""
database.py - SQLite Database Management for AI Financial Advisor
Handles all CRUD operations for expense storage.
"""

import sqlite3
import os
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "expenses.db")


def get_connection():
    """Return a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create the expenses table if it does not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            date      TEXT    NOT NULL,
            merchant  TEXT    NOT NULL,
            amount    REAL    NOT NULL,
            category  TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def insert_expense(merchant: str, amount: float, category: str, date: str = None) -> int:
    """
    Insert a new expense record.
    Returns the row id of the inserted record.
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (date, merchant, amount, category) VALUES (?, ?, ?, ?)",
        (date, merchant, amount, category),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def fetch_all_expenses() -> pd.DataFrame:
    """Return all expenses as a Pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC", conn)
    conn.close()
    return df


def fetch_expenses_by_category() -> pd.DataFrame:
    """Return total amount grouped by category."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT category, SUM(amount) AS total FROM expenses GROUP BY category ORDER BY total DESC",
        conn,
    )
    conn.close()
    return df


def fetch_monthly_summary() -> pd.DataFrame:
    """Return monthly expense totals."""
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT strftime('%Y-%m', date) AS month,
               SUM(amount)            AS total,
               COUNT(*)               AS transactions
        FROM   expenses
        GROUP  BY month
        ORDER  BY month DESC
        """,
        conn,
    )
    conn.close()
    return df


def delete_expense(expense_id: int) -> bool:
    """Delete an expense by id. Returns True on success."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def get_summary_stats() -> dict:
    """Return key summary statistics for the dashboard."""
    df = fetch_all_expenses()
    if df.empty:
        return {
            "total_expenses": 0.0,
            "transaction_count": 0,
            "highest_category": "N/A",
            "average_spending": 0.0,
            "categories": {},
        }
    cat_df = fetch_expenses_by_category()
    return {
        "total_expenses": float(df["amount"].sum()),
        "transaction_count": len(df),
        "highest_category": cat_df.iloc[0]["category"] if not cat_df.empty else "N/A",
        "average_spending": float(df["amount"].mean()),
        "categories": dict(zip(cat_df["category"], cat_df["total"])),
    }


# Ensure the table exists when the module is first imported
initialize_database()
