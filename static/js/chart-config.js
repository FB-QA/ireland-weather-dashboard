/**
 * chart-config.js — Chart.js configuration and rendering logic.
 *
 * Handles creation, updates, and destruction of the weather chart.
 * Open-Meteo returns hourly data as parallel arrays:
 *   { time: [...], temperature_2m: [...], precipitation: [...], wind_speed_10m: [...] }
 */

/** @type {Chart|null} */
let weatherChart = null;

/**
 * Metric-specific chart configuration.
 * dataKey is the property name in the Open-Meteo hourly response.
 */
const METRIC_CONFIG = {
    temperature: {
        label: "Temperature",
        unit: "\u00b0C",
        chartType: "line",
        borderColor: "#ef4444",
        backgroundColor: "rgba(239, 68, 68, 0.1)",
        pointBackgroundColor: "#ef4444",
        yAxisLabel: "Temperature (\u00b0C)",
        dataKey: "temperature_2m",
        tension: 0.3,
        fill: true,
    },
    rainfall: {
        label: "Rainfall",
        unit: "mm",
        chartType: "bar",
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59, 130, 246, 0.5)",
        pointBackgroundColor: "#3b82f6",
        yAxisLabel: "Rainfall (mm)",
        dataKey: "precipitation",
        tension: 0,
        fill: true,
    },
    wind: {
        label: "Wind Speed",
        unit: "km/h",
        chartType: "line",
        borderColor: "#10b981",
        backgroundColor: "rgba(16, 185, 129, 0.1)",
        pointBackgroundColor: "#10b981",
        yAxisLabel: "Wind Speed (km/h)",
        dataKey: "wind_speed_10m",
        tension: 0.3,
        fill: true,
    },
};

/**
 * Format an ISO timestamp to a readable label.
 * Shows "Mon 14:00" style for readability.
 */
function formatTimestamp(isoString) {
    const date = new Date(isoString);
    const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const day = days[date.getDay()];
    const hours = date.getHours().toString().padStart(2, "0");
    const mins = date.getMinutes().toString().padStart(2, "0");
    return `${day} ${hours}:${mins}`;
}

/**
 * Create or update the weather chart with hourly forecast data.
 *
 * @param {Object} hourlyData - Open-Meteo hourly object with parallel arrays
 * @param {string} metric - One of: "temperature", "rainfall", "wind"
 */
function renderChart(hourlyData, metric) {
    const config = METRIC_CONFIG[metric];
    if (!config) {
        console.error(`Unknown metric: ${metric}`);
        return;
    }

    // Open-Meteo returns hourly data — sample every 3 hours for readability
    const step = 3;
    const labels = [];
    const data = [];

    for (let i = 0; i < hourlyData.time.length; i += step) {
        labels.push(formatTimestamp(hourlyData.time[i]));
        data.push(hourlyData[config.dataKey][i]);
    }

    const canvas = document.getElementById("weather-chart");
    const ctx = canvas.getContext("2d");

    // Destroy previous chart instance to prevent memory leaks
    if (weatherChart) {
        weatherChart.destroy();
        weatherChart = null;
    }

    weatherChart = new Chart(ctx, {
        type: config.chartType,
        data: {
            labels: labels,
            datasets: [
                {
                    label: `${config.label} (${config.unit})`,
                    data: data,
                    borderColor: config.borderColor,
                    backgroundColor: config.backgroundColor,
                    pointBackgroundColor: config.pointBackgroundColor,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    borderWidth: 2,
                    tension: config.tension,
                    fill: config.fill,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 600,
                easing: "easeInOutQuart",
            },
            interaction: {
                intersect: false,
                mode: "index",
            },
            plugins: {
                legend: {
                    display: true,
                    position: "top",
                    labels: {
                        font: { size: 13, weight: "500" },
                        color: "#374151",
                        usePointStyle: true,
                        pointStyle: "circle",
                    },
                },
                tooltip: {
                    backgroundColor: "rgba(17, 24, 39, 0.9)",
                    titleFont: { size: 13 },
                    bodyFont: { size: 13 },
                    padding: 10,
                    cornerRadius: 8,
                    callbacks: {
                        label: function (context) {
                            return `${config.label}: ${context.parsed.y} ${config.unit}`;
                        },
                    },
                },
            },
            scales: {
                x: {
                    ticks: {
                        maxRotation: 45,
                        font: { size: 11 },
                        color: "#6b7280",
                        maxTicksLimit: 16,
                    },
                    grid: {
                        display: false,
                    },
                },
                y: {
                    title: {
                        display: true,
                        text: config.yAxisLabel,
                        font: { size: 13, weight: "500" },
                        color: "#374151",
                    },
                    ticks: {
                        font: { size: 11 },
                        color: "#6b7280",
                    },
                    grid: {
                        color: "rgba(107, 114, 128, 0.1)",
                    },
                    beginAtZero: metric === "rainfall",
                },
            },
        },
    });
}

/**
 * Destroy the chart (used when resetting the view).
 */
function destroyChart() {
    if (weatherChart) {
        weatherChart.destroy();
        weatherChart = null;
    }
}
