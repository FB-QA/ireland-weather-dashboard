/**
 * weather-codes.js — WMO weather code descriptions and SVG icons.
 *
 * Maps Open-Meteo weather codes to human-readable descriptions
 * and inline SVG icons for the current conditions display.
 */

const WEATHER_CODES = {
    0: { description: "Clear sky", icon: "sun" },
    1: { description: "Mainly clear", icon: "sun" },
    2: { description: "Partly cloudy", icon: "cloud-sun" },
    3: { description: "Overcast", icon: "cloud" },
    45: { description: "Foggy", icon: "cloud" },
    48: { description: "Depositing rime fog", icon: "cloud" },
    51: { description: "Light drizzle", icon: "cloud-drizzle" },
    53: { description: "Moderate drizzle", icon: "cloud-drizzle" },
    55: { description: "Dense drizzle", icon: "cloud-drizzle" },
    56: { description: "Light freezing drizzle", icon: "cloud-drizzle" },
    57: { description: "Dense freezing drizzle", icon: "cloud-drizzle" },
    61: { description: "Slight rain", icon: "cloud-rain" },
    63: { description: "Moderate rain", icon: "cloud-rain" },
    65: { description: "Heavy rain", icon: "cloud-rain" },
    66: { description: "Light freezing rain", icon: "cloud-rain" },
    67: { description: "Heavy freezing rain", icon: "cloud-rain" },
    71: { description: "Slight snow fall", icon: "cloud-snow" },
    73: { description: "Moderate snow fall", icon: "cloud-snow" },
    75: { description: "Heavy snow fall", icon: "cloud-snow" },
    77: { description: "Snow grains", icon: "cloud-snow" },
    80: { description: "Slight rain showers", icon: "cloud-rain" },
    81: { description: "Moderate rain showers", icon: "cloud-rain" },
    82: { description: "Violent rain showers", icon: "cloud-rain" },
    85: { description: "Slight snow showers", icon: "cloud-snow" },
    86: { description: "Heavy snow showers", icon: "cloud-snow" },
    95: { description: "Thunderstorm", icon: "cloud-lightning" },
    96: { description: "Thunderstorm with slight hail", icon: "cloud-lightning" },
    99: { description: "Thunderstorm with heavy hail", icon: "cloud-lightning" },
};

const WEATHER_ICONS = {
    sun: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="64" height="64"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`,
    "cloud-sun": `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="64" height="64"><path d="M12 2v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="M20 12h2"/><path d="m19.07 4.93-1.41 1.41"/><path d="M15.947 12.65a4 4 0 0 0-5.925-4.128"/><path d="M13 22H7a5 5 0 1 1 4.9-6H13a3 3 0 0 1 0 6Z"/></svg>`,
    cloud: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="64" height="64"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/></svg>`,
    "cloud-drizzle": `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="64" height="64"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M8 19v1"/><path d="M8 14v1"/><path d="M16 19v1"/><path d="M16 14v1"/><path d="M12 21v1"/><path d="M12 16v1"/></svg>`,
    "cloud-rain": `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="64" height="64"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M16 14v6"/><path d="M8 14v6"/><path d="M12 16v6"/></svg>`,
    "cloud-snow": `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="64" height="64"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M8 15h.01"/><path d="M8 19h.01"/><path d="M12 17h.01"/><path d="M12 21h.01"/><path d="M16 15h.01"/><path d="M16 19h.01"/></svg>`,
    "cloud-lightning": `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="64" height="64"><path d="M6 16.326A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 .5 8.973"/><path d="m13 12-3 5h4l-3 5"/></svg>`,
};

/**
 * Look up weather description and icon SVG for a WMO weather code.
 * Returns { description, iconSvg }.
 */
function getWeatherInfo(code) {
    const info = WEATHER_CODES[code] || { description: "Unknown", icon: "cloud" };
    const iconSvg = WEATHER_ICONS[info.icon] || WEATHER_ICONS["cloud"];
    return { description: info.description, iconSvg };
}
