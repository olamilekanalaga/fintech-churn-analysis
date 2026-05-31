from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "Fintech_user.csv"
DB_PATH = ROOT / "fintech.db"
OUTPUTS = ROOT / "outputs"


def most_common(series: pd.Series, fallback: str = "Unknown") -> str:
    mode = series.dropna().mode()
    return mode.iloc[0] if not mode.empty else fallback


def main() -> None:
    OUTPUTS.mkdir(exist_ok=True)
    df = pd.read_csv(CSV_PATH)

    numeric_fill_zero = [
        "deposits", "withdrawal", "purchases_partners", "purchases", "cc_taken",
        "cc_recommended", "cc_disliked", "cc_liked", "cc_application_begin",
        "registered_phones", "waiting_4_loan", "cancelled_loan", "received_loan",
        "rejected_loan", "left_for_two_month_plus", "left_for_one_month",
        "rewards_earned", "reward_rate",
    ]
    for col in numeric_fill_zero:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for col in ["churn", "app_downloaded", "web_user", "app_web_user", "ios_user", "android_user", "is_referred"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["credit_score"] = pd.to_numeric(df["credit_score"], errors="coerce")

    users = (
        df.groupby("user", as_index=False)
        .agg(
            churn=("churn", "max"),
            age=("age", "median"),
            credit_score=("credit_score", "median"),
            housing=("housing", most_common),
            payment_type=("payment_type", most_common),
            is_referred=("is_referred", "max"),
            total_deposits=("deposits", "sum"),
            total_withdrawals=("withdrawal", "sum"),
            total_purchases=("purchases", "sum"),
            total_partner_purchases=("purchases_partners", "sum"),
            credit_card_applications=("cc_application_begin", "sum"),
            waiting_for_loan=("waiting_4_loan", "max"),
            cancelled_loan=("cancelled_loan", "max"),
            received_loan=("received_loan", "max"),
            rejected_loan=("rejected_loan", "max"),
            app_downloaded=("app_downloaded", "max"),
            web_user=("web_user", "max"),
            app_web_user=("app_web_user", "max"),
            ios_user=("ios_user", "max"),
            android_user=("android_user", "max"),
            registered_phones=("registered_phones", "max"),
            rewards_earned=("rewards_earned", "sum"),
            reward_rate=("reward_rate", "mean"),
        )
    )

    users["age_group"] = pd.cut(users["age"], [0, 24, 34, 44, 54, 120], labels=["18-24", "25-34", "35-44", "45-54", "55+"], include_lowest=True).astype("object").fillna("Unknown")
    users["credit_score_band"] = pd.cut(users["credit_score"], [0, 499, 599, 699, 850], labels=["Under 500", "500-599", "600-699", "700+"], include_lowest=True).astype("object").fillna("Missing")
    users["activity_score"] = users["total_deposits"] + users["total_purchases"] + users["total_partner_purchases"] + users["credit_card_applications"]
    users["activity_segment"] = pd.qcut(users["activity_score"].rank(method="first"), 4, labels=["Very Low Activity", "Low Activity", "Moderate Activity", "High Activity"]).astype(str)
    users["rewards_segment"] = pd.cut(users["rewards_earned"], [-1, 0, 50, users["rewards_earned"].max()], labels=["No Rewards", "Low Rewards", "High Rewards"]).astype(str)

    users["loan_status"] = "No Loan Interaction"
    users.loc[users["waiting_for_loan"].eq(1), "loan_status"] = "Waiting For Loan"
    users.loc[users["received_loan"].eq(1), "loan_status"] = "Received Loan"
    users.loc[users["cancelled_loan"].eq(1), "loan_status"] = "Cancelled Loan"
    users.loc[users["rejected_loan"].eq(1), "loan_status"] = "Rejected Loan"

    users["platform_segment"] = "Unknown"
    users.loc[users["web_user"].eq(1), "platform_segment"] = "Web Only"
    users.loc[users["app_downloaded"].eq(1), "platform_segment"] = "App Only"
    users.loc[users["app_downloaded"].eq(1) & users["web_user"].eq(1), "platform_segment"] = "App + Web"

    risk = pd.Series(0, index=users.index)
    risk += users["activity_segment"].eq("Very Low Activity") * 35
    risk += users["activity_segment"].eq("Low Activity") * 20
    risk += users["rewards_segment"].eq("No Rewards") * 20
    risk += users["rewards_segment"].eq("Low Rewards") * 10
    risk += users["loan_status"].eq("Rejected Loan") * 25
    risk += users["loan_status"].eq("Cancelled Loan") * 15
    risk += users["platform_segment"].eq("Web Only") * 10
    risk += users["is_referred"].eq(0) * 10
    users["risk_score"] = risk.clip(upper=100).astype(int)
    users["risk_segment"] = pd.cut(users["risk_score"], [-1, 29, 59, 100], labels=["Low Risk", "Medium Risk", "High Risk"]).astype(str)

    users["recommended_action"] = "Maintain engagement with lifecycle messaging"
    users.loc[users["platform_segment"].eq("Web Only"), "recommended_action"] = "Encourage app download and mobile onboarding"
    users.loc[users["rewards_segment"].eq("No Rewards"), "recommended_action"] = "Introduce rewards education or welcome offer"
    users.loc[users["loan_status"].isin(["Rejected Loan", "Cancelled Loan"]), "recommended_action"] = "Loan journey follow-up and clearer next steps"
    users.loc[users["risk_segment"].eq("High Risk") & users["activity_segment"].eq("Very Low Activity"), "recommended_action"] = "Activation campaign: prompt first deposit or purchase"

    users.to_csv(OUTPUTS / "users_enriched.csv", index=False)
    with sqlite3.connect(DB_PATH) as conn:
        users.to_sql("users", conn, if_exists="replace", index=False)

    print(f"Created {DB_PATH}")
    print(f"Created {OUTPUTS / 'users_enriched.csv'}")


if __name__ == "__main__":
    main()
