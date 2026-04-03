# Data Dictionary

## users
This table contains user-level profile and acquisition information.

| Column | Description |
|---|---|
| `user_id` | Unique identifier for each user |
| `signup_date` | Date the user completed signup |
| `country` | User country |
| `region` | Geographic region |
| `device_type` | Primary device used during onboarding |
| `acquisition_channel` | Source channel that brought the user in |
| `plan_type` | User plan at signup, such as free or trial |
| `company_size` | Company size segment associated with the user |
| `industry` | Industry segment associated with the account |

## events
This table contains event-level user behavior across the product journey.

| Column | Description |
|---|---|
| `event_id` | Unique identifier for each event |
| `user_id` | User associated with the event |
| `event_date` | Date of the event |
| `event_name` | Name of the event |
| `session_id` | Session identifier |
| `feature_name` | Feature associated with the event, if applicable |

### Example event names
- `signup_completed`
- `email_verified`
- `workspace_created`
- `invited_teammate`
- `first_report_created`
- `dashboard_viewed`
- `integration_connected`
- `login`

## subscriptions
This table contains trial and conversion information.

| Column | Description |
|---|---|
| `user_id` | Unique identifier for each user |
| `trial_start_date` | Date the trial started |
| `trial_end_date` | Date the trial ended |
| `converted_to_paid` | Flag indicating whether the user converted to paid |
| `conversion_date` | Date of paid conversion |
| `monthly_revenue` | Monthly recurring revenue associated with the converted user |

## marketing_spend
This table contains channel-level spend and campaign information.

| Column | Description |
|---|---|
| `acquisition_channel` | Marketing channel |
| `month` | Reporting month |
| `spend` | Total spend for the period |
| `campaign_type` | Campaign grouping or type |

## KPI Definitions

| KPI | Definition |
|---|---|
| `Signups` | Total users who completed signup in a selected period |
| `Activated Users` | Users who completed both `workspace_created` and `first_report_created` within 7 days of signup |
| `Activation Rate` | Activated Users divided by Signups |
| `Median Time to Activate` | Median number of days between signup and activation |
| `Day 7 Retention` | Percentage of users active on day 7 after signup |
| `Day 30 Retention` | Percentage of users active on day 30 after signup |
| `Trial-to-Paid Conversion` | Percentage of trial users who converted to paid |
| `Feature Adoption Rate` | Percentage of users who used a feature at least once |
| `MAU` | Distinct active users in a given month |
| `Churn Proxy` | Users with no recorded activity for 30 or more days |
