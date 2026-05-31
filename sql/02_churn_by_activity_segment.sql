SELECT
  activity_segment,
  COUNT(*) AS users,
  SUM(churn) AS churned_users,
  ROUND(100.0 * SUM(churn) / COUNT(*), 2) AS churn_rate_pct,
  ROUND(AVG(activity_score), 2) AS avg_activity_score
FROM users
GROUP BY activity_segment
ORDER BY churn_rate_pct DESC;
