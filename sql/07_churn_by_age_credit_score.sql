SELECT
  age_group,
  credit_score_band,
  COUNT(*) AS users,
  SUM(churn) AS churned_users,
  ROUND(100.0 * SUM(churn) / COUNT(*), 2) AS churn_rate_pct
FROM users
GROUP BY age_group, credit_score_band
HAVING COUNT(*) >= 100
ORDER BY churn_rate_pct DESC;
