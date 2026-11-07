// US EPA AQI categories (https://www.airnow.gov/aqi/aqi-basics/)
export const BANDS = [
  { max: 50, key: 'good', label: 'Good', color: '#4ade80' },
  { max: 100, key: 'moderate', label: 'Moderate', color: '#facc15' },
  { max: 150, key: 'usg', label: 'Unhealthy for sensitive groups', color: '#fb923c' },
  { max: 200, key: 'unhealthy', label: 'Unhealthy', color: '#f87171' },
  { max: 300, key: 'very', label: 'Very unhealthy', color: '#c084fc' },
  { max: Infinity, key: 'hazardous', label: 'Hazardous', color: '#e11d48' },
];
export const band = (aqi) => BANDS.find((b) => aqi <= b.max);

export const mean = (xs) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null);

/** Last `n` entries of a series, plus the mean of the n entries before them (for deltas). */
export function windowDelta(series, n, pick) {
  const cur = series.slice(-n).map(pick), prev = series.slice(-2 * n, -n).map(pick);
  const a = mean(cur), b = mean(prev);
  return { value: a, delta: a != null && b != null ? a - b : null };
}

/** City summary used by the ranking table. */
export function summarize(city) {
  const aq = windowDelta(city.air, 7, (d) => d.aqi);
  const t = windowDelta(city.weather, 7, (d) => (d.tmax + d.tmin) / 2);
  const rain = city.weather.slice(-30).reduce((s, d) => s + (d.rain ?? 0), 0);
  return { id: city.id, name: city.name, uf: city.uf, aqi: Math.round(aq.value), aqiDelta: aq.delta, temp: t.value, rain30: rain };
}
