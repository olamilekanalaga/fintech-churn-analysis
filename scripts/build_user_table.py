import pandas as pd
import sqlite3

CSV_PATH = "Fintech_user.csv"   # if file is in /data folder: "data/Fintech_user.csv"
DB_PATH  = "fintech.db"

def main():
    # Load
    df = pd.read_csv(CSV_PATH)

    # Basic cleanup (safe defaults)
    # - ensure expected numeric fields are numeric (coerce errors -> NaN -> fill 0 for counts/sums)
    num_cols_fill0 = [
        "deposits", "withdrawal", "purchases", "purchases_partners", "rewards_earned"
    ]
    for c in num_cols_fill0:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # Binary flags (0/1) - coerce and fill 0
    flag_cols_fill0 = [
        "churn", "is_referred",
        "received_loan", "rejected_loan", "cancelled_loan",
        "app_downloaded", "web_user", "app_web_user"
    ]
    for c in flag_cols_fill0:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

    # reward_rate is a rate -> keep as float, fill NaN with 0 (or keep NaN if you prefer)
    if "reward_rate" in df.columns:
        df["reward_rate"] = pd.to_numeric(df["reward_rate"], errors="coerce").fillna(0.0)

    # Build USER-LEVEL table (one row per user)
    user_df = (
        df.groupby("user", as_index=False)
          .agg(
              churn=("churn", "max"),
              is_referred=("is_referred", "max"),

              total_deposits=("deposits", "sum"),
              total_withdrawals=("withdrawal", "sum"),
              total_purchases=("purchases", "sum"),
              total_partner_purchases=("purchases_partners", "sum"),

              received_loan=("received_loan", "max"),
              rejected_loan=("rejected_loan", "max"),
              cancelled_loan=("cancelled_loan", "max"),

              app_downloaded=("app_downloaded", "max"),
              web_user=("web_user", "max"),
              app_web_user=("app_web_user", "max"),

              rewards_earned=("rewards_earned", "sum"),
              reward_rate=("reward_rate", "mean"),
          )
    )

    print("User-level table shape:", user_df.shape)
    print(user_df.head())

    # Save to SQLite (replaces the users table each run)
    conn = sqlite3.connect(DB_PATH)
    user_df.to_sql("users", conn, if_exists="replace", index=False)
    conn.close()

    print(f"Saved user-level table to {DB_PATH} (table: users)")

if __name__ == "__main__":
    main()
