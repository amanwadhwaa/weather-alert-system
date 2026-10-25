import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def load_config():
    """Read configuration from environment variables."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///weather.db")
    # Render/Heroku style URLs use the legacy "postgres://" scheme
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return {
        "SQLALCHEMY_DATABASE_URI": db_url,
        "WEATHER_API_KEY": os.getenv("WEATHER_API_KEY", ""),
        "POSTMARK_SERVER_TOKEN": os.getenv(
            "POSTMARK_SERVER_TOKEN",
            os.getenv("POSTMARK_API_KEY", os.getenv("SENDGRID_API_KEY", "")),
        ),
        "ALERT_FROM_EMAIL": os.getenv("ALERT_FROM_EMAIL", ""),
        "ALERT_TO_EMAIL": os.getenv("ALERT_TO_EMAIL", ""),
        "CITY": os.getenv("CITY", "Manipal"),
        "TEMP_THRESHOLD_C": float(os.getenv("TEMP_THRESHOLD_C", "15")),
        "CHECK_INTERVAL_MINUTES": int(os.getenv("CHECK_INTERVAL_MINUTES", "30")),
        "ALERT_COOLDOWN_MINUTES": int(os.getenv("ALERT_COOLDOWN_MINUTES", "180")),
        "SCHEDULER_ENABLED": os.getenv("SCHEDULER_ENABLED", "true").lower() == "true",
    }
