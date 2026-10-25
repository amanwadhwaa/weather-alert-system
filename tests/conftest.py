import pytest

from app import create_app
from app.models import db


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WEATHER_API_KEY": "test-key",
        "POSTMARK_SERVER_TOKEN": "pm-token",
        "ALERT_FROM_EMAIL": "from@example.com",
        "ALERT_TO_EMAIL": "to@example.com",
        "CITY": "Manipal",
        "TEMP_THRESHOLD_C": 15.0,
        "ALERT_COOLDOWN_MINUTES": 180,
    })
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


def owm_payload(temp, name="Manipal", desc="clear sky"):
    return {"name": name, "main": {"temp": temp}, "weather": [{"description": desc}]}
