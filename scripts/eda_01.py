from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "Fintech_user.csv"


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    print("Shape:", df.shape)
    print("Unique users:", df["user"].nunique())
    print("Duplicate user rows:", df["user"].duplicated().sum())
    print("Raw churn rate:", round(df["churn"].mean() * 100, 2), "%")

    missing = (
        df.isna()
        .mean()
        .mul(100)
        .round(2)
        .sort_values(ascending=False)
        .reset_index()
    )
    missing.columns = ["column", "missing_pct"]
    print("\nTop missing columns:")
    print(missing.head(10))

    activity_cols = ["deposits", "withdrawal", "purchases", "purchases_partners", "rewards_earned"]
    print("\nAverage activity metrics by churn:")
    print(df.groupby("churn")[activity_cols].mean(numeric_only=True).round(2))


if __name__ == "__main__":
    main()
