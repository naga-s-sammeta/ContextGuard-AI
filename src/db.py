"""Thin DuckDB access layer."""
import duckdb
from config import DB_PATH


def run_sql(sql, db_path=None):
    """Execute SQL read-only. Returns (columns, rows) or raises."""
    con = duckdb.connect(db_path or DB_PATH, read_only=True)
    try:
        cur = con.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
        return cols, rows
    finally:
        con.close()


def table_last_loaded(table_name, db_path=None):
    """Return (last_loaded_timestamp, sla_hours) from the freshness metadata."""
    con = duckdb.connect(db_path or DB_PATH, read_only=True)
    try:
        r = con.execute(
            "SELECT last_loaded, sla_hours FROM _table_freshness WHERE table_name = ?",
            [table_name],
        ).fetchone()
        return (r[0], r[1]) if r else (None, None)
    finally:
        con.close()
