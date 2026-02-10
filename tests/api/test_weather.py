"""API tests for GET /api/weather."""

from datetime import date, timedelta

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


# ---------------------------------------------------------------------------
# Date range parameters
# ---------------------------------------------------------------------------


class TestWeatherDateRange:
    """GET /api/weather date range validation and happy paths."""

    # -- Helper dates (computed dynamically so tests never go stale) --------

    @staticmethod
    def _today():
        return date.today()

    @staticmethod
    def _fmt(d: date) -> str:
        return d.isoformat()

    # -- Happy paths --------------------------------------------------------

    @respx.mock
    async def test_valid_date_range_returns_200(self, async_client):
        """Valid start_date + end_date returns 200 and passes dates upstream."""
        today = self._today()
        sd = self._fmt(today)
        ed = self._fmt(today + timedelta(days=5))

        respx.get(OPEN_METEO_URL).mock(
            return_value=httpx.Response(200, json=SAMPLE_WEATHER_RESPONSE)
        )
        response = await async_client.get(
            "/api/weather",
            params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON, "start_date": sd, "end_date": ed},
        )
        assert response.status_code == 200
        assert "data" in response.json()

        # Verify the upstream request received start_date/end_date params
        upstream_request = respx.calls.last.request
        assert f"start_date={sd}" in str(upstream_request.url)
        assert f"end_date={ed}" in str(upstream_request.url)

    @respx.mock
    async def test_no_dates_defaults_to_forecast_days(self, async_client):
        """Omitting both dates falls back to forecast_days=5 (backward compat)."""
        respx.get(OPEN_METEO_URL).mock(
            return_value=httpx.Response(200, json=SAMPLE_WEATHER_RESPONSE)
        )
        response = await async_client.get(
            "/api/weather", params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON}
        )
        assert response.status_code == 200

        upstream_request = respx.calls.last.request
        assert "forecast_days=5" in str(upstream_request.url)
        assert "start_date" not in str(upstream_request.url)
        assert "end_date" not in str(upstream_request.url)

    # -- Boundary: start_date = today (minimum valid) -----------------------

    @respx.mock
    async def test_start_date_equals_today_returns_200(self, async_client):
        """start_date = today is the minimum valid value — should pass."""
        today = self._today()
        sd = self._fmt(today)
        ed = self._fmt(today + timedelta(days=3))

        respx.get(OPEN_METEO_URL).mock(
            return_value=httpx.Response(200, json=SAMPLE_WEATHER_RESPONSE)
        )
        response = await async_client.get(
            "/api/weather",
            params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON, "start_date": sd, "end_date": ed},
        )
        assert response.status_code == 200

    # -- Boundary: end_date = today + 16 (maximum valid) --------------------

    @respx.mock
    async def test_end_date_equals_today_plus_16_returns_200(self, async_client):
        """end_date = today + 16 days is the maximum valid value — should pass."""
        today = self._today()
        sd = self._fmt(today)
        ed = self._fmt(today + timedelta(days=16))

        respx.get(OPEN_METEO_URL).mock(
            return_value=httpx.Response(200, json=SAMPLE_WEATHER_RESPONSE)
        )
        response = await async_client.get(
            "/api/weather",
            params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON, "start_date": sd, "end_date": ed},
        )
        assert response.status_code == 200

    # -- Boundary: start_date = end_date (same day range) -------------------

    @respx.mock
    async def test_same_start_and_end_date_returns_200(self, async_client):
        """Single-day range (start_date == end_date) is valid."""
        today = self._today()
        d = self._fmt(today)

        respx.get(OPEN_METEO_URL).mock(
            return_value=httpx.Response(200, json=SAMPLE_WEATHER_RESPONSE)
        )
        response = await async_client.get(
            "/api/weather",
            params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON, "start_date": d, "end_date": d},
        )
        assert response.status_code == 200

    # -- Validation: only start_date provided -------------------------------

    async def test_only_start_date_returns_400(self, async_client):
        """Providing start_date without end_date is rejected."""
        sd = self._fmt(self._today())
        response = await async_client.get(
            "/api/weather",
            params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON, "start_date": sd},
        )
        assert response.status_code == 400
        assert "Both start_date and end_date are required" in response.json()["detail"]

    # -- Validation: only end_date provided ---------------------------------

    async def test_only_end_date_returns_400(self, async_client):
        """Providing end_date without start_date is rejected."""
        ed = self._fmt(self._today() + timedelta(days=3))
        response = await async_client.get(
            "/api/weather",
            params={"lat": DUBLIN_LAT, "lon": DUBLIN_LON, "end_date": ed},
        )
        assert response.status_code == 400
        assert "Both start_date and end_date are required" in response.json()["detail"]

    # -- Validation: invalid date format ------------------------------------

    async def test_invalid_date_format_returns_400(self, async_client):
        """Non-ISO date strings are rejected."""
        response = await async_client.get(
            "/api/weather",
            params={
                "lat": DUBLIN_LAT,
                "lon": DUBLIN_LON,
                "start_date": "10-02-2026",
                "end_date": "15-02-2026",
            },
        )
        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]

    # -- Validation: start_date in the past ---------------------------------

    async def test_start_date_in_past_returns_400(self, async_client):
        """start_date before today is rejected."""
        yesterday = self._fmt(self._today() - timedelta(days=1))
        ed = self._fmt(self._today() + timedelta(days=3))
        response = await async_client.get(
            "/api/weather",
            params={
                "lat": DUBLIN_LAT,
                "lon": DUBLIN_LON,
                "start_date": yesterday,
                "end_date": ed,
            },
        )
        assert response.status_code == 400
        assert "start_date cannot be in the past" in response.json()["detail"]

    # -- Validation: end_date beyond 16 days --------------------------------

    async def test_end_date_beyond_16_days_returns_400(self, async_client):
        """end_date more than 16 days from today is rejected."""
        sd = self._fmt(self._today())
        too_far = self._fmt(self._today() + timedelta(days=17))
        response = await async_client.get(
            "/api/weather",
            params={
                "lat": DUBLIN_LAT,
                "lon": DUBLIN_LON,
                "start_date": sd,
                "end_date": too_far,
            },
        )
        assert response.status_code == 400
        assert "end_date cannot be more than 16 days from today" in response.json()["detail"]

    # -- Validation: start_date after end_date ------------------------------

    async def test_start_date_after_end_date_returns_400(self, async_client):
        """start_date > end_date is rejected."""
        today = self._today()
        sd = self._fmt(today + timedelta(days=5))
        ed = self._fmt(today + timedelta(days=2))
        response = await async_client.get(
            "/api/weather",
            params={
                "lat": DUBLIN_LAT,
                "lon": DUBLIN_LON,
                "start_date": sd,
                "end_date": ed,
            },
        )
        assert response.status_code == 400
        assert "start_date must be on or before end_date" in response.json()["detail"]
