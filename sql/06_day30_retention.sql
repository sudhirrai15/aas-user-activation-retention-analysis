-- Measure Day 30 retention by signup cohort.

WITH signup_cohorts AS (
    SELECT
        user_id,
        signup_date,
        DATE_TRUNC('month', signup_date) AS signup_month
    FROM users
),
day30_activity AS (
    SELECT DISTINCT
        s.user_id,
        s.signup_month
    FROM signup_cohorts s
    JOIN events e
        ON s.user_id = e.user_id
    WHERE e.event_date >= s.signup_date + INTERVAL '30 day'
      AND e.event_date < s.signup_date + INTERVAL '31 day'
),
cohort_sizes AS (
    SELECT
        signup_month,
        COUNT(DISTINCT user_id) AS cohort_size
    FROM signup_cohorts
    GROUP BY signup_month
),
retained_counts AS (
    SELECT
        signup_month,
        COUNT(DISTINCT user_id) AS retained_users_day30
    FROM day30_activity
    GROUP BY signup_month
)

SELECT
    c.signup_month,
    c.cohort_size,
    COALESCE(r.retained_users_day30, 0) AS retained_users_day30,
    ROUND(100.0 * COALESCE(r.retained_users_day30, 0) / c.cohort_size, 2) AS day30_retention_pct
FROM cohort_sizes c
LEFT JOIN retained_counts r
    ON c.signup_month = r.signup_month
ORDER BY c.signup_month;
