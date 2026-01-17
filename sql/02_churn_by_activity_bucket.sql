WITH base AS (
  SELECT
    user,
    churn,
    (total_deposits + total_purchases + total_partner_purchases) AS activity_score
  FROM users
),
ranked AS (
  SELECT
    *,
    NTILE(4) OVER (ORDER BY activity_score) AS activity_quartile
  FROM base
)
SELECT
  activity_quartile,
  COUNT(*) AS users,
  SUM(churn) AS churned_users,
  ROUND(100.0 * SUM(churn) / COUNT(*), 2) AS churn_rate_pct,
  ROUND(AVG(activity_score), 2) AS avg_activity_score
FROM ranked
GROUP BY activity_quartile
ORDER BY activity_quartile;
