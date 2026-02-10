/**
 * ui.js — UI rendering and state management.
 *
 * Handles loading/error/prompt visibility, dropdown population,
 * current conditions rendering, and metric tab switching.
 */

// ---------------------------------------------------------------------------
// Visibility Helpers
// ---------------------------------------------------------------------------

function showLoading() {
    dom.loadingOverlay.classList.add("visible");
}

function hideLoading() {
    dom.loadingOverlay.classList.remove("visible");
}

function showError(message) {
    dom.errorMessage.textContent = message;
    dom.errorBanner.classList.add("visible");
}

function hideError() {
    dom.errorBanner.classList.remove("visible");
}

function showPrompt() {
    dom.promptMessage.classList.add("visible");
    dom.currentSection.classList.remove("visible");
    dom.chartSection.classList.remove("visible");
}

function showWeatherUI() {
    dom.promptMessage.classList.remove("visible");
    dom.currentSection.classList.add("visible");
    dom.chartSection.classList.add("visible");
}

// ---------------------------------------------------------------------------
// Dropdown
// ---------------------------------------------------------------------------

function populateDropdown(counties) {
    dom.countySelect.innerHTML =
        '<option value="">Select a county...</option>';

    counties.forEach((county) => {
        const option = document.createElement("option");
        option.value = county.name;
        option.textContent = county.name;
        dom.countySelect.appendChild(option);
    });
}

// ---------------------------------------------------------------------------
// Current Conditions
// ---------------------------------------------------------------------------

function renderCurrentConditions(current) {
    const { description, iconSvg } = getWeatherInfo(current.weather_code);

    dom.currentSection.innerHTML = `
        <div class="current-weather-card">
            <div class="current-main">
                <div class="weather-icon-svg" aria-hidden="true">
                    ${iconSvg}
                </div>
                <div class="current-temp">
                    <span class="temp-value">${Math.round(current.temperature_2m)}</span>
                    <span class="temp-unit">\u00b0C</span>
                </div>
                <p class="weather-desc">${description}</p>
            </div>
            <div class="current-details">
                <div class="detail-item">
                    <span class="detail-label">Feels Like</span>
                    <span class="detail-value">${Math.round(current.apparent_temperature)}\u00b0C</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Humidity</span>
                    <span class="detail-value">${current.relative_humidity_2m}%</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Wind</span>
                    <span class="detail-value">${current.wind_speed_10m} km/h</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Pressure</span>
                    <span class="detail-value">${Math.round(current.pressure_msl)} hPa</span>
                </div>
            </div>
        </div>
    `;
}

// ---------------------------------------------------------------------------
// Metric Tabs
// ---------------------------------------------------------------------------

function setActiveMetricTab(metric) {
    state.activeMetric = metric;

    dom.metricTabs.forEach((tab) => {
        tab.classList.toggle("active", tab.dataset.metric === metric);
        tab.setAttribute(
            "aria-selected",
            tab.dataset.metric === metric ? "true" : "false"
        );
    });

    if (state.weatherData) {
        renderChart(state.weatherData.hourly, metric);
    }
}
