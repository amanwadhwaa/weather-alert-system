from datetime import datetime, timedelta

import pytest

from app import alerts
from app.alerts import (AlertError, build_alert_message, in_cooldown,
                        send_email, should_alert)
from tests.conftest import FakeResponse


def test_should_alert_below_threshold():
    assert should_alert(10.0, 15.0)


def test_should_not_alert_at_or_above_threshold():
    assert not should_alert(15.0, 15.0)
    assert not should_alert(20.0, 15.0)


def test_cooldown_logic():
    now = datetime(2026, 1, 1, 12, 0)
    assert not in_cooldown(None, now, 180)
    assert in_cooldown(now - timedelta(minutes=30), now, 180)
    assert not in_cooldown(now - timedelta(minutes=181), now, 180)


def test_build_alert_message_mentions_city_and_temp():
    subject, body = build_alert_message("Manipal", 9.46, 15.0)
    assert "Manipal" in subject and "9.5" in subject
    assert "15.0" in body


def test_send_email_success(monkeypatch):
    sent = {}

    def fake_post(url, json, headers, timeout):
        sent.update(url=url, json=json, headers=headers)
        return FakeResponse(200)

    monkeypatch.setattr(alerts.requests, "post", fake_post)
    send_email("key", "a@x.com", "b@x.com", "Subj", "Body")
    assert sent["headers"]["X-Postmark-Server-Token"] == "key"
    assert sent["json"]["From"] == "a@x.com"
    assert sent["json"]["To"] == "b@x.com"
    assert sent["json"]["Subject"] == "Subj"
    assert sent["json"]["TextBody"] == "Body"


def test_send_email_failure_status(monkeypatch):
    monkeypatch.setattr(alerts.requests, "post", lambda *a, **k: FakeResponse(401))
    with pytest.raises(AlertError):
        send_email("key", "a@x.com", "b@x.com", "S", "B")


def test_send_email_requires_configuration():
    with pytest.raises(AlertError):
        send_email("", "a@x.com", "b@x.com", "S", "B")
