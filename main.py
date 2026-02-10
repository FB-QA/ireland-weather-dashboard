"""
Ireland Weather Dashboard — FastAPI Backend

Serves the frontend as static files and proxies Open-Meteo API calls.
No API key required.
"""

from datetime import date, timedelta
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
IP_GEOLOCATION_URL = "https://ipapi.co/json/"

# All 26 Republic of Ireland counties with approximate lat/lon coordinates
COUNTIES = [
    {"name": "Carlow", "lat": 52.8408, "lon": -6.9261},
    {"name": "Cavan", "lat": 53.9908, "lon": -7.3606},
    {"name": "Clare", "lat": 52.8419, "lon": -8.9833},
    {"name": "Cork", "lat": 51.8985, "lon": -8.4756},
    {"name": "Donegal", "lat": 54.6538, "lon": -8.1096},
    {"name": "Dublin", "lat": 53.3498, "lon": -6.2603},
    {"name": "Galway", "lat": 53.2707, "lon": -9.0568},
    {"name": "Kerry", "lat": 52.0599, "lon": -9.8544},
    {"name": "Kildare", "lat": 53.2120, "lon": -6.8195},
    {"name": "Kilkenny", "lat": 52.6541, "lon": -7.2448},
    {"name": "Laois", "lat": 52.9943, "lon": -7.5444},
    {"name": "Leitrim", "lat": 54.1245, "lon": -8.0025},
    {"name": "Limerick", "lat": 52.6638, "lon": -8.6267},
    {"name": "Longford", "lat": 53.7276, "lon": -7.7933},
    {"name": "Louth", "lat": 53.9254, "lon": -6.4891},
    {"name": "Mayo", "lat": 53.7633, "lon": -9.5294},
    {"name": "Meath", "lat": 53.6055, "lon": -6.6564},
    {"name": "Monaghan", "lat": 54.2492, "lon": -6.9683},
    {"name": "Offaly", "lat": 53.2357, "lon": -7.7122},
    {"name": "Roscommon", "lat": 53.6318, "lon": -8.1867},
    {"name": "Sligo", "lat": 54.2766, "lon": -8.4761},
    {"name": "Tipperary", "lat": 52.4738, "lon": -8.1619},
    {"name": "Waterford", "lat": 52.2593, "lon": -7.1101},
    {"name": "Westmeath", "lat": 53.5345, "lon": -7.4653},
    {"name": "Wexford", "lat": 52.3369, "lon": -6.4633},
    {"name": "Wicklow", "lat": 52.9808, "lon": -6.0446},
]

app = FastAPI(title="Ireland Weather Dashboard")


def _validate_coordinates(lat: float, lon: float) -> None:
    """Raise an HTTP 400 if coordinates are outside valid range."""
    if not (-90 <= lat <= 90):
        raise HTTPException(
            status_code=400,
            detail=f"Latitude must be between -90 and 90, got {lat}",
        )
    if not (-180 <= lon <= 180):
        raise HTTPException(
            status_code=400,
            detail=f"Longitude must be between -180 and 180, got {lon}",
        )


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------


@app.get("/api/counties")
async def get_counties():
    """Return all 26 Irish counties with their coordinates."""
    return {"data": COUNTIES}


@app.get("/api/weather")
async def get_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
):
    """
    Fetch current conditions and hourly forecast from Open-Meteo.
    Accepts optional start_date/end_date for custom date ranges (up to 16 days).
    If omitted, defaults to a 5-day forecast. No API key required.
    """
    _validate_coordinates(lat, lon)

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m,apparent_temperature,pressure_msl",
        "hourly": "temperature_2m,precipitation,wind_speed_10m",
        "timezone": "Europe/London",
    }

    if start_date or end_date:
        if not (start_date and end_date):
            raise HTTPException(
                status_code=400,
                detail="Both start_date and end_date are required when specifying a date range.",
            )
        try:
            sd = date.fromisoformat(start_date)
            ed = date.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD.",
            )
        today = date.today()
        max_date = today + timedelta(days=16)
        if sd < today:
            raise HTTPException(status_code=400, detail="start_date cannot be in the past.")
        if ed > max_date:
            raise HTTPException(status_code=400, detail="end_date cannot be more than 16 days from today.")
        if sd > ed:
            raise HTTPException(status_code=400, detail="start_date must be on or before end_date.")
        params["start_date"] = start_date
        params["end_date"] = end_date
    else:
        params["forecast_days"] = 5

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(OPEN_METEO_URL, params=params)
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Weather service request timed out. Please try again.",
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Could not reach weather service: {exc}",
            )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Weather API returned an error. Please try again.",
        )

    return {"data": response.json()}


@app.get("/api/geolocation")
async def get_geolocation():
    """
    Return approximate lat/lon from the caller's IP address.

    Uses ipapi.co (free tier, no key required) as a proxy so the frontend
    never contacts external services directly.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(IP_GEOLOCATION_URL)
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Geolocation service request timed out. Please try again.",
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Could not reach geolocation service: {exc}",
            )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Geolocation service returned an error. Please try again.",
        )

    payload = response.json()

    # ipapi.co returns an "error" field when the request is rate-limited or
    # the IP cannot be resolved.
    if payload.get("error"):
        raise HTTPException(
            status_code=503,
            detail=payload.get("reason", "Geolocation lookup failed."),
        )

    return {
        "data": {
            "lat": payload.get("latitude"),
            "lon": payload.get("longitude"),
            "city": payload.get("city"),
            "country": payload.get("country_name"),
        }
    }


# ---------------------------------------------------------------------------
# Static Files & SPA Fallback
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def serve_index():
    """Serve the main HTML page."""
    return FileResponse("static/index.html")
