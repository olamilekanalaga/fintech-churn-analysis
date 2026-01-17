# Fintech Churn Analysis (SQL + Python + SQLite)

## Project summary
This project analyses customer churn using a fintech user dataset. I converted event-level records into a clean user-level table, then used SQL to identify high-risk segments and behavioural drivers of churn across engagement, lending outcomes, referrals, rewards, and platform usage.

## Dataset
Source: Kaggle fintech churn dataset (public).  
Note: This repo contains no personal customer information.

## Workflow
1) **Build a user-level dataset (single row per user)**
- Input: raw CSV (event-level rows)
- Output: SQLite database with a `users` table (user-level grain)

2) **Run SQL analyses on SQLite**
- Overall churn rate
- Churn vs engagement/activity
- Churn vs loan outcomes
- Churn vs referral status
- Churn vs rewards
- Churn vs platform (app vs web)

## Key findings (from SQL)
- **Overall churn rate:** ~45.16%
- **Engagement is strongly linked to churn:** lowest activity quartile churns far more than the highest quartile.
- **Loan outcomes matter:** users with rejected loans show the highest churn rate.
- **Referrals reduce churn:** referred users churn less than non-referred users.
- **Rewards reduce churn:** high-reward users churn significantly less than users with no/low rewards.
- **Platform matters:** web users churn more than app users.

## Business recommendations
- Improve early activation: drive first deposit + first purchase sooner (reduce inactivity-driven churn).
- Add retention triggers for “low activity” users (nudges, education, reminders).
- Improve lending UX and communication for rejected/cancelled loan journeys.
- Invest in referral loops and rewards since both correlate with lower churn.

## How to run
Create the user-level table:
```bash
python build_user_table.py
