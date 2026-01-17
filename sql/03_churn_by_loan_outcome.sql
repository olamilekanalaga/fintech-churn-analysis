SELECT
  CASE
    WHEN received_loan = 1 THEN 'Received loan'
    WHEN rejected_loan = 1 THEN 'Rejected loan'
    WHEN cancelled_loan = 1 THEN 'Cancelled loan'
    ELSE 'No loan interaction'
  END AS loan_outcome,
  COUNT(*) AS users,
  SUM(churn) AS churned_users,
  ROUND(100.0 * SUM(churn) / COUNT(*), 2) AS churn_rate_pct
FROM users
GROUP BY loan_outcome
ORDER BY churn_rate_pct DESC;
