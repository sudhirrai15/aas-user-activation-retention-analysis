DROP TABLE IF EXISTS marketing_spend;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INT PRIMARY KEY,
    signup_date DATE NOT NULL,
    country VARCHAR(50),
    region VARCHAR(50),
    device_type VARCHAR(20),
    acquisition_channel VARCHAR(50),
    plan_type VARCHAR(20),
    company_size VARCHAR(20),
    industry VARCHAR(50)
);

CREATE TABLE events (
    event_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    event_date DATE NOT NULL,
    event_name VARCHAR(50) NOT NULL,
    session_id VARCHAR(50),
    feature_name VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE subscriptions (
    user_id INT PRIMARY KEY,
    trial_start_date DATE,
    trial_end_date DATE,
    converted_to_paid INT,
    conversion_date DATE,
    monthly_revenue NUMERIC(10,2),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE marketing_spend (
    acquisition_channel VARCHAR(50),
    month DATE,
    spend NUMERIC(12,2),
    campaign_type VARCHAR(50)
);
