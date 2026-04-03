-- Measure whether early feature adoption is associated with Day 30 retention.

WITH early_feature_usage AS (
    SELECT
        u.user_id,
        e.feature_name,
        1 AS used_feature_early
    FROM users u
    JOIN events e
        ON u.user_id = e.user_id
    WHERE e.feature_name IS NOT NULL
      AND e.event_date <= u.signup_date + INTERVAL '7 day'
    GROUP BY u.user_id, e.feature_name
),
day30_retention AS (
    SELECT DISTINCT
        u.user_id,
        1 AS retained_day30
    FROM users u
    JOIN events e
        ON u.user_id = e.user_id
    WHERE e.event_date >= u.signup_date + INTERVAL '30 day'
      AND e.event_date < u.signup_date + INTERVAL '31 day'
)

SELECT
    f.feature_name,
    COUNT(DISTINCT f.user_id) AS users_who_used_feature,
    SUM(COALESCE(r.retained_day30, 0)) AS retained_users_day30,
    ROUND(100.0 * SUM(COALESCE(r.retained_day30, 0)) / COUNT(DISTINCT f.user_id), 2) AS day30_retention_pct
FROM early_feature_usage f
LEFT JOIN day30_retention r
    ON f.user_id = r.user_id
GROUP BY f.feature_name
HAVING COUNT(DISTINCT f.user_id) >= 10
ORDER BY day30_retention_pct DESC, users_who_used_feature DESC;
