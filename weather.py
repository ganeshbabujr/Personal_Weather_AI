"""Daily family briefing: weather card, events, holidays, birthday cards, storm watch.

Run daily:   python weather.py
Run as watch: python weather.py --watch      (only messages on severe alerts)
"""
import os
import sys
import html
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
    """Free, no key. Gives hourly rain chance, UV and a 5-day outlook. Optional."""
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
    # Calculates phase based on a known new moon (Jan 11, 2024, 11:57 UTC)
    ref = datetime(2024, 1, 11, 11, 57, tzinfo=timezone.utc)
    days = (dt - ref).total_seconds() / 86400
    phase = (days % 29.53058867) / 29.53058867
    if phase < 0.04 or phase > 0.96:
        return "Amavasya"
    if 0.46 < phase < 0.54:
        return "Purnima"
    return None


def fmt(dt):
    return dt.strftime("%I:%M %p").lstrip("0")


def fmt_h(h):
    return f"{h % 12 or 12}:00 {'AM' if h < 12 else 'PM'}"


def short_h(h):
    return f"{h % 12 or 12}{'A' if h < 12 else 'P'}"


def wmo_emoji(c):
    if c == 0:
        return "☀️"
    if c in (1, 2):
        return "🌤️"
    if c == 3:
        return "☁️"
    if c in (45, 48):
        return "🌫️"
    if 51 <= c <= 57 or c in (80, 81, 82):
        return "🌦️"
    if 61 <= c <= 67:
        return "🌧️"
    if 71 <= c <= 77 or c in (85, 86):
        return "❄️"
    if c >= 95:
        return "⛈️"
    return "🌤️"


def owm_emoji(main, night=False):
    if main == "Clear":
        return "🌙" if night else "☀️"
    return {"Clouds": "☁️", "Rain": "🌧️", "Drizzle": "🌦️", "Thunderstorm": "⛈️",
            "Snow": "❄️"}.get(main, "🌫️")


# ----------------------------------------------------------------- events

ICONS = {"birthday": "🎂", "anniversary": "💐", "event": "📌", "reminder": "⏰", "bill": "💳",
         "medicine": "💊", "pet": "🐾", "vehicle": "🚗", "exam": "📝", "holiday": "🏖️"}
FESTIVALS = ("diwali", "deepavali", "pongal", "holi", "eid", "christmas", "onam", "ugadi", "navratri",
             "dussehra", "ganesh", "independence day", "republic day", "new year", "vishu", "baisakhi",
             "raksha", "janmashtami", "makar", "gudi", "durga", "bakrid", "ramzan")


def load_events():
    try:
        with open("events.yaml", encoding="utf-8") as f:
            return yaml.safe_load(f) or []
    except FileNotFoundError:
        return []


def holiday_table(year, state):
    try:
        import holidays
        return holidays.country_holidays("IN", subdiv=state or None, years=[year, year + 1])
    except Exception as exc:
        print("Holidays unavailable:", exc)
        return {}


def matches(e, day):
    rep = e.get("repeat")
    if rep == "daily":
        return True
    if rep == "weekly":
        return day.strftime("%a") in [str(x)[:3].title() for x in e.get("days", [])]
    if rep == "monthly":
        return day.day == int(e.get("day", 0))
    return str(e.get("date", "")) in (day.isoformat(), day.strftime("%m-%d"))


def items_for(day, events, hol, upcoming=False):
    out = []
    for e in events:
        if not matches(e, day):
            continue
        rep = e.get("repeat")
        if upcoming and rep in ("daily", "weekly"):
            continue
        kind = e.get("type", "event")
        text, age = e["name"], None
        if e.get("year") and kind in ("birthday", "anniversary"):
            age = day.year - int(e["year"])
            text += f" turns {age}" if kind == "birthday" else f" ({age} years)"
        out.append({"icon": ICONS.get(kind, "📌"), "text": text, "kind": kind,
                    "name": e["name"], "age": age, "special": rep != "daily"})
    if day in hol:
        name = hol[day]
        if not upcoming and any(k in name.lower() for k in FESTIVALS):
            out.append({"icon": "🎉", "text": f"Happy {name}!", "kind": "holiday", "special": True})
        else:
            out.append({"icon": ICONS["holiday"], "text": f"Holiday: {name}", "kind": "holiday", "special": True})
    return out


# ----------------------------------------------------------------- data


def mini(key, zip_code):
    geo = owm(key, "/geo/1.0/zip", zip=zip_code)
    cur = owm(key, "/data/2.5/weather", lat=geo["lat"], lon=geo["lon"])
    return {"city": cur["name"], "temp": cur["main"]["temp"], "emoji": owm_emoji(cur["weather"][0]["main"])}


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

    def at(ts):
        return datetime.fromtimestamp(ts, tz)

    sunrise, sunset = at(cur["sys"]["sunrise"]), at(cur["sys"]["sunset"])
    night = now < sunrise or now > sunset
    slots = [s for s in fc["list"] if at(s["dt"]).date() == today and at(s["dt"]) + timedelta(hours=3) > now]

    d = {"city": cur["name"], "now": now, "temp": cur["main"]["temp"], "feels": cur["main"]["feels_like"],
         "humidity": cur["main"]["humidity"], "cond": cur["weather"][0]["description"].title(),
         "main": cur["weather"][0]["main"], "night": night, "sunrise": sunrise, "sunset": sunset,
         "aqi": aq["main"]["aqi"], "pm25": aq["components"]["pm2_5"], "moon": get_moon_phase(now)}
    d["t_min"] = min([s["main"]["temp_min"] for s in slots] + [d["temp"]])
    d["t_max"] = max([s["main"]["temp_max"] for s in slots] + [d["temp"]])

    # Hourly table: hour -> rain chance %, temp, uv
    hourly = {}
    if om:
        h = om["hourly"]
        for i, ts in enumerate(h["time"]):
            dt = datetime.fromisoformat(ts)
            if dt.date() == today:
                hourly[dt.hour] = {"pop": h["precipitation_probability"][i] or 0,
                                   "temp": h["temperature_2m"][i], "uv": h["uv_index"][i]}
    else:
        for s in fc["list"]:
            dt = at(s["dt"])
            if dt.date() == today:
                for k in range(3):
                    hourly[dt.hour + k] = {"pop": int(s.get("pop", 0) * 100), "temp": s["main"]["temp"], "uv": None}
    d["hourly"] = hourly

    # Rain window (first spell from now)
    wet = [hr for hr in sorted(hourly) if hr >= now.hour and hourly[hr]["pop"] >= 50]
    d["rain"] = None
    if wet:
        end = wet[0]
        while end + 1 in wet:
            end += 1
        run = [hourly[x]["pop"] for x in range(wet[0], end + 1)]
        d["rain"] = {"start": wet[0], "end": end + 1, "chance": max(run), "now": wet[0] <= now.hour}

    # Wind (m/s -> km/h)
    winds = [cur["wind"]["speed"], cur["wind"].get("gust", 0)]
    for s in slots:
        winds += [s["wind"]["speed"], s["wind"].get("gust", 0)]
    d["wind"] = max(winds) * 3.6

    # UV
    uvs = [(v["uv"], hr) for hr, v in hourly.items() if v["uv"] is not None]
    d["uv"], d["uv_hour"] = (max(uvs) if uvs else (None, None))

    # Best walk time
    d["walk"] = None
    if d["aqi"] <= 3:
        cands = [hr for hr in (5, 6, 7, 17, 18, 19) if hr in hourly and hr >= now.hour
                 and hourly[hr]["pop"] < 30 and (hourly[hr]["uv"] or 0) < 4]
        if cands:
            d["walk"] = min(cands, key=lambda x: hourly[x]["temp"])

    # 5-day outlook
    outlook = []
    if om:
        dd = om["daily"]
        for i in range(1, 6):
            outlook.append({"label": datetime.fromisoformat(dd["time"][i]).strftime("%a"),
                            "emoji": wmo_emoji(dd["weather_code"][i]),
                            "hi": dd["temperature_2m_max"][i], "lo": dd["temperature_2m_min"][i],
                            "pop": dd["precipitation_probability_max"][i] or 0})
    else:
        days = {}
        for s in fc["list"]:
            dt = at(s["dt"])
            if dt.date() > today:
                days.setdefault(dt.date(), []).append(s)
        for day, ss in list(days.items())[:5]:
            mid = min(ss, key=lambda s: abs(at(s["dt"]).hour - 12))
            outlook.append({"label": day.strftime("%a"), "emoji": owm_emoji(mid["weather"][0]["main"]),
                            "hi": max(s["main"]["temp_max"] for s in ss), "lo": min(s["main"]["temp_min"] for s in ss),
                            "pop": int(max(s.get("pop", 0) for s in ss) * 100)})
    d["outlook"] = outlook

    # Alerts
    limit = float(os.environ.get("WIND_LIMIT") or 60)
    alerts = []
    if d["wind"] >= limit:
        alerts.append(("red", "⚠️ HIGH WIND / CYCLONE ALERT. DO NOT GO OUTSIDE"))
    elif d["wind"] >= 40:
        alerts.append(("amber", "💨 Strong winds expected. Secure loose items"))
    if d["main"] == "Thunderstorm":
        alerts.append(("red", "⛈️ Thunderstorm. Stay indoors"))
    if d["aqi"] == 5:
        alerts.append(("red", "😷 Very poor air quality. Avoid outdoor activity"))
    if d["feels"] >= 41:
        alerts.append(("red", "🥵 Extreme heat. Stay indoors from 11 AM to 4 PM"))
    d["alerts"] = alerts

    # Events and holidays
    events = load_events()
    hol = holiday_table(today.year, os.environ.get("HOLIDAY_STATE"))
    d["today"] = items_for(today, events, hol)
    sunday = today.weekday() == 6
    up = []
    for i in range(1, 8):
        day = today + timedelta(days=i)
        for it in items_for(day, events, hol, upcoming=True):
            it["when"] = "tomorrow" if i == 1 else f"in {i} days"
            it["date"] = day.strftime("%a %d %b")
            up.append(it)
    d["sunday"] = sunday
    d["upcoming"] = up[:8 if sunday else 5]

    # Advice (Translated to Tamil)
    adv = []
    uv = d["uv"]
    if uv is not None and uv >= 8:
        adv.append(("🧴", f"மிக அதிக UV ({uv:.0f}). காலை 11 முதல் மதியம் 3 வரை வெயிலை தவிர்க்கவும்"))
    elif uv is not None and uv >= 6:
        adv.append(("🧴", f"அதிக UV ({uv:.0f}). தொப்பி அல்லது குடை பயன்படுத்தவும்"))
    elif uv is not None and uv >= 3:
        adv.append(("🕶️", "மிதமான UV. வெளியே சென்றால் கவனம் தேவை"))
        
    if d["feels"] >= 40:
        adv.append(("🥵", "கடுமையான வெப்பம். அடிக்கடி தண்ணீர் குடிக்கவும், நிழலில் ஓய்வெடுக்கவும்"))
    elif d["feels"] >= 35:
        adv.append(("☀️", "வெப்பமான நாள். போதுமான தண்ணீர் குடிக்கவும்"))
        
    if d["feels"] >= 32:
        adv.append(("👕", "மெல்லிய பருத்தி ஆடைகளை அணியவும்"))
    elif d["feels"] <= 18:
        adv.append(("🧥", "குளிர்ச்சி: ஸ்வெட்டர்/ஜாக்கெட் எடுத்துச் செல்லவும்"))
    else:
        adv.append(("👚", "சாதாரண ஆடைகளே போதுமானது"))
        
    if d["rain"]:
        adv.append(("☔", "மழை வர வாய்ப்புள்ளது: குடை எடுத்துச் செல்லவும்"))
        adv.append(("🧺", "இன்று வெளியே துணி காயவைக்க வேண்டாம்"))
        if d["humidity"] >= 75:
            adv.append(("🦟", "கொசுக்கள்: வீட்டைச் சுற்றி தண்ணீர் தேங்காமல் பார்க்கவும்"))
    else:
        adv.append(("🧺", "துணிகளை வெளியே காயவைக்க நல்ல நாள்"))
        
    if d["aqi"] >= 4:
        adv.append(("😷", "காற்று மாசடைந்துள்ளது. வெளியே செல்லும் போது மாஸ்க் அணியவும்"))
        
    for var, label in (("SCHOOL_DROP", "பள்ளி செல்லும்"), ("SCHOOL_PICKUP", "பள்ளி முடியும்")):
        t = os.environ.get(var)
        if t and d["rain"]:
            hr, mn = (int(x) for x in (t.split(":") + ["0"])[:2])
            if d["rain"]["start"] <= hr < d["rain"]["end"]:
                adv.append(("🎒", f"{label} நேரத்தில் மழை வரலாம் ({hr % 12 or 12}:{mn:02d} {'AM' if hr < 12 else 'PM'}). குடை கொடுத்தனுப்பவும்"))
                
    watch = [w.strip().lower() for w in (os.environ.get("WATCH") or "").split(",") if w.strip()]
    if "elders" in watch and d["feels"] >= 35:
        adv.append(("👵", "பெரியவர்கள்: வெயிலில் செல்ல வேண்டாம், அடிக்கடி நீர் அருந்தவும்"))
    if "asthma" in watch and d["aqi"] >= 3:
        adv.append(("🫁", "ஆஸ்துமா: இன்ஹேலரை அருகில் வைத்திருக்கவும், தூசியை தவிர்க்கவும்"))
    if "kids" in watch and (d["rain"] or d["feels"] >= 38):
        adv.append(("🧒", "குழந்தைகள்: இன்று வீட்டிற்குள்ளேயே விளையாடவும்"))
        
    if d["walk"] is not None:
        adv.append(("🚶", f"நடைபயிற்சிக்கு சிறந்த நேரம்: {fmt_h(d['walk'])}"))
    d["advice"] = adv

    # Other places family lives
    d["extra"] = []
    for z in [z.strip() for z in (os.environ.get("EXTRA_ZIPS") or "").split(";") if z.strip()]:
        try:
            d["extra"].append(mini(key, z))
        except Exception as exc:
            print("Extra location failed:", z, exc)

    d["quiet"] = not d["alerts"] and not d["rain"] and not any(i["special"] for i in d["today"])
    return d


# ----------------------------------------------------------------- card design

FONT = "https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600&display=swap"
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Outfit','Noto Sans','DejaVu Sans',Arial,'Noto Color Emoji',sans-serif;background:#fff}
#card{width:800px;background:#fff;color:#0F172A;line-height:1.3}
.hero{position:relative;overflow:hidden;color:#fff;padding:50px 45px 100px;background:linear-gradient(165deg,var(--a),var(--b))}
.hero::before{content:"";position:absolute;right:-100px;top:-120px;width:450px;height:450px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.30),rgba(255,255,255,0) 68%)}
.top{position:relative;display:flex;justify-content:space-between;align-items:baseline}
.city{font-size:36px;font-weight:600}
.date{font-size:26px;font-weight:300}
.main{position:relative;display:flex;justify-content:space-between;align-items:center;margin-top:20px}
.temp{font-size:180px;font-weight:200;line-height:.95;letter-spacing:-6px}
.ico{font-size:140px;line-height:1}
.cond{font-size:42px;font-weight:500;margin-top:8px}
.sub{font-size:26px;font-weight:300;margin-top:8px}
.chips{position:relative;display:flex;gap:12px;margin-top:28px;flex-wrap:wrap}
.chip{background:rgba(255,255,255,.2);border-radius:40px;padding:10px 20px;font-size:24px}
.sheet{position:relative;margin-top:-50px;background:#fff;border-radius:50px 50px 0 0;padding-top:25px}
.al{margin:0 45px 15px;padding:20px 25px;border-radius:20px;font-size:32px;font-weight:600}
.red{background:#D92D20;color:#fff}
.amber{background:#FEF0C7;color:#93370D}
.today{margin:0 45px 10px;background:#FFF6D6;border-radius:24px;padding:24px 28px 18px}
.sec{padding:30px 45px}
.today+.sec,.al+.sec,.sheet>.sec:first-child{border-top:0}
.sec+.sec{border-top:1px solid #EAECF0}
.t{font-size:28px;font-weight:500;color:#475467;margin-bottom:16px}
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
.row{display:flex;align-items:center;gap:18px;font-size:28px;padding:8px 0}
.row .i{width:45px;text-align:center;font-size:32px}
.when{margin-left:auto;background:#F2F4F7;border-radius:20px;padding:5px 16px;font-size:22px;color:#475467;white-space:nowrap}
.sun{display:flex;gap:35px;font-size:26px;flex-wrap:wrap}
.sun span b{font-weight:500}
.out{display:grid;grid-template-columns:repeat(5,1fr);text-align:center}
.out .dn{font-size:25px;color:#475467}
.out .e{font-size:46px;margin:5px 0}
.out .h{font-size:26px;font-weight:600}
.out .l{font-size:22px;color:#667085}
.out .p{font-size:19px;color:#175CD3;margin-top:2px;height:22px}
.foot{padding:20px 45px 35px;font-size:22px;color:#98A2B3}
"""

THEMES = {"night": ("#101B3A", "#2D3F73"), "Clear": ("#1F6FEB", "#62B0FF"), "Clouds": ("#475A78", "#8296B4"),
          "Rain": ("#2F3F5A", "#5F7498"), "Drizzle": ("#3A4C68", "#6F86A8"),
          "Thunderstorm": ("#241F3A", "#4B4672"), "Snow": ("#5E7392", "#A5B8D2")}


def theme(d):
    if d["night"] and d["main"] == "Clear":
        return THEMES["night"]
    return THEMES.get(d["main"], THEMES["Clouds"])


def rows(items):
    return "".join(f'<div class="row"><span class="i">{i["icon"]}</span><span>{esc(i["text"])}</span></div>' for i in items)


def build_html(d):
    a, b = theme(d)
    now = d["now"]
    icon = owm_emoji(d["main"], d["night"])
    chips = "".join(f'<span class="chip">{c["emoji"]} {esc(c["city"])} {c["temp"]:.0f}°</span>' for c in d["extra"])
    hero = f"""<div class="hero" style="--a:{a};--b:{b}">
  <div class="top"><span class="city">{esc(d['city'])}</span><span class="date">{now.strftime('%A, %d %b')}</span></div>
  <div class="main"><div><div class="temp">{d['temp']:.0f}°</div><div class="cond">{esc(d['cond'])}</div>
  <div class="sub">Feels {d['feels']:.0f}°, high {d['t_max']:.0f}°, low {d['t_min']:.0f}°</div></div><div class="ico">{icon}</div></div>
  {f'<div class="chips">{chips}</div>' if chips else ''}</div>"""

    alerts = "".join(f'<div class="al {lvl}">{esc(t)}</div>' for lvl, t in d["alerts"])
    today = f'<div class="today"><div class="t" style="margin-bottom:6px">Today</div>{rows(d["today"])}</div>' if d["today"] else ""

    # stats
    if d["rain"]:
        r = d["rain"]
        rain_v = "Now" if r["now"] else fmt_h(r["start"])
        rain_d = f"{r['chance']}% till {fmt_h(r['end'])}"
    else:
        rain_v, rain_d = "Dry", "No rain today"
    wcol = "#D92D20" if d["wind"] >= 60 else "#B54708" if d["wind"] >= 40 else "#0F172A"
    wnote = "Dangerous" if d["wind"] >= 60 else "Strong" if d["wind"] >= 40 else "Calm to breezy"
    aqi_name = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very poor"}[d["aqi"]]
    acol = {1: "#067647", 2: "#4D7C0F", 3: "#B54708", 4: "#D92D20", 5: "#7A1FA2"}[d["aqi"]]
    if d["uv"] is None:
        uv_v, uv_d, ucol = f"{d['humidity']}%", "Humidity", "#0F172A"
        uv_k = "💧 Humid"
    else:
        uv_v = f"{d['uv']:.0f}"
        uv_d = "Very high" if d["uv"] >= 8 else "High" if d["uv"] >= 6 else "Moderate" if d["uv"] >= 3 else "Low"
        ucol = "#D92D20" if d["uv"] >= 8 else "#B54708" if d["uv"] >= 6 else "#0F172A"
        uv_k = "🧴 UV peak"
    stats = f"""<div class="sec"><div class="stats">
  <div class="st"><div class="k">🌧️ Rain</div><div class="v">{rain_v}</div><div class="d">{rain_d}</div></div>
  <div class="st"><div class="k">💨 Wind</div><div class="v" style="color:{wcol}">{d['wind']:.0f}</div><div class="d">km/h, {wnote}</div></div>
  <div class="st"><div class="k">🫁 Air</div><div class="v" style="color:{acol}">{aqi_name}</div><div class="d">AQI {d['aqi']}, PM2.5 {d['pm25']:.0f}</div></div>
  <div class="st"><div class="k">{uv_k}</div><div class="v" style="color:{ucol}">{uv_v}</div><div class="d">{uv_d}</div></div>
  </div></div>"""

    # hourly rain strip (hidden on quiet days)
    strip = ""
    hrs = [h for h in range(6, 22) if h in d["hourly"]]
    if not d["quiet"] and hrs:
        cols = ""
        for h in hrs:
            p = d["hourly"][h]["pop"]
            color = "#2E90FA" if p >= 50 else "#B2DDFF" if p >= 20 else "#E4E7EC"
            lab = short_h(h) if h % 3 == 0 else ""
            cols += f'<div class="col"><div class="bar" style="height:{max(8, p * 1.2):.0f}px;background:{color}"></div><div class="lab">{lab}</div></div>'
        if d["rain"]:
            r = d["rain"]
            call = "High chance of rain now" if r["now"] else f"Expected around {fmt_h(r['start'])}"
            call += f", {r['chance']}% chance"
        else:
            call = "Dry through the day"
        strip = f'<div class="sec"><div class="t">Rain chance by hour</div><div class="bars">{cols}</div><div class="call">{call}</div></div>'

    moon_str = f'<span>🌙 Phase <b>{d["moon"]}</b></span>' if d.get("moon") else ""
    sun = f'<span>🌅 Sunrise <b>{fmt(d["sunrise"])}</b></span><span>🌇 Sunset <b>{fmt(d["sunset"])}</b></span>{moon_str}'
    sunsec = f'<div class="sec"><div class="sun">{sun}</div></div>'

    advice = f'<div class="sec"><div class="t">Today\'s advice</div>{rows([{"icon": i, "text": t} for i, t in d["advice"][:4 if d["quiet"] else 9]])}</div>'

    out = ""
    if d["outlook"]:
        cells = "".join(
            f'<div><div class="dn">{o["label"]}</div><div class="e">{o["emoji"]}</div>'
            f'<div class="h">{o["hi"]:.0f}°</div><div class="l">{o["lo"]:.0f}°</div>'
            f'<div class="p">{"💧" + str(o["pop"]) + "%" if o["pop"] >= 40 else ""}</div></div>' for o in d["outlook"])
        out = f'<div class="sec"><div class="t">Next 5 days</div><div class="out">{cells}</div></div>'

    up = ""
    if d["upcoming"]:
        title = "Week ahead" if d["sunday"] else "Coming up"
        body = "".join(f'<div class="row"><span class="i">{i["icon"]}</span><span>{esc(i["text"])}'
                       f'<br><span style="font-size:21px;color:#667085">{i["date"]}</span></span>'
                       f'<span class="when">{i["when"]}</span></div>' for i in d["upcoming"])
        up = f'<div class="sec"><div class="t">{title}</div>{body}</div>'

    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}"><style>{CSS}</style></head><body>
<div id="card">{hero}<div class="sheet">{alerts}{today}{stats}{strip}{sunsec}{advice}{out}{up}<div class="foot">Updated {fmt(now)}</div></div></div></body></html>"""


def build_birthday_html(name, age):
    age_line = f"Turns {age} today" if age else "Many happy returns"
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Outfit','Noto Sans',Arial,'Noto Color Emoji',sans-serif}}
#b{{position:relative;overflow:hidden;width:800px;height:800px;color:#fff;text-align:center;
background:linear-gradient(160deg,#7A1FA2,#E5484D 55%,#FFB020);display:flex;flex-direction:column;justify-content:center;align-items:center}}
.e{{position:absolute;font-size:70px}}
.c{{font-size:180px;line-height:1}}
.h{{font-size:70px;font-weight:300;margin-top:15px}}
.n{{font-size:110px;font-weight:600;line-height:1.05;padding:0 40px}}
.a{{font-size:40px;font-weight:300;margin-top:15px}}
.f{{position:absolute;bottom:40px;font-size:26px;font-weight:300}}
</style></head><body><div id="b">
<span class="e" style="left:50px;top:50px">🎈</span><span class="e" style="right:60px;top:80px">🎉</span>
<span class="e" style="left:75px;bottom:110px">✨</span><span class="e" style="right:65px;bottom:125px">🎈</span>
<div class="c">🎂</div><div class="h">Happy Birthday</div><div class="n">{esc(name)}</div>
<div class="a">{esc(age_line)}</div><div class="f">With love from the family</div></div></body></html>"""


# ----------------------------------------------------------------- output


def render_png(page_html, path, selector="#card"):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 800, "height": 1200})
        try:
            page.set_content(page_html, wait_until="networkidle")
            page.evaluate("document.fonts.ready")
        except Exception:
            page.set_content(page_html)
        page.locator(selector).screenshot(path=path)
        browser.close()
    return path


def caption(d):
    c = f"{d['city']}: {d['temp']:.0f}°C, {d['cond']}."
    if d["rain"]:
        c += " Rain " + ("now." if d["rain"]["now"] else f"around {fmt_h(d['rain']['start'])}.")
    for lvl, t in d["alerts"]:
        if lvl == "red":
            c += f" {t.rstrip('.!')}."
    for i in d["today"]:
        if i["special"]:
            c += f" {i['text'].rstrip('.!')}."
    return c[:1000]


def tg(method, **kw):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    r = requests.post(f"https://api.telegram.org/bot{token}/{method}", timeout=60, **kw)
    r.raise_for_status()


def send_photo(path, cap):
    chat = os.environ["TELEGRAM_CHAT_ID"]
    with open(path, "rb") as f:
        tg("sendPhoto", data={"chat_id": chat, "caption": cap}, files={"photo": f})


def send_text(text):
    tg("sendMessage", json={"chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": text})


def run_watch(d):
    red = [t for lvl, t in d["alerts"] if lvl == "red"]
    if red:
        send_text(f"{d['city']} ALERT\n" + "\n".join(red))
        print("Alert sent.")
    else:
        print("No severe alert.")


def main():
    d = collect()
    if "--watch" in sys.argv:
        run_watch(d)
        return
    page_html = build_html(d)
    with open("card.html", "w", encoding="utf-8") as fh:
        fh.write(page_html)
    try:
        send_photo(render_png(page_html, "card.png"), caption(d))
    except Exception as exc:
        print("Card render failed, sending text:", exc)
        send_text(caption(d))
    for i in d["today"]:
        if i["kind"] == "birthday":
            try:
                path = render_png(build_birthday_html(i["name"], i["age"]), "birthday_card.png", "#b")
                send_photo(path, f"Happy Birthday {i['name']}!")
            except Exception as exc:
                print("Birthday card failed:", exc)
                send_text(f"Happy Birthday {i['name']}!")
    print("Done.")


if __name__ == "__main__":
    main()
