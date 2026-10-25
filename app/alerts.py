from datetime import timedelta

import requests

POSTMARK_URL = "https://api.postmarkapp.com/email"


class AlertError(Exception):
    """Raised when an alert email cannot be sent."""


def should_alert(temperature_c, threshold_c):
    """True only when the temperature is strictly below the threshold."""
    return temperature_c < threshold_c


def in_cooldown(last_alert_at, now, cooldown_minutes):
    """True if an alert was already sent within the cooldown window."""
    if last_alert_at is None:
        return False
    return now - last_alert_at < timedelta(minutes=cooldown_minutes)


def build_alert_message(city, temperature_c, threshold_c):
    subject = f"Cold alert: {city} is {temperature_c:.1f}°C"
    body = (
        f"The temperature in {city} has dropped to {temperature_c:.1f}°C, "
        f"below your threshold of {threshold_c:.1f}°C."
    )
    return subject, body


def send_email(server_token, from_email, to_email, subject, body, timeout=10):
    """Send an email through the Postmark REST API."""
    if not (server_token and from_email and to_email):
        raise AlertError("Email settings are not fully configured")
    payload = {
        "From": from_email,
        "To": to_email,
        "Subject": subject,
        "TextBody": body,
    }
    try:
        resp = requests.post(
            POSTMARK_URL,
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Postmark-Server-Token": server_token,
            },
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise AlertError(f"Postmark request failed: {exc}") from exc

    if resp.status_code != 200:
        msg = ""
        try:
            msg = resp.json().get("Message", "")
        except Exception:
            msg = getattr(resp, "text", "")
        raise AlertError(f"Postmark error ({resp.status_code}): {msg}" if msg else f"Postmark returned status {resp.status_code}")
