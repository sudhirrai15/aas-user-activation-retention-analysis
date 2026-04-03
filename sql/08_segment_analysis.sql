-- Compare key performance metrics across user segments.

WITH activation_status AS (
    SELECT
        u.user_id,
        u.device_type,
        u.country,
        u.plan_type,
        u.company_size,
        CASE
            WHEN MIN(CASE WHEN e.event_name = 'workspace_created' THEN e.event_date END) <= u.signup_date + INTERVAL '7 day'
             AND MIN(CASE WHEN e.event_name = 'first_report_created' THEN e.event_date END) <= u.signup_date + INTERVAL '7 day'
            THEN 1
            ELSE 0
        END AS is_activated
    FROM users u
    LEFT JOIN events e
        ON u.user_id = e.user_id
    GROUP BY u.user_id, u.device_type, u.country, u.plan_type, u.company_size, u.signup_date
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
    device_type,
    plan_type,
    company_size,
    COUNT(DISTINCT a.user_id) AS total_users,
    SUM(a.is_activated) AS activated_users,
    ROUND(100.0 * SUM(a.is_activated) / COUNT(DISTINCT a.user_id), 2) AS activation_rate_pct,
    SUM(COALESCE(r.retained_day30, 0)) AS retained_users_day30,
    ROUND(100.0 * SUM(COALESCE(r.retained_day30, 0)) / COUNT(DISTINCT a.user_id), 2) AS day30_retention_pct
FROM activation_status a
LEFT JOIN day30_retention r
    ON a.user_id = r.user_id
GROUP BY device_type, plan_type, company_size
ORDER BY day30_retention_pct DESC, activation_rate_pct DESC;
