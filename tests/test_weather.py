import pytest
import requests

from app import weather
from app.weather import WeatherError, fetch_weather, parse_weather
from tests.conftest import FakeResponse, owm_payload


def test_parse_weather_extracts_fields():
    result = parse_weather(owm_payload(21.5, "Udupi", "light rain"))
    assert result == {"city": "Udupi", "temperature_c": 21.5, "description": "light rain"}


@pytest.mark.parametrize("bad", [{}, {"name": "X"}, {"name": "X", "main": {}, "weather": []}, None])
def test_parse_weather_rejects_malformed_data(bad):
    with pytest.raises(WeatherError):
        parse_weather(bad)


def test_fetch_weather_success(monkeypatch):
    monkeypatch.setattr(weather.requests, "get", lambda *a, **k: FakeResponse(200, owm_payload(12.0)))
    assert fetch_weather("Manipal", "key")["temperature_c"] == 12.0


def test_fetch_weather_non_200(monkeypatch):
    monkeypatch.setattr(weather.requests, "get", lambda *a, **k: FakeResponse(401, {}))
    with pytest.raises(WeatherError):
        fetch_weather("Manipal", "key")


def test_fetch_weather_network_error(monkeypatch):
    def boom(*a, **k):
        raise requests.ConnectionError("down")
    monkeypatch.setattr(weather.requests, "get", boom)
    with pytest.raises(WeatherError):
        fetch_weather("Manipal", "key")


def test_fetch_weather_requires_api_key():
    with pytest.raises(WeatherError):
        fetch_weather("Manipal", "")
