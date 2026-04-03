from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import random


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "sample"
SEED = 42
USER_COUNT = 2500
START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 6, 30)


CHANNELS = [
    ("Organic Search", 0.28),
    ("Referral", 0.16),
    ("Paid Search", 0.18),
    ("Paid Social", 0.18),
    ("Partner", 0.10),
    ("Email", 0.10),
]

COUNTRIES = [
    ("United States", "North America"),
    ("Canada", "North America"),
    ("United Kingdom", "EMEA"),
    ("Germany", "EMEA"),
    ("India", "APAC"),
    ("Australia", "APAC"),
]

DEVICE_TYPES = ["Desktop", "Mobile", "Tablet"]
PLAN_TYPES = ["trial", "free_trial"]
COMPANY_SIZES = ["SMB", "Mid-Market", "Enterprise"]
INDUSTRIES = ["SaaS", "Technology", "Retail", "Finance", "Healthcare", "Manufacturing"]
FEATURES = ["Reporting", "Dashboard", "Integration", "Automation", "Collaboration"]

ACTIVATION_LIFT = {
    "Organic Search": 0.10,
    "Referral": 0.18,
    "Paid Search": 0.02,
    "Paid Social": -0.08,
    "Partner": 0.06,
    "Email": 0.04,
}

RETENTION_LIFT = {
    "Organic Search": 0.08,
    "Referral": 0.15,
    "Paid Search": 0.01,
    "Paid Social": -0.07,
    "Partner": 0.05,
    "Email": 0.03,
}

COMPANY_SIZE_LIFT = {
    "SMB": -0.03,
    "Mid-Market": 0.04,
    "Enterprise": 0.08,
}

PLAN_LIFT = {
    "trial": 0.04,
    "free_trial": -0.01,
}


@dataclass
class UserRow:
    user_id: int
    signup_date: date
    country: str
    region: str
    device_type: str
    acquisition_channel: str
    plan_type: str
    company_size: str
    industry: str


def bounded_probability(value: float) -> float:
    return max(0.02, min(0.95, value))


def choose_weighted(options: list[tuple[str, float]]) -> str:
    labels, weights = zip(*options)
    return random.choices(labels, weights=weights, k=1)[0]


def generate_users() -> list[dict]:
    total_days = (END_DATE - START_DATE).days
    rows: list[UserRow] = []

    for user_id in range(1, USER_COUNT + 1):
        signup_date = START_DATE + timedelta(days=random.randint(0, total_days))
        country, region = random.choice(COUNTRIES)
        acquisition_channel = choose_weighted(CHANNELS)

        rows.append(
            UserRow(
                user_id=user_id,
                signup_date=signup_date,
                country=country,
                region=region,
                device_type=random.choices(DEVICE_TYPES, weights=[0.62, 0.33, 0.05], k=1)[0],
                acquisition_channel=acquisition_channel,
                plan_type=random.choices(PLAN_TYPES, weights=[0.68, 0.32], k=1)[0],
                company_size=random.choices(COMPANY_SIZES, weights=[0.46, 0.34, 0.20], k=1)[0],
                industry=random.choice(INDUSTRIES),
            )
        )

    return [row.__dict__ for row in rows]


def generate_events(users: list[dict]) -> list[dict]:
    event_rows: list[dict] = []
    event_id = 1

    for row in users:
        signup_date = row["signup_date"]
        session_number = 1

        def add_event(event_date: date, event_name: str, feature_name: str | None = None) -> None:
            nonlocal event_id, session_number
            event_rows.append(
                {
                    "event_id": event_id,
                    "user_id": row["user_id"],
                    "event_date": event_date.isoformat(),
                    "event_name": event_name,
                    "session_id": f"s{row['user_id']}_{session_number}",
                    "feature_name": feature_name,
                }
            )
            event_id += 1
            session_number += 1

        activation_prob = bounded_probability(
            0.48
            + ACTIVATION_LIFT[row["acquisition_channel"]]
            + COMPANY_SIZE_LIFT[row["company_size"]]
            + PLAN_LIFT[row["plan_type"]]
        )

        retention_prob = bounded_probability(
            0.28
            + RETENTION_LIFT[row["acquisition_channel"]]
            + 0.5 * COMPANY_SIZE_LIFT[row["company_size"]]
            + 0.5 * PLAN_LIFT[row["plan_type"]]
        )

        add_event(signup_date, "signup_completed")

        if random.random() < 0.93:
            add_event(signup_date + timedelta(days=random.randint(0, 2)), "email_verified")

        activated = random.random() < activation_prob
        used_features: set[str] = set()

        if activated:
            workspace_date = signup_date + timedelta(days=random.randint(0, 4))
            report_date = workspace_date + timedelta(days=random.randint(0, 2))
            add_event(workspace_date, "workspace_created")

            primary_feature = random.choice(FEATURES)
            used_features.add(primary_feature)
            add_event(report_date, "first_report_created", primary_feature)

            extra_feature_count = random.randint(1, 3)
            for _ in range(extra_feature_count):
                feature = random.choice(FEATURES)
                used_features.add(feature)
                add_event(
                    report_date + timedelta(days=random.randint(0, 10)),
                    random.choice(["dashboard_viewed", "integration_connected", "login"]),
                    feature,
                )

        if activated and random.random() < retention_prob:
            add_event(signup_date + timedelta(days=7), "login")
            if random.random() < bounded_probability(retention_prob + 0.10):
                for extra_offset in [14, 21, 30, 45]:
                    if random.random() < 0.75:
                        feature = random.choice(list(used_features) or FEATURES)
                        add_event(
                            signup_date + timedelta(days=extra_offset),
                            random.choice(["login", "dashboard_viewed", "integration_connected"]),
                            feature,
                        )
        elif activated and random.random() < 0.20:
            add_event(signup_date + timedelta(days=random.randint(8, 20)), "login")

    return event_rows


def generate_subscriptions(users: list[dict], events: list[dict]) -> list[dict]:
    activated_users = set(
        event["user_id"]
        for event in events
        if event["event_name"] in {"workspace_created", "first_report_created"}
    )
    user_signup_dates = {row["user_id"]: row["signup_date"] for row in users}
    retained_users = set()
    for event in events:
        if event["event_name"] != "login":
            continue
        user_id = event["user_id"]
        if date.fromisoformat(event["event_date"]) >= user_signup_dates[user_id] + timedelta(days=30):
            retained_users.add(user_id)

    rows: list[dict] = []
    for row in users:
        trial_start = row["signup_date"]
        trial_end = trial_start + timedelta(days=14)

        conversion_prob = bounded_probability(
            0.14
            + ACTIVATION_LIFT[row["acquisition_channel"]] * 0.8
            + COMPANY_SIZE_LIFT[row["company_size"]]
            + PLAN_LIFT[row["plan_type"]] * 0.5
            + (0.18 if row["user_id"] in activated_users else -0.08)
            + (0.12 if row["user_id"] in retained_users else 0.0)
        )

        converted = random.random() < conversion_prob
        if converted:
            conversion_date = trial_end + timedelta(days=random.randint(0, 5))
            base_revenue = {"SMB": 79, "Mid-Market": 199, "Enterprise": 499}[row["company_size"]]
            revenue = round(base_revenue + random.randint(-20, 60), 2)
        else:
            conversion_date = None
            revenue = ""

        rows.append(
            {
                "user_id": row["user_id"],
                "trial_start_date": trial_start.isoformat(),
                "trial_end_date": trial_end.isoformat(),
                "converted_to_paid": int(converted),
                "conversion_date": conversion_date.isoformat() if conversion_date else "",
                "monthly_revenue": revenue,
            }
        )

    return rows


def generate_marketing_spend() -> list[dict]:
    months = [date(2025, month, 1) for month in range(1, 7)]
    base_spend = {
        "Organic Search": 7000,
        "Referral": 3500,
        "Paid Search": 12000,
        "Paid Social": 15000,
        "Partner": 6000,
        "Email": 4500,
    }
    campaign_types = {
        "Organic Search": "SEO",
        "Referral": "Referral Program",
        "Paid Search": "Performance",
        "Paid Social": "Awareness",
        "Partner": "Partnerships",
        "Email": "Lifecycle",
    }

    rows: list[dict] = []
    for month in months:
        for channel, spend in base_spend.items():
            rows.append(
                {
                    "acquisition_channel": channel,
                    "month": month.isoformat(),
                    "spend": round(spend + random.randint(-1200, 1500), 2),
                    "campaign_type": campaign_types[channel],
                }
            )
    return rows


def build_load_sql() -> str:
    return """-- PostgreSQL example load commands
-- Update the absolute path if your local path differs.

\\copy users FROM 'data/sample/users.csv' DELIMITER ',' CSV HEADER;
\\copy events FROM 'data/sample/events.csv' DELIMITER ',' CSV HEADER;
\\copy subscriptions FROM 'data/sample/subscriptions.csv' DELIMITER ',' CSV HEADER;
\\copy marketing_spend FROM 'data/sample/marketing_spend.csv' DELIMITER ',' CSV HEADER;
"""


def main() -> None:
    random.seed(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    users = generate_users()
    events = generate_events(users)
    subscriptions = generate_subscriptions(users, events)
    marketing_spend = generate_marketing_spend()

    users = sorted(users, key=lambda row: (row["signup_date"], row["user_id"]))
    events = sorted(events, key=lambda row: (row["event_date"], row["user_id"], row["event_id"]))
    subscriptions = sorted(subscriptions, key=lambda row: row["user_id"])
    marketing_spend = sorted(marketing_spend, key=lambda row: (row["month"], row["acquisition_channel"]))

    def write_csv(path: Path, rows: list[dict]) -> None:
        if not rows:
            return
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    write_csv(OUTPUT_DIR / "users.csv", users)
    write_csv(OUTPUT_DIR / "events.csv", events)
    write_csv(OUTPUT_DIR / "subscriptions.csv", subscriptions)
    write_csv(OUTPUT_DIR / "marketing_spend.csv", marketing_spend)
    (OUTPUT_DIR / "load_postgres.sql").write_text(build_load_sql(), encoding="utf-8")

    print(f"Generated users: {len(users):,}")
    print(f"Generated events: {len(events):,}")
    print(f"Generated subscriptions: {len(subscriptions):,}")
    print(f"Generated marketing rows: {len(marketing_spend):,}")
    print(f"Files written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
