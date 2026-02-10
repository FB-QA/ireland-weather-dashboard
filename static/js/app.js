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
// Data Loading
// ---------------------------------------------------------------------------

async function loadWeatherData(lat, lon, locationName) {
    hideError();
    showLoading();

    try {
        const weatherData = await fetchWeather(lat, lon);

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

function handleGeolocation() {
    if (!navigator.geolocation) {
        showError("Geolocation is not supported by your browser.");
        return;
    }

    hideError();
    showLoading();

    navigator.geolocation.getCurrentPosition(
        (position) => {
            hideLoading();
            const { latitude, longitude } = position.coords;
            dom.countySelect.value = "";
            loadWeatherData(latitude, longitude, "Your Location");
        },
        (error) => {
            hideLoading();
            const messages = {
                1: "Location access was denied. Please allow location access in your browser settings and try again, or select a county from the dropdown.",
                2: "Location unavailable. Please check that Location Services is enabled in your system settings and that your browser has location permission, then try again. Or select a county from the dropdown.",
                3: "Location request timed out. Please try again or select a county from the dropdown.",
            };
            showError(
                messages[error.code] ||
                    "Could not determine your location. Please select a county."
            );
        },
        {
            enableHighAccuracy: false,
            timeout: 10000,
            maximumAge: 300000,
        }
    );
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
}

// ---------------------------------------------------------------------------
// Initialisation
// ---------------------------------------------------------------------------

async function init() {
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
