"""Daily family briefing: 3-card layout (Weather, Advice, Events).

Run daily:   python weather.py
Run as watch: python weather.py --watch      (only messages on severe alerts)
"""
import os
import sys
import html
import json
import requests
import yaml
from datetime import datetime, timezone, timedelta

OWM = "https://api.openweathermap.org"
esc = html.escape

# ----------------------------------------------------------------- helpers

def owm(key, path, **params):
    r = requests.get(OWM + path, params={**params, "appid": key, "units": "metric"}, timeout=20)
    r.raise_for_status()
    return r.json()

def openmeteo(lat, lon):
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat, "longitude": lon, "timezone": "auto", "forecast_days": 6,
            "hourly": "precipitation_probability,temperature_2m,uv_index",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        }, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        print("Open-Meteo unavailable:", exc)
        return None

def get_moon_phase(dt):
    ref = datetime(2024, 1, 11, 11, 57, tzinfo=timezone.utc)
    days = (dt - ref).total_seconds() / 86400
    phase = (days % 29.53058867) / 29.53058867
    if phase < 0.04 or phase > 0.96:
        return "Amavasya (New Moon) 🌑"
    if 0.46 < phase < 0.54:
        return "Purnima (Full Moon) 🌕"
    return None

def fmt(dt): return dt.strftime("%I:%M %p").lstrip("0")
def fmt_h(h): return f"{h % 12 or 12}:00 {'AM' if h < 12 else 'PM'}"
def short_h(h): return f"{h % 12 or 12}{'A' if h < 12 else 'P'}"

def wmo_emoji(c):
    if c == 0: return "☀️"
    if c in (1, 2): return "🌤️"
    if c == 3: return "☁️"
    if c in (45, 48): return "🌫️"
    if 51 <= c <= 57 or c in (80, 81, 82): return "🌦️"
    if 61 <= c <= 67: return "🌧️"
    if 71 <= c <= 77 or c in (85, 86): return "❄️"
    if c >= 95: return "⛈️"
    return "🌤️"

def owm_emoji(main, night=False):
    if main == "Clear": return "🌙" if night else "☀️"
    return {"Clouds": "☁️", "Rain": "🌧️", "Drizzle": "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️"}.get(main, "🌫️")

# ----------------------------------------------------------------- events

ICONS = {"birthday": "🎂", "anniversary": "💐", "event": "📌", "reminder": "⏰", "bill": "💳", "temple": "🛕", "holiday": "🏖️"}
FESTIVALS = ("diwali", "deepavali", "pongal", "holi", "eid", "christmas", "onam", "ugadi", "navratri", "dussehra", "ganesh", "new year")

def load_events():
    try:
        with open("events.yaml", encoding="utf-8") as f:
            return yaml.safe_load(f) or []
    except FileNotFoundError: return []

def holiday_table(year, state):
    try:
        import holidays
        return holidays.country_holidays("IN", subdiv=state or None, years=[year, year + 1])
    except: return {}

def matches(e, day):
    rep = e.get("repeat")
    if rep == "daily": return True
    if rep == "weekly": return day.strftime("%a") in [str(x)[:3].title() for x in e.get("days", [])]
    if rep == "monthly": return day.day == int(e.get("day", 0))
    return str(e.get("date", "")) in (day.isoformat(), day.strftime("%m-%d"))

def items_for(day, events, hol, upcoming=False):
    out = []
    for e in events:
        if not matches(e, day): continue
        rep = e.get("repeat")
        if upcoming and rep in ("daily", "weekly"): continue
        kind = e.get("type", "event")
        text, age = e["name"], None
        if e.get("year") and kind in ("birthday", "anniversary"):
            age = day.year - int(e["year"])
            text += f" turns {age}" if kind == "birthday" else f" ({age} years)"
        out.append({"icon": ICONS.get(kind, "📌"), "text": text, "kind": kind, "name": e["name"], "age": age, "special": rep != "daily"})
    if day in hol:
        name = hol[day]
        if not upcoming and any(k in name.lower() for k in FESTIVALS):
            out.append({"icon": "🎉", "text": f"Happy {name}!", "kind": "holiday", "special": True})
        else:
            out.append({"icon": ICONS["holiday"], "text": f"Holiday: {name}", "kind": "holiday", "special": True})
    return out

# ----------------------------------------------------------------- data

def collect():
    key = os.environ["OWM_API_KEY"]
    zip_code = os.environ.get("ZIP_CODE") or "600001,IN"
    geo = owm(key, "/geo/1.0/zip", zip=zip_code)
    lat, lon = geo["lat"], geo["lon"]
    cur = owm(key, "/data/2.5/weather", lat=lat, lon=lon)
    fc = owm(key, "/data/2.5/forecast", lat=lat, lon=lon)
    aq = owm(key, "/data/2.5/air_pollution", lat=lat, lon=lon)["list"][0]
    om = openmeteo(lat, lon)

    tz = timezone(timedelta(seconds=fc["city"]["timezone"]))
    now = datetime.now(tz)
    today = now.date()
    def at(ts): return datetime.fromtimestamp(ts, tz)

    sunrise, sunset = at(cur["sys"]["sunrise"]), at(cur["sys"]["sunset"])
    night = now < sunrise or now > sunset
    slots = [s for s in fc["list"] if at(s["dt"]).date() == today and at(s["dt"]) + timedelta(hours=3) > now]

    d = {"city": cur["name"], "now": now, "temp": cur["main"]["temp"], "feels": cur["main"]["feels_like"],
         "humidity": cur["main"]["humidity"], "cond": cur["weather"][0]["description"].title(),
         "main": cur["weather"][0]["main"], "night": night, "sunrise": sunrise, "sunset": sunset,
         "aqi": aq["main"]["aqi"], "pm25": aq["components"]["pm2_5"], "moon": get_moon_phase(now)}
    d["t_min"] = min([s["main"]["temp_min"] for s in slots] + [d["temp"]])
    d["t_max"] = max([s["main"]["temp_max"] for s in slots] + [d["temp"]])

    hourly = {}
    if om:
        h = om["hourly"]
        for i, ts in enumerate(h["time"]):
            dt = datetime.fromisoformat(ts)
            if dt.date() == today:
                hourly[dt.hour] = {"pop": h["precipitation_probability"][i] or 0, "temp": h["temperature_2m"][i], "uv": h["uv_index"][i]}
    d["hourly"] = hourly

    wet = [hr for hr in sorted(hourly) if hr >= now.hour and hourly[hr]["pop"] >= 50]
    d["rain"] = None
    if wet:
        end = wet[0]
        while end + 1 in wet: end += 1
        d["rain"] = {"start": wet[0], "end": end + 1, "chance": max([hourly[x]["pop"] for x in range(wet[0], end + 1)]), "now": wet[0] <= now.hour}

    winds = [cur["wind"]["speed"], cur["wind"].get("gust", 0)] + [s["wind"]["speed"] for s in slots]
    d["wind"] = max(winds) * 3.6
    uvs = [(v["uv"], hr) for hr, v in hourly.items() if v["uv"] is not None]
    d["uv"], d["uv_hour"] = (max(uvs) if uvs else (None, None))

    outlook = []
    if om:
        dd = om["daily"]
        for i in range(1, 6):
            outlook.append({"label": datetime.fromisoformat(dd["time"][i]).strftime("%a"), "emoji": wmo_emoji(dd["weather_code"][i]),
                            "hi": dd["temperature_2m_max"][i], "lo": dd["temperature_2m_min"][i], "pop": dd["precipitation_probability_max"][i] or 0})
    d["outlook"] = outlook

    limit = float(os.environ.get("WIND_LIMIT") or 60)
    alerts = []
    if d["wind"] >= limit: alerts.append(("red", "⚠️ HIGH WIND ALERT. DO NOT GO OUTSIDE"))
    if d["aqi"] == 5: alerts.append(("red", "😷 Very poor air quality. Avoid outdoor activity"))
    d["alerts"] = alerts

    events = load_events()
    hol = holiday_table(today.year, os.environ.get("HOLIDAY_STATE"))
    d["today"] = items_for(today, events, hol)
    sunday = today.weekday() == 6
    up = []
    for i in range(1, 15): # Look ahead 2 weeks for bills/events
        day = today + timedelta(days=i)
        for it in items_for(day, events, hol, upcoming=True):
            it["when"] = "tomorrow" if i == 1 else f"in {i} days"
            it["date"] = day.strftime("%a %d %b")
            up.append(it)
    d["upcoming"] = up[:8]

    # Tamil Advice
    adv = []
    if d.get("moon"): adv.append(("✨", f"இன்று {d['moon']}"))
    for i in d["today"]:
        if "temple" in i.get("kind", "") or "pradosham" in i.get("name", "").lower():
            adv.append(("🛕", f"இன்று {i['name']} - சிவன் கோவிலுக்கு செல்லவும்"))
            
    if d["uv"] and d["uv"] >= 6: adv.append(("🧴", f"அதிக UV ({d['uv']:.0f}). குடை பயன்படுத்தவும்"))
    if d["feels"] >= 35: adv.append(("☀️", "வெப்பமான நாள். போதுமான தண்ணீர் குடிக்கவும்"))
    
    if d["rain"]:
        r_time = "இப்போது" if d["rain"]["now"] else f"{fmt_h(d['rain']['start'])} அளவில்"
        adv.append(("☔", f"{r_time} மழை வரலாம்: குடை எடுத்துச் செல்லவும்"))
        adv.append(("🧺", "இன்று வெளியே துணி காயவைக்க வேண்டாம்"))
    else:
        adv.append(("🧺", "துணிகளை வெளியே காயவைக்க நல்ல நாள்"))
        
    for var, label in (("SCHOOL_DROP", "பள்ளி செல்லும்"), ("SCHOOL_PICKUP", "பள்ளி முடியும்")):
        t = os.environ.get(var)
        if t and d["rain"]:
            hr, mn = (int(x) for x in (t.split(":") + ["0"])[:2])
            if d["rain"]["start"] <= hr < d["rain"]["end"]:
                adv.append(("🎒", f"{label} நேரத்தில் மழை வரலாம். குடை கொடுத்தனுப்பவும்"))
    d["advice"] = adv
    return d

# ----------------------------------------------------------------- HTML Templates

FONT = "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap"
BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Outfit',sans-serif;background:#F9FAFB;color:#0F172A;line-height:1.3;width:800px}
.card{background:#fff;border-radius:40px;margin:20px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,0.05)}
.head{color:#fff;padding:45px;background:linear-gradient(135deg,var(--a),var(--b))}
.title{font-size:32px;font-weight:600;opacity:0.9}
.date{font-size:24px;font-weight:300;margin-top:5px}
.sec{padding:30px 45px;border-bottom:1px solid #EAECF0}
.sec:last-child{border-bottom:0}
.t{font-size:28px;font-weight:600;color:#1E293B;margin-bottom:20px}
.row{display:flex;align-items:center;gap:20px;font-size:26px;padding:12px 0;border-bottom:1px solid #f1f5f9}
.row:last-child{border-bottom:0}
.row .i{font-size:36px;width:45px;text-align:center}
.when{margin-left:auto;background:#F1F5F9;border-radius:20px;padding:6px 16px;font-size:22px;color:#475467}
"""

def template(title, d, content):
    a, b = {"night": ("#1E293B", "#334155"), "Clear": ("#0284C7", "#38BDF8")}.get("night" if d["night"] and d["main"]=="Clear" else d["main"], ("#475569", "#94A3B8"))
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}">
<style>{BASE_CSS}</style></head><body><div class="card" style="--a:{a};--b:{b}">
<div class="head"><div class="title">{title}</div><div class="date">{d["now"].strftime('%A, %d %b %Y')}</div></div>
{content}</div></body></html>"""

def card_weather(d):
    icon = owm_emoji(d["main"], d["night"])
    stats = f"""
    <div style="display:flex;justify-content:space-between;align-items:center;padding:45px;background:linear-gradient(135deg,var(--a),var(--b));color:#fff;margin-top:-45px">
        <div><div style="font-size:160px;font-weight:300;line-height:1">{d['temp']:.0f}°</div><div style="font-size:36px;font-weight:500">{d['cond']}</div></div>
        <div style="font-size:140px">{icon}</div>
    </div>
    <div class="sec" style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
        <div style="background:#F1F5F9;padding:20px;border-radius:20px"><div style="font-size:22px;color:#475467">🌧️ Rain</div><div style="font-size:32px;font-weight:600">{f"{d['rain']['chance']}% chance" if d['rain'] else "No rain"}</div></div>
        <div style="background:#F1F5F9;padding:20px;border-radius:20px"><div style="font-size:22px;color:#475467">🫁 AQI</div><div style="font-size:32px;font-weight:600">Level {d['aqi']}</div></div>
    </div>"""
    
    out = "".join(f'<div style="text-align:center"><div style="font-size:24px;color:#475467">{o["label"]}</div><div style="font-size:46px;margin:10px 0">{o["emoji"]}</div><div style="font-size:26px;font-weight:600">{o["hi"]:.0f}°</div></div>' for o in d["outlook"])
    return template(f"{d['city']} Weather", d, stats + f'<div class="sec"><div class="t">5-Day Outlook</div><div style="display:grid;grid-template-columns:repeat(5,1fr)">{out}</div></div>')

def card_advice(d):
    items = "".join(f'<div class="row"><span class="i">{i}</span><span>{esc(t)}</span></div>' for i, t in d["advice"])
    sun = f'<div class="sec" style="display:flex;justify-content:space-around;font-size:26px;background:#FFFBEB"><span>🌅 {fmt(d["sunrise"])}</span><span>🌇 {fmt(d["sunset"])}</span></div>'
    return template("Daily Guide & Advice", d, sun + f'<div class="sec">{items}</div>')

def card_events(d):
    today = "".join(f'<div class="row"><span class="i">{i["icon"]}</span><span><b>{esc(i["text"])}</b></span></div>' for i in d["today"])
    up = "".join(f'<div class="row"><span class="i">{i["icon"]}</span><span>{esc(i["text"])}<br><span style="font-size:22px;color:#667085">{i["date"]}</span></span><span class="when">{i["when"]}</span></div>' for i in d["upcoming"])
    content = ""
    if today: content += f'<div class="sec" style="background:#F0FDF4"><div class="t" style="color:#166534">Happening Today</div>{today}</div>'
    if up: content += f'<div class="sec"><div class="t">Upcoming Events & Bills</div>{up}</div>'
    if not content: content = '<div class="sec" style="font-size:26px;color:#667085">No upcoming events or bills in the next two weeks.</div>'
    return template("Family Calendar", d, content)

# ----------------------------------------------------------------- output

def render_png(html_str, path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 800, "height": 100}) # auto-resizes to content
        page.set_content(html_str)
        page.locator(".card").screenshot(path=path)
        b.close()
    return path

def send_album(paths, cap):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat = os.environ["TELEGRAM_CHAT_ID"]
    files, media = {}, []
    
    for i, path in enumerate(paths):
        name = f"img{i}"
        files[name] = open(path, "rb")
        item = {"type": "photo", "media": f"attach://{name}"}
        if i == 0: item["caption"] = cap
        media.append(item)
        
    r = requests.post(f"https://api.telegram.org/bot{token}/sendMediaGroup", data={"chat_id": chat, "media": json.dumps(media)}, files=files, timeout=60)
    r.raise_for_status()

def main():
    d = collect()
    if "--watch" in sys.argv:
        if any(lvl == "red" for lvl, t in d["alerts"]):
            requests.post(f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage", json={"chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": "ALERT!\n" + "\n".join(t for l, t in d["alerts"])})
        return

    render_png(card_weather(d), "weather.png")
    render_png(card_advice(d), "advice.png")
    render_png(card_events(d), "events.png")
    
    cap = f"{d['city']}: {d['temp']:.0f}°C, {d['cond']}. " + ("Rain expected." if d["rain"] else "")
    try:
        send_album(["weather.png", "advice.png", "events.png"], cap)
    except Exception as exc:
        print("Failed to send album:", exc)

if __name__ == "__main__":
    main()
