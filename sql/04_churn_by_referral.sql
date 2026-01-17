SELECT
  CASE 
    WHEN is_referred = 1 THEN 'Referred user'
    ELSE 'Not referred'
  END AS referral_status,
  COUNT(*) AS users,
  SUM(churn) AS churned_users,
  ROUND(100.0 * SUM(churn) / COUNT(*), 2) AS churn_rate_pct
FROM users
GROUP BY referral_status
ORDER BY churn_rate_pct DESC;
