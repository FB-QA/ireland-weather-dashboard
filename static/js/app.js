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
            // Native geolocation succeeded
            hideLoading();
            const { latitude, longitude } = position.coords;
            dom.countySelect.value = "";
            loadWeatherData(latitude, longitude, "Your Location");
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
        dom.countySelect.value = "";
        loadWeatherData(geo.lat, geo.lon, geo.city || "Your Location");
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
