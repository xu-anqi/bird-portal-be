import os
import requests
from datetime import datetime, timezone

# For local testing, you can temporarily hard-code your key:
# API_KEY = ""
# For GitHub Actions, we will use an environment variable:
API_KEY = os.getenv("OPENWEATHER_API_KEY")

LAT = 50.8798
LON = 4.7005
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def classify_temp(temp_c: float):
    if 6 <= temp_c <= 20:
        return "good", 2, f"Comfortable temperature ({temp_c:.1f}°C)"
    elif 0 <= temp_c < 6 or 20 < temp_c <= 25:
        return "medium", 1, f"Acceptable but not ideal ({temp_c:.1f}°C)"
    else:
        return "bad", 0, f"Challenging temperature ({temp_c:.1f}°C)"


def classify_wind(wind_ms: float):
    if wind_ms < 6:
        return "good", 2, f"Light wind ({wind_ms:.1f} m/s)"
    elif wind_ms < 9:
        return "medium", 1, f"Moderate wind ({wind_ms:.1f} m/s)"
    else:
        return "bad", 0, f"Strong wind ({wind_ms:.1f} m/s)"


def classify_rain(rain_1h_mm: float):
    if rain_1h_mm < 0.2:
        return "good", 2, f"Almost dry ({rain_1h_mm:.2f} mm last hour)"
    elif rain_1h_mm < 1.0:
        return "medium", 1, f"Light rain/drizzle ({rain_1h_mm:.2f} mm last hour)"
    else:
        return "bad", 0, f"Significant rain ({rain_1h_mm:.2f} mm last hour)"


def classify_visibility(vis_km: float):
    if vis_km > 7:
        return "good", 2, f"Good visibility ({vis_km:.1f} km)"
    elif vis_km >= 3:
        return "medium", 1, f"Limited visibility ({vis_km:.1f} km)"
    else:
        return "bad", 0, f"Poor visibility ({vis_km:.1f} km)"


def overall_verdict(total_score: int, max_score: int = 10):
    if total_score >= 9:
        emoji = "🌤"
        text = "Great birding weather in Leuven"
    elif total_score >= 7:
        emoji = "🙂"
        text = "Good birding conditions in Leuven"
    elif total_score >= 5:
        emoji = "😐"
        text = "Mixed conditions – check details"
    elif total_score >= 3:
        emoji = "😬"
        text = "Poor conditions for birding"
    else:
        emoji = "🚫"
        text = "Not recommended for birding"

    return emoji, text, f"{total_score}/{max_score}"


def fetch_weather():
    if not API_KEY:
        raise RuntimeError("OPENWEATHER_API_KEY is not set")
    params = {
        "lat": LAT,
        "lon": LON,
        "appid": API_KEY,
    }
    r = requests.get(BASE_URL, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def generate_html():
    data = fetch_weather()

    temp_k = data["main"]["temp"]
    temp_c = temp_k - 273.15

    wind_ms = data["wind"]["speed"]
    visibility_m = data.get("visibility", 10000)
    visibility_km = visibility_m / 1000

    rain_1h_mm = data.get("rain", {}).get("1h", 0.0)
    description = data["weather"][0]["description"].capitalize()
    clouds = data.get("clouds", {}).get("all", None)

    t_label, t_score, t_msg = classify_temp(temp_c)
    w_label, w_score, w_msg = classify_wind(wind_ms)
    r_label, r_score, r_msg = classify_rain(rain_1h_mm)
    v_label, v_score, v_msg = classify_visibility(visibility_km)

    total_score = t_score + w_score + v_score + (2 * r_score)
    max_score = 2 + 2 + 2 + 2 * 2  # temp + wind + vis + rain×2 = 10

    emoji, verdict_text, score_str = overall_verdict(total_score, max_score)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Simple mapping for label → color
    def badge_class(label):
        if label == "good":
            return "badge-good"
        if label == "medium":
            return "badge-medium"
        return "badge-bad"

    t_class = badge_class(t_label)
    w_class = badge_class(w_label)
    r_class = badge_class(r_label)
    v_class = badge_class(v_label)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Leuven birding weather</title>
  <style>
    :root {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      color-scheme: light dark;
    }}
    body {{
      margin: 0;
      padding: 0.75rem;
      font-size: 14px;
      background: transparent;
    }}
    .card {{
      border-radius: 12px;
      border: 1px solid #e0e0e0;
      padding: 0.75rem 0.9rem;
      background: rgba(255, 255, 255, 0.9);
      box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }}
    .title-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      margin-bottom: 0.35rem;
    }}
    .title {{
      font-size: 15px;
      font-weight: 600;
    }}
    .score-pill {{
      font-size: 12px;
      padding: 0.15rem 0.5rem;
      border-radius: 999px;
      border: 1px solid #ddd;
      background: #f7f7f7;
    }}
    .verdict {{
      font-size: 14px;
      margin-bottom: 0.3rem;
    }}
    .meta {{
      font-size: 11px;
      color: #666;
      margin-bottom: 0.6rem;
    }}
    .meta span + span::before {{
      content: "•";
      margin: 0 0.3rem;
      color: #aaa;
    }}
    ul {{
      list-style: none;
      padding-left: 0;
      margin: 0;
      font-size: 13px;
    }}
    li {{
      margin-bottom: 0.25rem;
      display: flex;
      gap: 0.35rem;
      align-items: baseline;
    }}
    .label {{
      min-width: 78px;
      font-weight: 500;
    }}
    .badge {{
      font-size: 11px;
      padding: 0.05rem 0.4rem;
      border-radius: 999px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .badge-good {{
      background: #e3f6e8;
      color: #1b7b3f;
    }}
    .badge-medium {{
      background: #fff5d6;
      color: #946200;
    }}
    .badge-bad {{
      background: #ffe3e3;
      color: #a12a2a;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="title-row">
      <div class="title">Leuven birding weather</div>
      <div class="score-pill">{score_str}</div>
    </div>
    <div class="verdict">{emoji} {verdict_text}</div>
    <div class="meta">
      <span>{description}{"," if clouds is not None else ""}{f" clouds {clouds}%" if clouds is not None else ""}</span>
      <span>Last update: {now}</span>
    </div>
    <ul>
      <li>
        <span class="label">Temperature</span>
        <span class="badge {t_class}">{t_label}</span>
        <span>{t_msg}</span>
      </li>
      <li>
        <span class="label">Wind</span>
        <span class="badge {w_class}">{w_label}</span>
        <span>{w_msg}</span>
      </li>
      <li>
        <span class="label">Rain (1 h)</span>
        <span class="badge {r_class}">{r_label}</span>
        <span>{r_msg}</span>
      </li>
      <li>
        <span class="label">Visibility</span>
        <span class="badge {v_class}">{v_label}</span>
        <span>{v_msg}</span>
      </li>
    </ul>
  </div>
</body>
</html>
"""
    return html


def main():
    html = generate_html()
    with open("leuven_birding_status.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
