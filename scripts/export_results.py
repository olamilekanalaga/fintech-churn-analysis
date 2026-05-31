from __future__ import annotations

import glob
import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "fintech.db"
SQL_DIR = ROOT / "sql"
OUT_DIR = ROOT / "outputs"


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        for sql_file in sorted(glob.glob(str(SQL_DIR / "*.sql"))):
            path = Path(sql_file)
            query = path.read_text(encoding="utf-8").strip().rstrip(";")
            df = pd.read_sql_query(query, conn)
            out_path = OUT_DIR / f"{path.stem}.csv"
            df.to_csv(out_path, index=False)
            print(f"{path.name} -> {out_path.name} ({len(df)} rows)")


if __name__ == "__main__":
    main()
