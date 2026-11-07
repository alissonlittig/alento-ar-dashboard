"""Fetch open data from Open-Meteo (no key) and write public/data.json. Stdlib only."""
import json, subprocess, sys, urllib.request, urllib.parse
from datetime import date, timedelta, datetime, timezone
from collections import defaultdict

CITIES = [
    ("curitiba", "Curitiba", "PR", -25.43, -49.27), ("sao-paulo", "São Paulo", "SP", -23.55, -46.63),
    ("rio", "Rio de Janeiro", "RJ", -22.91, -43.17), ("belo-horizonte", "Belo Horizonte", "MG", -19.92, -43.94),
    ("brasilia", "Brasília", "DF", -15.79, -47.88), ("salvador", "Salvador", "BA", -12.97, -38.50),
    ("manaus", "Manaus", "AM", -3.12, -60.02), ("porto-alegre", "Porto Alegre", "RS", -30.03, -51.23),
]
DAYS = 60
TZ = "America/Sao_Paulo"

def get(url, **q):
    # curl: uses the OS trust store (python's bundled store can be stale on some Windows boxes)
    out = subprocess.run(["curl", "-sfS", "--max-time", "60", url + "?" + urllib.parse.urlencode(q)],
                         capture_output=True, check=True)
    return json.loads(out.stdout)

def build_city(c):
    cid, name, uf, lat, lon = c
    end = date.today() - timedelta(days=2)  # archive lags ~2 days
    wx = get("https://archive-api.open-meteo.com/v1/archive", latitude=lat, longitude=lon,
             start_date=(end - timedelta(days=DAYS)).isoformat(), end_date=end.isoformat(),
             daily="temperature_2m_max,temperature_2m_min,precipitation_sum", timezone=TZ)["daily"]
    aq = get("https://air-quality-api.open-meteo.com/v1/air-quality", latitude=lat, longitude=lon,
             hourly="pm2_5,pm10,ozone,nitrogen_dioxide,us_aqi", past_days=DAYS, forecast_days=1, timezone=TZ)["hourly"]
    byday = defaultdict(lambda: defaultdict(list))
    for i, t in enumerate(aq["time"]):
        for k in ("pm2_5", "pm10", "ozone", "nitrogen_dioxide", "us_aqi"):
            v = aq[k][i]
            if v is not None: byday[t[:10]][k].append(v)
    air = []
    for d in sorted(byday):
        m = byday[d]
        if not m["us_aqi"]: continue
        avg = lambda k: round(sum(m[k]) / len(m[k]), 1) if m[k] else None
        air.append({"d": d, "aqi": round(sum(m["us_aqi"]) / len(m["us_aqi"])), "aqiMax": max(m["us_aqi"]),
                    "pm25": avg("pm2_5"), "pm10": avg("pm10"), "o3": avg("ozone"), "no2": avg("nitrogen_dioxide")})
    last = max(byday)
    hourly = [{"t": t[11:16], "aqi": v} for t, v in zip(aq["time"], aq["us_aqi"]) if t[:10] == last and v is not None]
    weather = [{"d": d, "tmax": a, "tmin": b, "rain": r} for d, a, b, r in
               zip(wx["time"], wx["temperature_2m_max"], wx["temperature_2m_min"], wx["precipitation_sum"]) if a is not None]
    return {"id": cid, "name": name, "uf": uf, "lat": lat, "lon": lon, "air": air, "weather": weather, "lastDayHourly": hourly}

if __name__ == "__main__":
    out = {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="minutes"),
           "source": "Open-Meteo Historical Weather API and Air Quality API (CAMS), open data, no login",
           "cities": [build_city(c) for c in CITIES]}
    path = sys.argv[1] if len(sys.argv) > 1 else "public/data.json"
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("ok", path, [(c["id"], len(c["air"]), len(c["weather"])) for c in out["cities"]])
