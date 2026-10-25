from app import alerts, service, weather
from app.models import Reading, db
from tests.conftest import FakeResponse, owm_payload


def _patch(monkeypatch, temp, email_calls):
    monkeypatch.setattr(weather.requests, "get", lambda *a, **k: FakeResponse(200, owm_payload(temp)))

    def fake_post(*a, **k):
        email_calls.append(1)
        return FakeResponse(200)
    monkeypatch.setattr(alerts.requests, "post", fake_post)


def test_cold_reading_stores_and_sends_alert(app, monkeypatch):
    calls = []
    _patch(monkeypatch, 8.0, calls)
    reading = service.run_check(app)
    assert reading.alert_sent is True
    assert len(calls) == 1
    with app.app_context():
        assert Reading.query.count() == 1


def test_warm_reading_stores_without_alert(app, monkeypatch):
    calls = []
    _patch(monkeypatch, 25.0, calls)
    reading = service.run_check(app)
    assert reading.alert_sent is False
    assert calls == []


def test_cooldown_prevents_repeat_alerts(app, monkeypatch):
    calls = []
    _patch(monkeypatch, 8.0, calls)
    service.run_check(app)
    second = service.run_check(app)
    assert len(calls) == 1
    assert second.alert_sent is False


def test_weather_failure_returns_none(app, monkeypatch):
    monkeypatch.setattr(weather.requests, "get", lambda *a, **k: FakeResponse(500, {}))
    assert service.run_check(app) is None
    with app.app_context():
        assert Reading.query.count() == 0
