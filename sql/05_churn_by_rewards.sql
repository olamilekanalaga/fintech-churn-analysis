SELECT
  rewards_segment,
  COUNT(*) AS users,
  SUM(churn) AS churned_users,
  ROUND(100.0 * SUM(churn) / COUNT(*), 2) AS churn_rate_pct,
  ROUND(AVG(rewards_earned), 2) AS avg_rewards
FROM users
GROUP BY rewards_segment
ORDER BY churn_rate_pct DESC;
