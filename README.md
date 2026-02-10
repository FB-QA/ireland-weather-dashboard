# Ireland Weather Dashboard

A lightweight web app that displays weather data for Irish counties, visualised with interactive charts.

## Features

- View current weather conditions for any of the 26 Republic of Ireland counties
- 5-day forecast visualised as interactive charts (temperature, rainfall, wind speed)
- Use browser geolocation or select a county from a searchable dropdown
- Responsive design that works on desktop and mobile

## Prerequisites

- Python 3.9+

## Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd output/dev/ireland-weather-dashboard
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   uvicorn main:app --reload
   ```

5. **Open your browser:**
   Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000)

> **Note:** No API key or `.env` file is needed — the app uses [Open-Meteo](https://open-meteo.com/), which is free and requires no authentication.

## Tech Stack

- **Backend:** Python / FastAPI
- **Frontend:** HTML, CSS, JavaScript (no framework, no build step)
- **Charts:** Chart.js (loaded via CDN)
- **Weather API:** Open-Meteo (free, no key required)

## Project Structure

```
ireland-weather-dashboard/
  main.py                # FastAPI app - API routes + static file serving
  requirements.txt       # Python dependencies
  .env.example           # Environment variable template
  static/
    index.html           # Main page
    css/
      style.css          # Styles
    js/
      app.js             # Main application logic
      chart-config.js    # Chart.js configuration and rendering
      counties.js        # County data for the dropdown
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serves the frontend |
| GET | `/api/counties` | Returns list of counties with coordinates |
| GET | `/api/weather/current?lat=...&lon=...` | Current weather for coordinates |
| GET | `/api/weather/forecast?lat=...&lon=...` | 5-day/3-hour forecast for coordinates |
