# Ireland Weather Dashboard

## User Story
As a user in Ireland, I want to view current weather and 5-day forecasts for any county, so that I can plan around weather conditions.

## Acceptance Criteria
- [x] County dropdown (all 26 Republic of Ireland counties)
- [x] Current conditions: temperature, feels-like, humidity, wind, pressure, weather icon
- [x] 5-day hourly forecast chart with tab switching (Temperature / Rainfall / Wind)
- [x] Geolocation ("Use My Location") with IP fallback, snaps to nearest county
- [x] Date range selection (From/To, up to 16 days) with preset buttons (3D/5D/7D/14D)
- [x] "Last Updated" timestamp
- [x] Responsive (640px, 380px breakpoints), accessible, loading/error states

## Stack
- **Backend:** FastAPI + httpx (proxies Open-Meteo API + ipapi.co)
- **Frontend:** Vanilla JS + Chart.js 4.4.7 (CDN)
- **No API keys needed** -- Open-Meteo and ipapi.co are free

## Architecture Notes
- Proxy pattern: frontend never calls external APIs directly
- Geolocation cascade: native GPS -> IP fallback -> nearest county snap
- Global state object + cached DOM refs shared across JS modules
- Chart.js instance created/destroyed per render (prevents memory leaks)
- 3-hour interval sampling from hourly data for chart readability

## Design Notes
- CSS custom properties for theming, teal gradient header
- Components: sticky controls bar, error banner (animated), prompt card, conditions card, metric tabs (pill style), chart container, loading overlay
- Responsive breakpoints: 640px (mobile), 380px (small mobile)

## How to Run
```bash
cd projects/ireland-weather-dashboard/repo
source venv/bin/activate
uvicorn main:app --reload
# Opens at http://127.0.0.1:8000
```

## Dependencies
**Python:** fastapi, uvicorn, httpx, python-dotenv
**JS (CDN):** Chart.js 4.4.7
**Test:** pytest, pytest-asyncio, httpx, respx
