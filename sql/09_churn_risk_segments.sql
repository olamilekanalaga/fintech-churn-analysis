SELECT
  risk_segment,
  COUNT(*) AS users,
  SUM(churn) AS churned_users,
  ROUND(100.0 * SUM(churn) / COUNT(*), 2) AS churn_rate_pct,
  ROUND(AVG(risk_score), 2) AS avg_risk_score
FROM users
GROUP BY risk_segment
ORDER BY avg_risk_score DESC;
