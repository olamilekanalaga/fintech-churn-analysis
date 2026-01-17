import pandas as pd

PATH = "Fintech_user.csv"  # if your file is in the same folder as this script
# If it's in a /data folder, use: PATH = "data/Fintech_user.csv"

def main():
    df = pd.read_csv(PATH)

    print("\n==============================")
    print("1) BASIC SHAPE")
    print("==============================")
    print("rows, cols:", df.shape)
    print("\nColumns:")
    print(df.columns.tolist())

    print("\n==============================")
    print("2) DATA TYPES")
    print("==============================")
    print(df.dtypes.sort_values())

    print("\n==============================")
    print("3) MISSING VALUES (COUNT + %)")
    print("==============================")
    missing_count = df.isna().sum().sort_values(ascending=False)
    missing_pct = (df.isna().mean() * 100).sort_values(ascending=False)
    missing = pd.DataFrame({"missing_count": missing_count, "missing_pct": missing_pct})
    print(missing.head(20))

    print("\n==============================")
    print("4) CHURN BALANCE")
    print("==============================")
    if "churn" not in df.columns:
        raise ValueError("No 'churn' column found. Check dataset columns.")

    churn_counts = df["churn"].value_counts(dropna=False)
    churn_pct = df["churn"].value_counts(normalize=True, dropna=False) * 100
    churn_table = pd.DataFrame({"count": churn_counts, "pct": churn_pct.round(2)})
    print(churn_table)

    print("\n==============================")
    print("5) QUICK SANITY CHECKS")
    print("==============================")
    # Check duplicates by user
    if "user" in df.columns:
        dup_users = df["user"].duplicated().sum()
        print("duplicate user ids:", dup_users)

    # Quick numeric summary (helps spot weird ranges)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    print("\nNumeric summary (selected):")
    print(df[numeric_cols].describe().T[["min", "mean", "max"]].head(15))

    print("\n==============================")
    print("6) FIRST INSIGHT TEST: churn vs inactivity")
    print("==============================")
    # Define inactivity proxies (based on your columns)
    # Inactivity = little/no deposits + little/no purchases + not app/web active
    cols_needed = ["deposits", "purchases", "app_downloaded", "web_user", "app_web_user"]
    for c in cols_needed:
        if c not in df.columns:
            print(f"WARNING: missing expected column: {c}")

    # Only use what exists
    deposits = df["deposits"] if "deposits" in df.columns else 0
    purchases = df["purchases"] if "purchases" in df.columns else 0

    # For engagement columns, handle if they don't exist
    app_downloaded = df["app_downloaded"] if "app_downloaded" in df.columns else 0
    web_user = df["web_user"] if "web_user" in df.columns else 0
    app_web_user = df["app_web_user"] if "app_web_user" in df.columns else 0

    df["is_inactive"] = (
        (deposits.fillna(0) == 0) &
        (purchases.fillna(0) == 0) &
        (app_downloaded.fillna(0) == 0) &
        (web_user.fillna(0) == 0) &
        (app_web_user.fillna(0) == 0)
    ).astype(int)

    # Compare churn rate for inactive vs active
    inactivity_churn = (
        df.groupby("is_inactive")["churn"]
          .agg(users="count", churn_rate="mean")
          .reset_index()
    )
    inactivity_churn["churn_rate"] = (inactivity_churn["churn_rate"] * 100).round(2)

    print("\nChurn by inactivity flag (0=active, 1=inactive):")
    print(inactivity_churn)

    # Compare averages for churned vs not churned for key activity metrics
    compare_cols = [c for c in ["deposits", "withdrawal", "purchases", "purchases_partners"] if c in df.columns]
    churn_activity = (
        df.groupby("churn")[compare_cols]
          .mean(numeric_only=True)
          .round(2)
          .reset_index()
    )
    print("\nAverage activity metrics by churn (0=not churned, 1=churned):")
    print(churn_activity)

    print("\nDONE. Next step: turn the best findings into SQL + dashboard.")

if __name__ == "__main__":
    main()
