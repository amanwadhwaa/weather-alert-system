from app.models import Reading, db


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_api_readings_empty(client):
    assert client.get("/api/readings").get_json() == []


def test_api_readings_returns_latest_first(app, client):
    with app.app_context():
        db.session.add(Reading(city="Manipal", temperature_c=10.0, description="mist"))
        db.session.add(Reading(city="Manipal", temperature_c=12.0, description="clear"))
        db.session.commit()
    data = client.get("/api/readings").get_json()
    assert len(data) == 2
    assert {"city", "temperature_c", "alert_sent", "recorded_at"} <= set(data[0])


def test_dashboard_renders_empty_and_populated(app, client):
    assert b"No readings yet" in client.get("/").data
    with app.app_context():
        db.session.add(Reading(city="Manipal", temperature_c=9.0, description="mist"))
        db.session.commit()
    page = client.get("/")
    assert page.status_code == 200
    assert b"9.0" in page.data
    assert b"Check Weather Now" in page.data


def test_check_now_redirects(client, monkeypatch):
    from app import weather
    from tests.conftest import FakeResponse, owm_payload
    monkeypatch.setattr(weather.requests, "get", lambda *a, **k: FakeResponse(200, owm_payload(22.0)))

    resp = client.post("/check-now")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/"
