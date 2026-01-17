# export_results.py
# Runs every .sql file in /sql against fintech.db and writes CSV outputs to /outputs

import os
import glob
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = "fintech.db"
SQL_DIR = "sql"
OUT_DIR = "outputs"


def _is_query(stmt: str) -> bool:
    s = stmt.strip().lower()
    return s.startswith("select") or s.startswith("with")


def run_sql_file(conn: sqlite3.Connection, sql_path: str) -> pd.DataFrame:
    """
    Supports either:
    - a single SELECT/WITH query
    - OR multiple statements where the LAST statement is SELECT/WITH
      (earlier statements will be executed via executescript)
    """
    raw = Path(sql_path).read_text(encoding="utf-8").strip()

    # Remove BOM if any
    raw = raw.lstrip("\ufeff").strip()

    # Split into statements, keep non-empty
    parts = [p.strip() for p in raw.split(";") if p.strip()]

    if not parts:
        raise ValueError("SQL file is empty after parsing.")

    # If it is a single SELECT/WITH, just run it
    if len(parts) == 1 and _is_query(parts[0]):
        return pd.read_sql_query(parts[0], conn)

    # Otherwise, we expect the last statement to be SELECT/WITH
    last = parts[-1]
    if not _is_query(last):
        raise ValueError(
            "SQL file has multiple statements, but the LAST statement is not a SELECT/WITH query.\n"
            "Tip: end the file with a final SELECT that produces the output table."
        )

    # Execute everything before the last statement
    prefix = ";\n".join(parts[:-1]).strip()
    if prefix:
        conn.executescript(prefix + ";")

    # Run final query and return
    return pd.read_sql_query(last, conn)


def main():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Cannot find {DB_PATH}. Run build_user_table.py first to create the database."
        )

    os.makedirs(OUT_DIR, exist_ok=True)

    sql_files = sorted(glob.glob(os.path.join(SQL_DIR, "*.sql")))
    if not sql_files:
        raise FileNotFoundError(f"No .sql files found in {SQL_DIR}/")

    conn = sqlite3.connect(DB_PATH)

    print(f"[OK] DB: {DB_PATH}")
    print(f"[OK] Found {len(sql_files)} SQL files in {SQL_DIR}/")
    print(f"[OK] Outputs will be saved to {OUT_DIR}/\n")

    failures = 0

    for sql_path in sql_files:
        base = os.path.basename(sql_path)
        out_name = os.path.splitext(base)[0] + ".csv"
        out_path = os.path.join(OUT_DIR, out_name)

        try:
            df = run_sql_file(conn, sql_path)
            df.to_csv(out_path, index=False)
            print(f"[DONE] {base} -> {out_path}  (rows={len(df)}, cols={len(df.columns)})")
        except Exception as e:
            failures += 1
            print(f"[FAIL] {base}: {e}")

    conn.close()

    print("\n--- Summary ---")
    print(f"Success: {len(sql_files) - failures}")
    print(f"Failed : {failures}")
    print(f"Outputs: {OUT_DIR}/")


if __name__ == "__main__":
    main()
