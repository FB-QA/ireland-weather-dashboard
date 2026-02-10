/**
 * app.js — Application orchestrator.
 *
 * Wires everything together: initialisation, event binding,
 * data loading, and geolocation. All rendering, API calls,
 * state, and data are handled by their respective modules.
 *
 * Load order (all via <script> tags):
 *   counties.js → weather-codes.js → state.js → api.js →
 *   chart-config.js → ui.js → app.js
 */

// ---------------------------------------------------------------------------
// Date Range Helpers
// ---------------------------------------------------------------------------

function toISODate(d) {
    return d.toISOString().split("T")[0];
}

function initDateInputs() {
    const today = new Date();
    const maxDate = new Date(today);
    maxDate.setDate(maxDate.getDate() + 16);

    const defaultEnd = new Date(today);
    defaultEnd.setDate(defaultEnd.getDate() + 5);

    const minStr = toISODate(today);
    const maxStr = toISODate(maxDate);

    dom.startDateInput.min = minStr;
    dom.startDateInput.max = maxStr;
    dom.startDateInput.value = minStr;

    dom.endDateInput.min = minStr;
    dom.endDateInput.max = maxStr;
    dom.endDateInput.value = toISODate(defaultEnd);

    state.dateRange = { start: minStr, end: toISODate(defaultEnd) };
}

function handleDateChange() {
    let start = dom.startDateInput.value;
    let end = dom.endDateInput.value;

    // Auto-swap if start > end
    if (start && end && start > end) {
        [start, end] = [end, start];
        dom.startDateInput.value = start;
        dom.endDateInput.value = end;
    }

    if (start && end) {
        state.dateRange = { start, end };
        if (state.selectedLocation) {
            const { lat, lon, name } = state.selectedLocation;
            loadWeatherData(lat, lon, name);
        }
    }
}

// ---------------------------------------------------------------------------
// Data Loading
// ---------------------------------------------------------------------------

async function loadWeatherData(lat, lon, locationName) {
    hideError();
    showLoading();

    try {
        const weatherData = await fetchWeather(lat, lon, state.dateRange);

        state.weatherData = weatherData;
        state.selectedLocation = { lat, lon, name: locationName };

        dom.locationLabel.textContent = locationName;

        renderCurrentConditions(weatherData.current);
        renderChart(weatherData.hourly, state.activeMetric);
        showWeatherUI();
    } catch (error) {
        console.error("Error loading weather data:", error);
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// ---------------------------------------------------------------------------
// Geolocation
// ---------------------------------------------------------------------------

/**
 * Find the nearest county to the given coordinates using Euclidean distance.
 * Accurate enough for Ireland-scale distances.
 */
function findNearestCounty(lat, lon) {
    let nearest = null;
    let minDist = Infinity;
    for (const county of state.counties) {
        const dist = Math.pow(county.lat - lat, 2) + Math.pow(county.lon - lon, 2);
        if (dist < minDist) {
            minDist = dist;
            nearest = county;
        }
    }
    return nearest;
}

async function handleGeolocation() {
    if (!navigator.geolocation) {
        // No native geolocation support — go straight to IP fallback
        await fallbackToIPGeolocation();
        return;
    }

    hideError();
    showLoading();

    navigator.geolocation.getCurrentPosition(
        (position) => {
            // Native geolocation succeeded — snap to nearest county
            hideLoading();
            const { latitude, longitude } = position.coords;
            const county = findNearestCounty(latitude, longitude);
            if (county) {
                dom.countySelect.value = county.name;
                loadWeatherData(county.lat, county.lon, county.name);
            } else {
                dom.countySelect.value = "";
                loadWeatherData(latitude, longitude, "Your Location");
            }
        },
        async (error) => {
            // Native geolocation failed — try IP fallback silently
            console.warn("Native geolocation failed, trying IP fallback:", error.message);
            await fallbackToIPGeolocation();
        },
        {
            enableHighAccuracy: false,
            timeout: 10000,
            maximumAge: 300000,
        }
    );
}

async function fallbackToIPGeolocation() {
    hideError();
    showLoading();
    try {
        const geo = await fetchGeolocation();
        const county = findNearestCounty(geo.lat, geo.lon);
        if (county) {
            dom.countySelect.value = county.name;
            loadWeatherData(county.lat, county.lon, county.name);
        } else {
            loadWeatherData(geo.lat, geo.lon, geo.city || "Your Location");
        }
    } catch (err) {
        hideLoading();
        showError("Could not determine your location. Please select a county from the dropdown.");
    }
}

// ---------------------------------------------------------------------------
// Event Binding
// ---------------------------------------------------------------------------

function bindEvents() {
    dom.countySelect.addEventListener("change", (e) => {
        const countyName = e.target.value;
        if (!countyName) return;

        const county = state.counties.find((c) => c.name === countyName);
        if (county) {
            loadWeatherData(county.lat, county.lon, county.name);
        }
    });

    dom.geoButton.addEventListener("click", handleGeolocation);

    dom.metricTabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            setActiveMetricTab(tab.dataset.metric);
        });

        tab.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                setActiveMetricTab(tab.dataset.metric);
            }
        });
    });

    dom.errorDismiss.addEventListener("click", hideError);

    dom.startDateInput.addEventListener("change", handleDateChange);
    dom.endDateInput.addEventListener("change", handleDateChange);
}

// ---------------------------------------------------------------------------
// Initialisation
// ---------------------------------------------------------------------------

async function init() {
    initDateInputs();
    bindEvents();

    try {
        state.counties = await fetchCounties();
        populateDropdown(state.counties);
    } catch (error) {
        console.error("Failed to load counties:", error);
        showError("Failed to load county data. Please refresh the page.");
    }

    showPrompt();
}

document.addEventListener("DOMContentLoaded", init);
