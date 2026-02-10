"""API tests for GET /api/weather."""

import httpx
import pytest
import respx

from main import OPEN_METEO_URL

pytestmark = pytest.mark.asyncio

# Dublin coordinates for valid-request tests
DUBLIN_LAT = 53.3498
DUBLIN_LON = -6.2603

# Minimal realistic response from Open-Meteo
SAMPLE_WEATHER_RESPONSE = {
    "latitude": DUBLIN_LAT,
    "longitude": DUBLIN_LON,
    "current": {
        "temperature_2m": 12.5,
        "weather_code": 3,
        "wind_speed_10m": 15.2,
        "relative_humidity_2m": 78,
        "apparent_temperature": 10.1,
        "pressure_msl": 1013.0,
    },
    "hourly": {
        "time": ["2026-02-10T00:00", "2026-02-10T01:00"],
        "temperature_2m": [11.0, 10.5],
        "precipitation": [0.0, 0.2],
        "wind_speed_10m": [14.0, 13.5],
    },
}


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


class TestWeatherHappyPath:
    """GET /api/weather with valid coordinates and a mocked upstream."""

    @respx.mock
    async def test_returns_200_with_valid_coords(self, async_client):
        respx.get(OPEN_METEO_URL).mock(
            return_value=httpx.Response(200, json=SAMPLE_WEATHER_RESPONSE)
        )
        response = await async_client.get(
            "/api/weather", params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON}
        )
        assert response.status_code == 200

    @respx.mock
    async def test_response_contains_data_key(self, async_client):
        respx.get(OPEN_METEO_URL).mock(
            return_value=httpx.Response(200, json=SAMPLE_WEATHER_RESPONSE)
        )
        response = await async_client.get(
            "/api/weather", params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON}
        )
        body = response.json()
        assert "data" in body

    @respx.mock
    async def test_response_data_contains_current_weather(self, async_client):
        respx.get(OPEN_METEO_URL).mock(
            return_value=httpx.Response(200, json=SAMPLE_WEATHER_RESPONSE)
        )
        response = await async_client.get(
            "/api/weather", params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON}
        )
        data = response.json()["data"]
        assert "current" in data
        assert data["current"]["temperature_2m"] == 12.5

    @respx.mock
    async def test_response_data_contains_hourly_forecast(self, async_client):
        respx.get(OPEN_METEO_URL).mock(
            return_value=httpx.Response(200, json=SAMPLE_WEATHER_RESPONSE)
        )
        response = await async_client.get(
            "/api/weather", params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON}
        )
        data = response.json()["data"]
        assert "hourly" in data
        assert "temperature_2m" in data["hourly"]


# ---------------------------------------------------------------------------
# Coordinate validation (400)
# ---------------------------------------------------------------------------


class TestWeatherValidation:
    """GET /api/weather rejects invalid coordinates with 400."""

    async def test_invalid_latitude_above_90_returns_400(self, async_client):
        response = await async_client.get(
            "/api/weather", params={"lat": 91.0, "lon": 0.0}
        )
        assert response.status_code == 400
        assert "Latitude" in response.json()["detail"]

    async def test_invalid_latitude_below_negative_90_returns_400(self, async_client):
        response = await async_client.get(
            "/api/weather", params={"lat": -91.0, "lon": 0.0}
        )
        assert response.status_code == 400
        assert "Latitude" in response.json()["detail"]

    async def test_invalid_longitude_above_180_returns_400(self, async_client):
        response = await async_client.get(
            "/api/weather", params={"lat": 0.0, "lon": 200.0}
        )
        assert response.status_code == 400
        assert "Longitude" in response.json()["detail"]

    async def test_invalid_longitude_below_negative_180_returns_400(self, async_client):
        response = await async_client.get(
            "/api/weather", params={"lat": 0.0, "lon": -181.0}
        )
        assert response.status_code == 400
        assert "Longitude" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Missing parameters (422)
# ---------------------------------------------------------------------------


class TestWeatherMissingParams:
    """GET /api/weather with missing query parameters returns 422."""

    async def test_missing_both_params_returns_422(self, async_client):
        response = await async_client.get("/api/weather")
        assert response.status_code == 422

    async def test_missing_lon_returns_422(self, async_client):
        response = await async_client.get(
            "/api/weather", params={"lat": DUBLIN_LAT}
        )
        assert response.status_code == 422

    async def test_missing_lat_returns_422(self, async_client):
        response = await async_client.get(
            "/api/weather", params={"lon": DUBLIN_LON}
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Upstream errors
# ---------------------------------------------------------------------------


class TestWeatherUpstreamErrors:
    """GET /api/weather handles upstream Open-Meteo failures gracefully."""

    @respx.mock
    async def test_upstream_timeout_returns_504(self, async_client):
        respx.get(OPEN_METEO_URL).mock(side_effect=httpx.ReadTimeout("timed out"))
        response = await async_client.get(
            "/api/weather", params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON}
        )
        assert response.status_code == 504
        assert "timed out" in response.json()["detail"].lower()

    @respx.mock
    async def test_upstream_connection_error_returns_502(self, async_client):
        respx.get(OPEN_METEO_URL).mock(
            side_effect=httpx.ConnectError("connection refused")
        )
        response = await async_client.get(
            "/api/weather", params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON}
        )
        assert response.status_code == 502
        assert "Could not reach weather service" in response.json()["detail"]

    @respx.mock
    async def test_upstream_500_returns_500(self, async_client):
        respx.get(OPEN_METEO_URL).mock(
            return_value=httpx.Response(500, json={"error": "internal"})
        )
        response = await async_client.get(
            "/api/weather", params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON}
        )
        assert response.status_code == 500
        assert "Weather API returned an error" in response.json()["detail"]

    @respx.mock
    async def test_upstream_429_returns_429(self, async_client):
        respx.get(OPEN_METEO_URL).mock(
            return_value=httpx.Response(429, json={"error": "rate limited"})
        )
        response = await async_client.get(
            "/api/weather", params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON}
        )
        assert response.status_code == 429

    @respx.mock
    async def test_upstream_503_returns_503(self, async_client):
        respx.get(OPEN_METEO_URL).mock(
            return_value=httpx.Response(503, json={"error": "service unavailable"})
        )
        response = await async_client.get(
            "/api/weather", params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON}
        )
        assert response.status_code == 503
