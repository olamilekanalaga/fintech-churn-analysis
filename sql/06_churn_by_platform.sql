SELECT
  platform_segment,
  COUNT(*) AS users,
  SUM(churn) AS churned_users,
  ROUND(100.0 * SUM(churn) / COUNT(*), 2) AS churn_rate_pct
FROM users
GROUP BY platform_segment
ORDER BY churn_rate_pct DESC;
