SELECT
  CASE
    WHEN app_downloaded = 1 AND web_user = 1 THEN 'App + Web user'
    WHEN app_downloaded = 1 THEN 'App user'
    WHEN web_user = 1 THEN 'Web user'
    ELSE 'Unknown platform'
  END AS platform,
  COUNT(*) AS users,
  SUM(churn) AS churned_users,
  ROUND(100.0 * SUM(churn) / COUNT(*), 2) AS churn_rate_pct
FROM users
GROUP BY platform
ORDER BY churn_rate_pct DESC;
