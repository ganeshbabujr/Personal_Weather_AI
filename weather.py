"""Daily family briefing: 3-card layout (Weather, Advice+Panchangam, Events) + Birthday Cards.

Run daily:   python weather.py
Run as watch: python weather.py --watch
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

def get_panchangam(dt, sunrise, sunset):
    """Calculates Tithi, Nakshatra, Tamil Date, and exact daily timings based on local sunrise."""
    try:
        import ephem
        import math
    except ImportError:
        print("ephem library not installed. Skipping panchangam.")
        return None

    obs = ephem.Observer()
    special = set()
    nak_names = set()

    for hr in [6, 12, 18]:
        check_time = dt.replace(hour=hr, minute=0, second=0)
        obs.date = check_time.astimezone(timezone.utc)
        sun = ephem.Sun(obs)
        moon = ephem.Moon(obs)

        sun_deg = math.degrees(ephem.Ecliptic(sun).lon)
        moon_deg = math.degrees(ephem.Ecliptic(moon).lon)

        diff = (moon_deg - sun_deg) % 360
        tithi_num = int(diff / 12.0) + 1
        tithis = ["Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadasi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
                  "Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadasi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"]
        tithi_name = tithis[tithi_num - 1]

        if tithi_name == "Amavasya": special.add("🌑 Amavasya (அமாவாசை)")
        if tithi_name == "Purnima": special.add("🌕 Pournami (பௌர்ணமி)")
        if tithi_name == "Ekadasi": special.add("🙏 Ekadasi (ஏகாதசி) - Fasting day")
        if tithi_name == "Trayodashi":
            if check_time.weekday() == 5:
                special.add("🛕 Sani Pradosham (சனி பிரதோஷம்) - Go to Sivan temple")
            else:
                special.add("🛕 Pradosham (பிரதோஷம்) - Go to Sivan temple")
        if tithi_name == "Chaturthi": special.add("🐘 Chaturthi (சதுர்த்தி) - Vinayagar worship")
        if tithi_name == "Shashti": special.add("🦚 Shashti (சஷ்டி) - Murugan worship")
        if tithi_name == "Ashtami": special.add("⚠️ Ashtami (அஷ்டமி)")
        if tithi_name == "Navami": special.add("⚠️ Navami (நவமி)")

        ayanamsa = 24.15 
        nirayana_moon = (moon_deg - ayanamsa) % 360
        nak_num = int(nirayana_moon / (360/27.0))
        nakshatras = ["Aswini", "Bharani", "Karthigai", "Rohini", "Mrigasira", "Arudra", "Punarvasu", "Pushya", "Ashlesha",
                      "Magam", "Pooram", "Uthiram", "Hastham", "Chithirai", "Swathi", "Visakam", "Anusham", "Kettai",
                      "Moolam", "Pooradam", "Uthiradam", "Thiruvonam", "Avittam", "Sadayam", "Poorattadhi", "Uthirattadhi", "Revathi"]
        nak_name = nakshatras[nak_num]
        nak_names.add(nak_name)
        
        if nak_name == "Karthigai": special.add("🪔 Kiruthigai (கிருத்திகை)")
        if nak_name == "Thiruvonam": special.add("🌸 Thiruvonam (திருவோணம்)")

    obs.date = dt.replace(hour=12).astimezone(timezone.utc)
    sun.compute(obs)
    sun_deg = math.degrees(ephem.Ecliptic(sun).lon)
    nirayana_sun = (sun_deg - ayanamsa) % 360
    month_num = int(nirayana_sun / 30)
    months = ["Chithirai", "Vaikasi", "Aani", "Aadi", "Avani", "Purattasi", "Aippasi", "Karthigai", "Margazhi", "Thai", "Masi", "Panguni"]
    
    rasi_deg = nirayana_sun % 30
    day_num = int(rasi_deg / 0.9856) + 1

    # Exact Daily Timings (Dividing daytime into 8 parts)
    day_idx = dt.weekday() # 0 = Mon, 6 = Sun
    rahu_parts = [1, 6, 4, 5, 3, 2, 7]
    yama_parts = [3, 2, 1, 0, 6, 5, 4]
    kuli_parts = [5, 4, 3, 2, 1, 0, 6]
    nalla_neram_map = [
        "6:30 AM - 7:30 AM, 4:30 PM - 5:30 PM", # Mon
        "7:30 AM - 8:30 AM, 4:30 PM - 5:30 PM", # Tue
        "9:00 AM - 10:00 AM, 4:30 PM - 5:30 PM", # Wed
        "10:30 AM - 11:30 AM, 12:00 PM - 1:00 PM", # Thu
        "9:30 AM - 10:30 AM, 4:30 PM - 5:30 PM", # Fri
        "7:30 AM - 8:30 AM, 4:30 PM - 5:30 PM", # Sat
        "7:30 AM - 8:30 AM, 3:30 PM - 4:30 PM", # Sun
    ]
    
    part_dur = (sunset - sunrise) / 8
    def get_time(p):
        start = sunrise + (part_dur * p)
        end = start + part_dur
        return f"{start.strftime('%I:%M %p').lstrip('0')} - {end.strftime('%I:%M %p').lstrip('0')}"

    return {
        "special": sorted(list(special)),
        "nakshatra": " / ".join(sorted(list(nak_names))),
        "tamil_date": f"{months[month_num]} {day_num}",
        "rahu": get_time(rahu_parts[day_idx]),
        "yama": get_time(yama_parts[day_idx]),
        "kuli": get_time(kuli_parts[day_idx]),
        "nalla": nalla_neram_map[day_idx]
    }

def fmt(dt): return dt.strftime("%I:%M %p").lstrip("0")
def fmt_h(h): return f"{h % 12 or 12}:00 {'AM' if h < 12 else 'PM'}"
def short_h(h): return f"{h % 12 or 12}{'A' if h < 12 else 'P'}"
def owm_emoji(main, night=False):
    if main == "Clear": return "🌙" if night else "☀️"
    return {"Clouds": "☁️", "Rain": "🌧️", "Drizzle": "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️"}.get(main, "🌫️")

# ----------------------------------------------------------------- events

ICONS = {"birthday": "🎂", "anniversary": "💐", "event": "📌", "reminder": "⏰", "bill": "💳", "temple": "🛕", "holiday": "🏖️"}
FESTIVALS = ("diwali", "deepavali", "pongal", "holi", "eid", "christmas", "onam", "ugadi", "navratri", "dussehra", "ganesh", "new year")

def load_events():
    try:
        with open("events.yaml", encoding="utf-8") as f: return yaml.safe_load(f) or []
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
        if not upcoming and any(k in name.lower() for k in FESTIVALS): out.append({"icon": "🎉", "text": f"Happy {name}!", "kind": "holiday", "special": True})
        else: out.append({"icon": ICONS["holiday"], "text": f"Holiday: {name}", "kind": "holiday", "special": True})
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
         "aqi": aq["main"]["aqi"], "pm25": aq["components"]["pm2_5"], "panchangam": get_panchangam(now, sunrise, sunset)}
    
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
            outlook.append({"label": datetime.fromisoformat(dd["time"][i]).strftime("%a"), "emoji": owm_emoji(None) if dd["weather_code"][i] == 0 else "☁️",
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
    for i in range(1, 15):
        day = today + timedelta(days=i)
        for it in items_for(day, events, hol, upcoming=True):
            it["when"] = "tomorrow" if i == 1 else f"in {i} days"
            it["date"] = day.strftime("%a %d %b")
            up.append(it)
    d["upcoming"] = up[:8]

    # Tamil Advice
    adv = []
    if d["uv"] and d["uv"] >= 6: adv.append(("🧴", f"அதிக UV ({d['uv']:.0f}). குடை பயன்படுத்தவும்"))
    if d["feels"] >= 35: adv.append(("☀️", "வெப்பமான நாள். போதுமான தண்ணீர் குடிக்கவும்"))
    
    if d["rain"]:
        r_time = "இப்போது" if d["rain"]["now"] else f"{fmt_h(d['rain']['start'])} அளவில்"
        adv.append(("☔", f"{r_time} மழை வரலாம்: குடை எடுத்துச் செல்லவும்"))
        adv.append(("🧺", "இன்று வெளியே துணி காயவைக்க வேண்டாம்"))
    else:
        adv.append(("🧺", "துணிகளை வெளியே காயவைக்க நல்ல நாள்"))
        
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
.sub{font-size:26px;font-weight:300;margin-top:8px;color:rgba(255,255,255,0.9)}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:24px}
.st{padding:18px;background:#F9FAFB;border-radius:16px}
.k{font-size:24px;color:#667085}
.v{font-size:38px;font-weight:600;margin-top:6px}
.d{font-size:21px;color:#475467;margin-top:4px}
.bars{display:flex;align-items:flex-end;gap:6px;height:120px}
.col{flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;height:100%}
.bar{width:100%;border-radius:6px 6px 3px 3px}
.lab{font-size:19px;color:#667085;height:24px;margin-top:6px;white-space:nowrap}
.call{font-size:28px;font-weight:500;margin-top:12px}
"""

def template(title, d, content):
    a, b = {"night": ("#1E293B", "#334155"), "Clear": ("#0284C7", "#38BDF8")}.get("night" if d["night"] and d["main"]=="Clear" else d["main"], ("#475569", "#94A3B8"))
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}">
<style>{BASE_CSS}</style></head><body><div class="card" style="--a:{a};--b:{b}">
<div class="head"><div class="title">{title}</div><div class="date">{d["now"].strftime('%A, %d %b %Y')}</div></div>
{content}</div></body></html>"""

def card_weather(d):
    icon = owm_emoji(d["main"], d["night"])
    wcol = "#D92D20" if d["wind"] >= 60 else "#B54708" if d["wind"] >= 40 else "#0F172A"
    wnote = "Dangerous" if d["wind"] >= 60 else "Strong" if d["wind"] >= 40 else "Calm to breezy"
    aqi_name = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very poor"}.get(d["aqi"], "Unknown")
    acol = {1: "#067647", 2: "#4D7C0F", 3: "#B54708", 4: "#D92D20", 5: "#7A1FA2"}.get(d["aqi"], "#0F172A")
    if d["uv"] is None:
        uv_v, uv_d, ucol, uv_k = f"{d['humidity']}%", "Humidity", "#0F172A", "💧 Humid"
    else:
        uv_v, uv_k = f"{d['uv']:.0f}", "🧴 UV peak"
        uv_d = "Very high" if d["uv"] >= 8 else "High" if d["uv"] >= 6 else "Moderate" if d["uv"] >= 3 else "Low"
        ucol = "#D92D20" if d["uv"] >= 8 else "#B54708" if d["uv"] >= 6 else "#0F172A"
    
    rain_v = "Now" if d["rain"] and d["rain"]["now"] else (fmt_h(d["rain"]["start"]) if d["rain"] else "Dry")
    rain_d = f"{d['rain']['chance']}% chance" if d["rain"] else "No rain today"
    
    stats = f"""<div class="sec"><div class="stats">
      <div class="st"><div class="k">🌧️ Rain</div><div class="v">{rain_v}</div><div class="d">{rain_d}</div></div>
      <div class="st"><div class="k">💨 Wind</div><div class="v" style="color:{wcol}">{d['wind']:.0f}</div><div class="d">km/h, {wnote}</div></div>
      <div class="st"><div class="k">🫁 Air</div><div class="v" style="color:{acol}">{aqi_name}</div><div class="d">AQI {d['aqi']}, PM2.5 {d['pm25']:.0f}</div></div>
      <div class="st"><div class="k">{uv_k}</div><div class="v" style="color:{ucol}">{uv_v}</div><div class="d">{uv_d}</div></div>
      </div></div>"""

    strip = ""
    hrs = [h for h in range(6, 22) if h in d["hourly"]]
    if hrs:
        cols = ""
        for h in hrs:
            p = d["hourly"][h]["pop"]
            color = "#2E90FA" if p >= 50 else "#B2DDFF" if p >= 20 else "#E4E7EC"
            lab = short_h(h) if h % 3 == 0 else ""
            cols += f'<div class="col"><div class="bar" style="height:{max(8, p * 1.2):.0f}px;background:{color}"></div><div class="lab">{lab}</div></div>'
        call = f"High chance of rain now, {d['rain']['chance']}% chance" if d["rain"] and d["rain"]["now"] else ("Expected around " + fmt_h(d["rain"]["start"]) if d["rain"] else "Dry through the day")
        strip = f'<div class="sec"><div class="t">Rain chance by hour</div><div class="bars">{cols}</div><div class="call">{call}</div></div>'

    head = f"""<div style="display:flex;justify-content:space-between;align-items:center;padding:20px 45px 45px;background:linear-gradient(135deg,var(--a),var(--b));color:#fff;margin-top:-45px">
        <div><div style="font-size:160px;font-weight:300;line-height:1;letter-spacing:-6px">{d['temp']:.0f}°</div><div style="font-size:36px;font-weight:500;margin-top:10px">{d['cond']}</div><div class="sub">Feels {d['feels']:.0f}°, high {d['t_max']:.0f}°, low {d['t_min']:.0f}°</div></div>
        <div style="font-size:140px">{icon}</div>
    </div>"""
    
    return template(f"{d['city']} Weather", d, head + stats + strip)

def card_advice(d):
    p = d.get("panchangam")
    panch_html = ""
    if p:
        sp = "".join(f'<div class="row"><span class="i" style="font-size:32px">{i.split(" ")[0]}</span><span>{esc(" ".join(i.split(" ")[1:]))}</span></div>' for i in p["special"])
        time_grid = f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px">
            <div style="background:#fff;padding:15px;border-radius:15px;box-shadow:0 2px 5px rgba(0,0,0,0.05)"><div style="font-size:22px;color:#93370D;margin-bottom:5px">நல்ல நேரம்</div><div style="font-size:24px;font-weight:600;color:#1E293B">{p['nalla']}</div></div>
            <div style="background:#fff;padding:15px;border-radius:15px;box-shadow:0 2px 5px rgba(0,0,0,0.05)"><div style="font-size:22px;color:#93370D;margin-bottom:5px">ராகு காலம்</div><div style="font-size:24px;font-weight:600;color:#1E293B">{p['rahu']}</div></div>
            <div style="background:#fff;padding:15px;border-radius:15px;box-shadow:0 2px 5px rgba(0,0,0,0.05)"><div style="font-size:22px;color:#93370D;margin-bottom:5px">எமகண்டம்</div><div style="font-size:24px;font-weight:600;color:#1E293B">{p['yama']}</div></div>
            <div style="background:#fff;padding:15px;border-radius:15px;box-shadow:0 2px 5px rgba(0,0,0,0.05)"><div style="font-size:22px;color:#93370D;margin-bottom:5px">குளிகை</div><div style="font-size:24px;font-weight:600;color:#1E293B">{p['kuli']}</div></div>
        </div>"""
        
        panch_html = f"""<div class="sec" style="background:#FFF6D6;border-bottom:1px solid #FDE68A">
        <div class="t" style="color:#93370D;margin-bottom:10px">Hindu Calendar & Timings</div>
        <div style="font-size:28px;color:#B45309;margin-bottom:15px;font-weight:500">📅 {p['tamil_date']} &nbsp;|&nbsp; 🌙 {p['nakshatra']}</div>
        {sp}
        {time_grid}
        </div>"""
    
    items = "".join(f'<div class="row"><span class="i">{i}</span><span>{esc(t)}</span></div>' for i, t in d["advice"])
    sun = f'<div class="sec" style="display:flex;justify-content:space-around;font-size:26px;background:#F8FAFC"><span>🌅 Sunrise {fmt(d["sunrise"])}</span><span>🌇 Sunset {fmt(d["sunset"])}</span></div>'
    return template("Daily Guide & Advice", d, panch_html + sun + f'<div class="sec"><div class="t">Weather Advice</div>{items}</div>')

def card_events(d):
    today = "".join(f'<div class="row"><span class="i">{i["icon"]}</span><span><b>{esc(i["text"])}</b></span></div>' for i in d["today"])
    up = "".join(f'<div class="row"><span class="i">{i["icon"]}</span><span>{esc(i["text"])}<br><span style="font-size:22px;color:#667085">{i["date"]}</span></span><span class="when">{i["when"]}</span></div>' for i in d["upcoming"])
    content = ""
    if today: content += f'<div class="sec" style="background:#F0FDF4"><div class="t" style="color:#166534">Happening Today</div>{today}</div>'
    if up: content += f'<div class="sec"><div class="t">Upcoming Events & Bills</div>{up}</div>'
    if not content: content = '<div class="sec" style="font-size:26px;color:#667085">No upcoming events or bills in the next two weeks.</div>'
    return template("Family Calendar", d, content)

def build_birthday_html(name, age):
    age_line = f"Turns {age} today" if age else "Many happy returns"
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Outfit',sans-serif;width:800px}}
.b{{position:relative;overflow:hidden;width:800px;height:800px;color:#fff;text-align:center;
background:linear-gradient(160deg,#7A1FA2,#E5484D 55%,#FFB020);display:flex;flex-direction:column;justify-content:center;align-items:center;border-radius:40px;margin:20px}}
.e{{position:absolute;font-size:70px}}
.c{{font-size:180px;line-height:1}}
.h{{font-size:70px;font-weight:300;margin-top:15px}}
.n{{font-size:110px;font-weight:600;line-height:1.05;padding:0 40px}}
.a{{font-size:40px;font-weight:300;margin-top:15px}}
.f{{position:absolute;bottom:40px;font-size:26px;font-weight:300}}
</style></head><body><div class="b">
<span class="e" style="left:50px;top:50px">🎈</span><span class="e" style="right:60px;top:80px">🎉</span>
<span class="e" style="left:75px;bottom:110px">✨</span><span class="e" style="right:65px;bottom:125px">🎈</span>
<div class="c">🎂</div><div class="h">Happy Birthday</div><div class="n">{esc(name)}</div>
<div class="a">{esc(age_line)}</div><div class="f">With love from the family</div></div></body></html>"""

# ----------------------------------------------------------------- output

def render_png(html_str, path, selector=".card"):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 840, "height": 100})
        page.set_content(html_str)
        try:
            page.locator(selector).screenshot(path=path)
        except:
            page.locator(".b").screenshot(path=path)
        b.close()
    return path

def send_photo(path, cap):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat = os.environ["TELEGRAM_CHAT_ID"]
    with open(path, "rb") as f:
        requests.post(f"https://api.telegram.org/bot{token}/sendPhoto", data={"chat_id": chat, "caption": cap}, files={"photo": f}, timeout=60).raise_for_status()

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
    requests.post(f"https://api.telegram.org/bot{token}/sendMediaGroup", data={"chat_id": chat, "media": json.dumps(media)}, files=files, timeout=60).raise_for_status()

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

    for i in d["today"]:
        if i["kind"] == "birthday":
            try:
                path = render_png(build_birthday_html(i["name"], i["age"]), "birthday_card.png", ".b")
                send_photo(path, f"Happy Birthday {i['name']}!")
            except Exception as exc:
                print("Birthday card failed:", exc)

if __name__ == "__main__":
    main()
