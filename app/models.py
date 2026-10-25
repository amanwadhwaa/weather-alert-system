from datetime import datetime, timezone, timedelta

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options={"expire_on_commit": False})

IST = timezone(timedelta(hours=5, minutes=30))


def utcnow():
    """Naive UTC timestamp (works the same on SQLite and PostgreSQL)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    temperature_c = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), default="")
    recorded_at = db.Column(db.DateTime, default=utcnow, index=True)
    alert_sent = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def recorded_at_ist(self):
        if self.recorded_at is None:
            return None
        return self.recorded_at.replace(tzinfo=timezone.utc).astimezone(IST)

    def to_dict(self):
        return {
            "id": self.id,
            "city": self.city,
            "temperature_c": self.temperature_c,
            "description": self.description,
            "recorded_at": self.recorded_at.isoformat() + "Z",
            "recorded_at_ist": self.recorded_at_ist.strftime("%Y-%m-%d %H:%M:%S IST") if self.recorded_at else None,
            "alert_sent": self.alert_sent,
        }
