from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
USERS_PATH = ROOT / "outputs" / "users_enriched.csv"


st.set_page_config(page_title="Fintech Churn Analytics", layout="wide")


@st.cache_data
def load_users() -> pd.DataFrame:
    return pd.read_csv(USERS_PATH)


users = load_users()

st.title("Fintech Customer Churn & Retention Analytics")

platforms = sorted(users["platform_segment"].dropna().unique())
selected_platforms = st.sidebar.multiselect("Platform", platforms, default=platforms)

risks = ["High Risk", "Medium Risk", "Low Risk"]
selected_risks = st.sidebar.multiselect("Risk segment", risks, default=risks)

filtered = users[
    users["platform_segment"].isin(selected_platforms)
    & users["risk_segment"].isin(selected_risks)
].copy()

total_users = len(filtered)
churned_users = int(filtered["churn"].sum())
churn_rate = filtered["churn"].mean() * 100 if total_users else 0
avg_risk = filtered["risk_score"].mean() if total_users else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Users", f"{total_users:,}")
kpi2.metric("Churned Users", f"{churned_users:,}")
kpi3.metric("Churn Rate", f"{churn_rate:.2f}%")
kpi4.metric("Average Risk Score", f"{avg_risk:.1f}")

tab_overview, tab_segments, tab_risk = st.tabs(["Overview", "Churn Drivers", "Risk Actions"])

with tab_overview:
    left, right = st.columns(2)
    activity = (
        filtered.groupby("activity_segment", as_index=False)
        .agg(users=("user", "count"), churn_rate=("churn", "mean"), avg_activity=("activity_score", "mean"))
    )
    activity["churn_rate"] *= 100
    activity = activity.sort_values("churn_rate", ascending=False)

    platform = (
        filtered.groupby("platform_segment", as_index=False)
        .agg(users=("user", "count"), churn_rate=("churn", "mean"))
    )
    platform["churn_rate"] *= 100
    platform = platform.sort_values("churn_rate", ascending=False)

    left.subheader("Churn by Activity Segment")
    left.bar_chart(activity, x="activity_segment", y="churn_rate")

    right.subheader("Churn by Platform")
    right.bar_chart(platform, x="platform_segment", y="churn_rate")

    st.subheader("Activity Segment Summary")
    st.dataframe(activity, use_container_width=True)

with tab_segments:
    left, right = st.columns(2)

    loan = (
        filtered.groupby("loan_status", as_index=False)
        .agg(users=("user", "count"), churn_rate=("churn", "mean"))
    )
    loan["churn_rate"] *= 100
    loan = loan.sort_values("churn_rate", ascending=False)

    rewards = (
        filtered.groupby("rewards_segment", as_index=False)
        .agg(users=("user", "count"), churn_rate=("churn", "mean"), avg_rewards=("rewards_earned", "mean"))
    )
    rewards["churn_rate"] *= 100
    rewards = rewards.sort_values("churn_rate", ascending=False)

    left.subheader("Churn by Loan Status")
    left.bar_chart(loan, x="loan_status", y="churn_rate")

    right.subheader("Churn by Rewards Segment")
    right.bar_chart(rewards, x="rewards_segment", y="churn_rate")

    st.subheader("Reward Segment Summary")
    st.dataframe(rewards, use_container_width=True)

with tab_risk:
    left, right = st.columns(2)

    risk_summary = (
        filtered.groupby("risk_segment", as_index=False)
        .agg(users=("user", "count"), churned_users=("churn", "sum"), churn_rate=("churn", "mean"), avg_risk_score=("risk_score", "mean"))
    )
    risk_summary["churn_rate"] *= 100
    risk_summary = risk_summary.sort_values("avg_risk_score", ascending=False)

    actions = (
        filtered.groupby("recommended_action", as_index=False)
        .agg(users=("user", "count"), churn_rate=("churn", "mean"), avg_risk_score=("risk_score", "mean"))
    )
    actions["churn_rate"] *= 100
    actions = actions.sort_values("churn_rate", ascending=False)

    left.subheader("Users by Risk Segment")
    left.bar_chart(risk_summary, x="risk_segment", y="users")

    right.subheader("Churn Rate by Risk Segment")
    right.bar_chart(risk_summary, x="risk_segment", y="churn_rate")

    st.subheader("Recommended Retention Actions")
    st.dataframe(actions, use_container_width=True)

    st.subheader("Highest Risk Users")
    cols = ["user", "risk_score", "risk_segment", "activity_segment", "loan_status", "rewards_segment", "platform_segment", "recommended_action", "churn"]
    st.dataframe(filtered.sort_values("risk_score", ascending=False)[cols].head(50), use_container_width=True)
