<script>
  import Chart from './lib/Chart.svelte';
  import { BANDS, band, summarize } from './lib/aqi.js';

  let data = $state(null);
  let error = $state('');
  let sel = $state('curitiba');
  let sortKey = $state('aqi');
  let sortDir = $state(-1);

  fetch('./data.json').then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then((d) => (data = d)).catch((e) => (error = 'Could not load data (' + e.message + ')'));

  const city = $derived(data?.cities.find((c) => c.id === sel));
  const last = $derived(city?.air.at(-1));
  const lastW = $derived(city?.weather.at(-1));
  const b = $derived(last ? band(last.aqi) : null);
  const rows = $derived(data ? data.cities.map(summarize).sort((x, y) => (x[sortKey] > y[sortKey] ? 1 : -1) * sortDir) : []);
  const fmt = (v, d = 0) => (v == null ? '—' : v.toFixed(d));
  const short = (iso) => new Date(iso + 'T12:00').toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
  const sort = (k) => { if (sortKey === k) sortDir = -sortDir; else { sortKey = k; sortDir = k === 'name' ? 1 : -1; } };

  const grid = 'rgba(148,180,196,.12)', tick = '#8fa9b5';
  const base = { animation: false, responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false },
    plugins: { legend: { labels: { color: '#c9dbe3', boxWidth: 10, boxHeight: 10, usePointStyle: true } },
      tooltip: { backgroundColor: '#0d1b24', borderColor: '#2a4352', borderWidth: 1, padding: 10 } } };
  const axes = (extra = {}) => ({ x: { grid: { display: false }, ticks: { color: tick, maxTicksLimit: 7, maxRotation: 0 } },
    y: { grid: { color: grid }, ticks: { color: tick }, ...extra } });

  const aqiCfg = $derived(city && {
    type: 'line',
    data: { labels: city.air.map((d) => short(d.d)), datasets: [
      { label: 'Daily peak', data: city.air.map((d) => d.aqiMax), borderColor: 'rgba(94,234,212,.35)', borderDash: [4, 4], pointRadius: 0, borderWidth: 1.5, tension: .3 },
      { label: 'Daily mean AQI', data: city.air.map((d) => d.aqi), borderColor: '#5eead4', backgroundColor: 'rgba(94,234,212,.12)', fill: true, pointRadius: 0, pointHoverRadius: 4, borderWidth: 2.5, tension: .3 } ] },
    options: { ...base, scales: axes({ beginAtZero: true, suggestedMax: 100 }) },
    plugins: [{ id: 'bands', beforeDatasetsDraw(c) {
      const { ctx, chartArea: a, scales: { y } } = c; let lo = 0;
      for (const bd of BANDS) { if (lo >= y.max) break; const hi = Math.min(bd.max, y.max);
        ctx.fillStyle = bd.color + '14'; ctx.fillRect(a.left, y.getPixelForValue(hi), a.right - a.left, y.getPixelForValue(lo) - y.getPixelForValue(hi)); lo = hi; } } }] });

  const wxCfg = $derived(city && {
    data: { labels: city.weather.map((d) => short(d.d)), datasets: [
      { type: 'bar', label: 'Rain (mm)', data: city.weather.map((d) => d.rain), backgroundColor: 'rgba(96,165,250,.55)', yAxisID: 'r', borderRadius: 2, order: 3 },
      { type: 'line', label: 'Max °C', data: city.weather.map((d) => d.tmax), borderColor: '#fb923c', pointRadius: 0, borderWidth: 2, tension: .3, yAxisID: 'y', order: 1 },
      { type: 'line', label: 'Min °C', data: city.weather.map((d) => d.tmin), borderColor: '#38bdf8', pointRadius: 0, borderWidth: 2, tension: .3, yAxisID: 'y', order: 2 } ] },
    options: { ...base, scales: { ...axes(), r: { position: 'right', grid: { display: false }, ticks: { color: tick }, beginAtZero: true, suggestedMax: 40 } } } });

  const polCfg = $derived(last && {
    type: 'bar',
    data: { labels: ['PM2.5', 'PM10', 'Ozone', 'NO₂'], datasets: [{ label: 'µg/m³ (daily mean)', data: [last.pm25, last.pm10, last.o3, last.no2],
      backgroundColor: ['#5eead4', '#2dd4bf', '#a78bfa', '#f472b6'], borderRadius: 6 }] },
    options: { ...base, indexAxis: 'y', plugins: { ...base.plugins, legend: { display: false } }, scales: { x: { grid: { color: grid }, ticks: { color: tick } }, y: { grid: { display: false }, ticks: { color: '#c9dbe3' } } } } });

  const hourCfg = $derived(city && {
    type: 'bar',
    data: { labels: city.lastDayHourly.map((h) => h.t.slice(0, 2)), datasets: [{ label: 'US AQI', data: city.lastDayHourly.map((h) => h.aqi), backgroundColor: city.lastDayHourly.map((h) => band(h.aqi).color), borderRadius: 3 }] },
    options: { ...base, plugins: { ...base.plugins, legend: { display: false } }, scales: axes({ beginAtZero: true }) } });
</script>

<header class="top">
  <div class="brand">
    <svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="#13303a"/><path d="M6 12h14a3 3 0 1 0-3-3M6 17h19a3 3 0 1 1-3 3M6 22h9" stroke="#5eead4" stroke-width="2.2" fill="none" stroke-linecap="round"/></svg>
    <div><b>Alento</b><span>Brazil air &amp; weather atlas</span></div>
  </div>
  {#if data}<p class="src">Open data · Open-Meteo / CAMS · updated {data.generatedAt.slice(0, 10)}</p>{/if}
</header>

<main>
  {#if error}<p class="err" role="alert">{error}</p>
  {:else if !data}<p class="load">Loading atmosphere…</p>
  {:else}
    <nav class="chips" aria-label="City">
      {#each data.cities as c}
        <button class:on={c.id === sel} aria-pressed={c.id === sel} onclick={() => (sel = c.id)}>{c.name}</button>
      {/each}
    </nav>

    <section class="hero">
      <div class="aqi" style="--c:{b.color}">
        <small>{city.name} · {city.uf} · latest day</small>
        <div class="big">{last.aqi}<span>US AQI</span></div>
        <div class="pill"><i></i>{b.label}</div>
      </div>
      <div class="kpis">
        <div><small>PM2.5</small><b>{fmt(last.pm25, 1)}</b><em>µg/m³</em></div>
        <div><small>Peak AQI</small><b>{last.aqiMax}</b><em>that day</em></div>
        <div><small>Temp range</small><b>{fmt(lastW.tmin)}–{fmt(lastW.tmax)}°</b><em>{short(lastW.d)}</em></div>
        <div><small>Rain</small><b>{fmt(lastW.rain, 1)}</b><em>mm · {short(lastW.d)}</em></div>
      </div>
    </section>

    <section class="grid">
      <article class="card wide"><h2>Air quality, last 60 days <small>shaded bands = EPA categories</small></h2>
        <div class="h">{#key sel}<Chart config={aqiCfg} label="Daily US AQI line chart for {city.name}" />{/key}</div></article>
      <article class="card"><h2>Pollutants <small>latest day</small></h2>
        <div class="h s">{#key sel}<Chart config={polCfg} label="Pollutant concentrations for {city.name}" />{/key}</div></article>
      <article class="card"><h2>Hour by hour <small>AQI, latest day</small></h2>
        <div class="h s">{#key sel}<Chart config={hourCfg} label="Hourly AQI for {city.name}" />{/key}</div></article>
      <article class="card wide"><h2>Temperature &amp; rainfall <small>60 days</small></h2>
        <div class="h">{#key sel}<Chart config={wxCfg} label="Temperature and rainfall for {city.name}" />{/key}</div></article>

      <article class="card wide"><h2>City ranking <small>7-day mean AQI vs previous 7 days</small></h2>
        <div class="scroll"><table>
          <thead><tr>
            {#each [['name', 'City'], ['aqi', 'AQI 7d'], ['aqiDelta', 'Δ vs prev.'], ['temp', 'Temp °C'], ['rain30', 'Rain 30d']] as [k, l]}
              <th aria-sort={sortKey === k ? (sortDir > 0 ? 'ascending' : 'descending') : 'none'}><button onclick={() => sort(k)}>{l}{sortKey === k ? (sortDir > 0 ? ' ↑' : ' ↓') : ''}</button></th>
            {/each}
          </tr></thead>
          <tbody>
            {#each rows as r (r.id)}
              <tr class:on={r.id === sel} onclick={() => (sel = r.id)}>
                <td>{r.name} <small>{r.uf}</small></td>
                <td><span class="dot" style="background:{band(r.aqi).color}"></span>{r.aqi}</td>
                <td class={r.aqiDelta > 0 ? 'up' : 'down'}>{r.aqiDelta == null ? '—' : (r.aqiDelta > 0 ? '+' : '') + r.aqiDelta.toFixed(1)}</td>
                <td>{fmt(r.temp, 1)}</td><td>{fmt(r.rain30)} mm</td>
              </tr>
            {/each}
          </tbody>
        </table></div></article>
    </section>
  {/if}
</main>

{#if data}<footer>
  <p>Data: <a href="https://open-meteo.com/">Open-Meteo</a> weather archive and air-quality API (Copernicus CAMS model, CC BY 4.0). Values are modelled estimates, not station readings; do not use for health decisions. Alento is a fictional brand and a portfolio demo.</p>
</footer>{/if}
