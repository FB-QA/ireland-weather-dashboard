/**
 * state.js — Application state and DOM references.
 *
 * Centralised state object and cached DOM element references
 * used across all modules.
 */

const state = {
    counties: [],
    weatherData: null,
    activeMetric: "temperature",
    selectedLocation: null,
    dateRange: null,
};

const dom = {
    countySelect: document.getElementById("county-select"),
    geoButton: document.getElementById("geo-button"),
    metricTabs: document.querySelectorAll(".metric-tab"),
    currentSection: document.getElementById("current-conditions"),
    chartSection: document.getElementById("chart-section"),
    chartCanvas: document.getElementById("weather-chart"),
    loadingOverlay: document.getElementById("loading-overlay"),
    errorBanner: document.getElementById("error-banner"),
    errorMessage: document.getElementById("error-message"),
    errorDismiss: document.getElementById("error-dismiss"),
    locationLabel: document.getElementById("location-label"),
    promptMessage: document.getElementById("prompt-message"),
    startDateInput: document.getElementById("start-date"),
    endDateInput: document.getElementById("end-date"),
    rangeBtns: document.querySelectorAll(".range-btn"),
    lastUpdated: document.getElementById("last-updated"),
};
