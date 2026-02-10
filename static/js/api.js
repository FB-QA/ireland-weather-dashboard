/**
 * api.js — Backend API calls.
 *
 * All fetch requests to the FastAPI backend live here.
 * Each function returns parsed data or throws a descriptive error.
 */

async function fetchCounties() {
    const response = await fetch("/api/counties");
    if (!response.ok) {
        throw new Error("Failed to load county data.");
    }
    const json = await response.json();
    return json.data;
}

async function fetchGeolocation() {
    const response = await fetch("/api/geolocation");
    if (!response.ok) {
        throw new Error("Could not determine your location.");
    }
    const json = await response.json();
    return json.data;
}

async function fetchWeather(lat, lon, dateRange) {
    let url = `/api/weather?lat=${lat}&lon=${lon}`;
    if (dateRange) {
        url += `&start_date=${dateRange.start}&end_date=${dateRange.end}`;
    }
    const response = await fetch(url);
    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to fetch weather data.");
    }
    const json = await response.json();
    return json.data;
}
