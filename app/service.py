import logging

from .alerts import (AlertError, build_alert_message, in_cooldown,
                     send_email, should_alert)
from .models import Reading, db, utcnow
from .weather import WeatherError, fetch_weather

log = logging.getLogger(__name__)


def run_check(app):
    """Fetch weather, store the reading, and send an alert if needed."""
    with app.app_context():
        cfg = app.config
        try:
            data = fetch_weather(cfg["CITY"], cfg["WEATHER_API_KEY"])
        except WeatherError as exc:
            log.error("Weather fetch failed: %s", exc)
            return None

        now = utcnow()
        reading = Reading(
            city=data["city"],
            temperature_c=data["temperature_c"],
            description=data["description"],
            recorded_at=now,
        )

        if should_alert(reading.temperature_c, cfg["TEMP_THRESHOLD_C"]):
            last = (
                Reading.query.filter_by(city=reading.city, alert_sent=True)
                .order_by(Reading.recorded_at.desc())
                .first()
            )
            last_at = last.recorded_at if last else None
            if not in_cooldown(last_at, now, cfg["ALERT_COOLDOWN_MINUTES"]):
                subject, body = build_alert_message(
                    reading.city, reading.temperature_c, cfg["TEMP_THRESHOLD_C"]
                )
                try:
                    send_email(
                        cfg["POSTMARK_SERVER_TOKEN"], cfg["ALERT_FROM_EMAIL"],
                        cfg["ALERT_TO_EMAIL"], subject, body,
                    )
                    reading.alert_sent = True
                except AlertError as exc:
                    log.error("Alert email failed: %s", exc)

        db.session.add(reading)
        db.session.commit()
        return reading
