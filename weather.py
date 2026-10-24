"""Daily family briefing: 3-card layout + Rain Watch + 1-min intervals + Gold Rates.

Run daily:   python weather.py
Run as watch: python weather.py --watch
"""
import os, sys, time, json, requests, yaml, html
from datetime import datetime, timezone, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import ui

# Setup resilient API connection
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

def owm_emoji(main, night=False):
    if main == "Clear": return "🌙" if night else "☀️"
    return {"Clouds": "☁️", "Rain": "🌧️", "Drizzle": "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️"}.get(main, "🌫️")

def get_metals():
    key = os.environ.get("GOLD_API_KEY")
    if not key: return None
    try:
        g = session.get("https://www.goldapi.io/api/XAU/INR", headers={"x-access-token": key}, timeout=10).json()
        s = session.get("https://www.goldapi.io/api/XAG/INR", headers={"x-access-token": key}, timeout=10).json()
        return {"gold22": int((g["price"] / 31.103) * 0.916), "silver": int(s["price"] / 31.103)}
    except: return None

def openmeteo(lat, lon):
    try:
        r = session.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat, "longitude": lon, "timezone": "auto", "forecast_days": 6,
            "hourly": "precipitation_probability,temperature_2m,uv_index",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        }, timeout=20)
        r.raise_for_status()
        return r.json()
    except: return None

def get_panchangam(dt, sunrise, sunset):
    try:
        import ephem
        import math
    except ImportError:
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
        tithi_name = ["Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadasi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
                      "Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadasi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"][int(((moon_deg - sun_deg) % 360) / 12.0)]

        if tithi_name == "Amavasya": special.add("🌑 Amavasya (அமாவாசை)")
        if tithi_name == "Purnima": special.add("🌕 Pournami (பௌர்ணமி)")
        if tithi_name == "Ekadasi": special.add("🙏 Ekadasi (ஏகாதசி) - Fasting day")
        if tithi_name == "Trayodashi": special.add(f"🛕 {'Sani ' if check_time.weekday() == 5 else ''}Pradosham (பிரதோஷம்)")
        if tithi_name == "Chaturthi": special.add("🐘 Chaturthi (சதுர்த்தி)")
        if tithi_name == "Shashti": special.add("🦚 Shashti (சஷ்டி)")
        if tithi_name in ["Ashtami", "Navami"]: special.add(f"⚠️ {tithi_name} ({'அஷ்டமி' if tithi_name=='Ashtami' else 'நவமி'})")

        nak_name = ["Aswini", "Bharani", "Karthigai", "Rohini", "Mrigasira", "Arudra", "Punarvasu", "Pushya", "Ashlesha",
                    "Magam", "Pooram", "Uthiram", "Hastham", "Chithirai", "Swathi", "Visakam", "Anusham", "Kettai",
                    "Moolam", "Pooradam", "Uthiradam", "Thiruvonam", "Avittam", "Sadayam", "Poorattadhi", "Uthirattadhi", "Revathi"][int(((moon_deg - 24.15) % 360) / (360/27.0))]
        nak_names.add(nak_name)
        if nak_name == "Karthigai": special.add("🪔 Kiruthigai (கிருத்திகை)")
        if nak_name == "Thiruvonam": special.add("🌸 Thiruvonam (திருவோணம்)")

    obs.date = dt.replace(hour=12).astimezone(timezone.utc)
    sun.compute(obs)
    nirayana_sun = (math.degrees(ephem.Ecliptic(sun).lon) - 24.15) % 360
    
    day_idx = dt.weekday()
    part_dur = (sunset - sunrise) / 8
    def get_time(p): return f"{(sunrise + (part_dur * p)).strftime('%I:%M %p').lstrip('0')} - {(sunrise + (part_dur * (p+1))).strftime('%I:%M %p').lstrip('0')}"

    return {
        "special": sorted(list(special)),
        "nakshatra": " / ".join(sorted(list(nak_names))),
        "tamil_date": f"{['Chithirai', 'Vaikasi', 'Aani', 'Aadi', 'Avani', 'Purattasi', 'Aippasi', 'Karthigai', 'Margazhi', 'Thai', 'Masi', 'Panguni'][int(nirayana_sun / 30)]} {int((nirayana_sun % 30) / 0.9856) + 1}",
        "rahu": get_time([1, 6, 4, 5, 3, 2, 7][day_idx]), "yama": get_time([3, 2, 1, 0, 6, 5, 4][day_idx]), "kuli": get_time([5, 4, 3, 2, 1, 0, 6][day_idx]),
        "nalla": ["6:30 AM - 7:30 AM, 4:30 PM - 5:30 PM", "7:30 AM - 8:30 AM, 4:30 PM - 5:30 PM", "9:00 AM - 10:00 AM, 4:30 PM - 5:30 PM", "10:30 AM - 11:30 AM, 12:00 PM - 1:00 PM", "9:30 AM - 10:30 AM, 4:30 PM - 5:30 PM", "7:30 AM - 8:30 AM, 4:30 PM - 5:30 PM", "7:30 AM - 8:30 AM, 3:30 PM - 4:30 PM"][day_idx]
    }

def load_events():
    try:
        with open("events.yaml", encoding="utf-8") as f: return yaml.safe_load(f) or []
    except: return []

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
    ICONS = {"birthday": "🎂", "anniversary": "💐", "event": "📌", "reminder": "⏰", "bill": "💳", "temple": "🛕", "holiday": "🏖️"}
    for e in events:
        if not matches(e, day): continue
        if upcoming and e.get("repeat") in ("daily", "weekly"): continue
        kind = e.get("type", "event")
        text, age = e["name"], None
        if e.get("year") and kind in ("birthday", "anniversary"):
            age = day.year - int(e["year"])
            text += f" turns {age}" if kind == "birthday" else f" ({age} years)"
        out.append({"icon": ICONS.get(kind, "📌"), "text": text, "kind": kind, "name": e["name"], "age": age})
    if day in hol:
        out.append({"icon": "🎉" if any(k in hol[day].lower() for k in ("diwali","deepavali","pongal","holi","eid","christmas","onam","ugadi","navratri","dussehra","ganesh","new year")) else ICONS.get("holiday", "🏖️"), "text": hol[day], "kind": "holiday"})
    return out

def collect():
    key = os.environ["OWM_API_KEY"]
    zip_code = os.environ.get("ZIP_CODE") or "600001,IN"
    geo = session.get(f"https://api.openweathermap.org/geo/1.0/zip?zip={zip_code}&appid={key}").json()
    lat, lon = geo["lat"], geo["lon"]
    cur = session.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={key}").json()
    fc = session.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={key}").json()
    aq = session.get(f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={key}").json()["list"][0]
    om = openmeteo(lat, lon)

    tz = timezone(timedelta(seconds=fc["city"]["timezone"]))
    now = datetime.now(tz)
    today = now.date()
    def at(ts): return datetime.fromtimestamp(ts, tz)

    sunrise, sunset = at(cur["sys"]["sunrise"]), at(cur["sys"]["sunset"])
    night = now < sunrise or now > sunset
    slots = [s for s in fc["list"] if at(s["dt"]).date() == today and at(s["dt"]) + timedelta(hours=3) > now]

    d = {"city": cur["name"], "now": now, "temp": cur["main"]["temp"], "feels": cur["main"]["feels_like"], "cond": cur["weather"][0]["description"].title(),
         "main": cur["weather"][0]["main"], "night": night, "sunrise": sunrise, "sunset": sunset, "icon": owm_emoji(cur["weather"][0]["main"], night),
         "aqi": aq["main"]["aqi"], "pm25": aq["components"]["pm2_5"], "panchangam": get_panchangam(now, sunrise, sunset), "metals": get_metals()}
    
    d["t_min"] = min([s["main"]["temp_min"] for s in slots] + [d["temp"]])
    d["t_max"] = max([s["main"]["temp_max"] for s in slots] + [d["temp"]])

    hourly = {}
    if om:
        h = om["hourly"]
        for i, ts in enumerate(h["time"]):
            dt = datetime.fromisoformat(ts)
            if dt.date() == today: hourly[dt.hour] = {"pop": h["precipitation_probability"][i] or 0, "uv": h["uv_index"][i]}
    d["hourly"] = hourly

    wet = [hr for hr in sorted(hourly) if hr >= now.hour and hourly[hr]["pop"] >= 50]
    d["rain"] = None
    if wet:
        end = wet[0]
        while end + 1 in wet: end += 1
        d["rain"] = {"start": wet[0], "end": end + 1, "chance": max([hourly[x]["pop"] for x in range(wet[0], end + 1)]), "now": wet[0] <= now.hour}

    d["wind"] = max([cur["wind"]["speed"], cur["wind"].get("gust", 0)] + [s["wind"]["speed"] for s in slots]) * 3.6
    uvs = [(v["uv"], hr) for hr, v in hourly.items() if v["uv"] is not None]
    d["uv"] = max(uvs)[0] if uvs else 0

    d["alerts"] = []
    if d["wind"] >= float(os.environ.get("WIND_LIMIT") or 60): d["alerts"].append(("red", "⚠️ HIGH WIND ALERT. DO NOT GO OUTSIDE"))
    if d["aqi"] == 5: d["alerts"].append(("red", "😷 Very poor air quality. Avoid outdoor activity"))

    events = load_events()
    hol = holiday_table(today.year, os.environ.get("HOLIDAY_STATE"))
    d["today"] = items_for(today, events, hol)
    
    d["upcoming"] = []
    for i in range(1, 31):
        day = today + timedelta(days=i)
        for it in items_for(day, events, hol, upcoming=True):
            it["when"] = "tomorrow" if i == 1 else f"in {i} days"
            d["upcoming"].append(it)
    d["upcoming"] = d["upcoming"][:8] 

    adv = []
    if d["uv"] and d["uv"] >= 6: adv.append(("🧴", f"அதிக UV ({d['uv']:.0f}). குடை பயன்படுத்தவும்"))
    if d["feels"] >= 35: adv.append(("☀️", "வெப்பமான நாள். போதுமான தண்ணீர் குடிக்கவும்"))
    if d["rain"]:
        adv.append(("☔", f"{'இப்போது' if d['rain']['now'] else f'{d['rain']['start'] % 12 or 12}:00 அளவில்'} மழை வரலாம்: குடை எடுத்துச் செல்லவும்"))
        adv.append(("🧺", "இன்று வெளியே துணி காயவைக்க வேண்டாம்"))
    else: adv.append(("🧺", "துணிகளை வெளியே காயவைக்க நல்ல நாள்"))
    d["advice"] = adv

    d["theme"] = "festival" if any(any(f in str(e).lower() for f in ["diwali","deepavali","pongal","new year","ugadi","navratri"]) for e in d["today"]) else "default"
    return d

def render_png(html_str, path, selector=".card"):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 840, "height": 100})
        page.set_content(html_str)
        try: page.locator(selector).screenshot(path=path)
        except:
            try: page.locator(".rain-bg").screenshot(path=path)
            except: page.locator(".b").screenshot(path=path)
        b.close()
    return path

def send_photo(path, cap):
    with open(path, "rb") as f:
        session.post(f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendPhoto", data={"chat_id": os.environ['TELEGRAM_CHAT_ID'], "caption": cap}, files={"photo": f}, timeout=60).raise_for_status()

def main():
    d = collect()
    
    if "--watch" in sys.argv:
        alerts = [t for l, t in d["alerts"] if l == "red"]
        rain_alert = d["rain"] and ((d["rain"]["start"] - d["now"].hour) % 24) <= 1
                
        if alerts:
            session.post(f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage", json={"chat_id": os.environ['TELEGRAM_CHAT_ID'], "text": "⚠️ ALERT!\n" + "\n".join(alerts)})
        if rain_alert:
            render_png(ui.card_rain_alert(d), "alert.png", ".rain-bg")
            send_photo("alert.png", f"⚠️ Sudden Rain Watch for {d['city']}: High chance of rain expected shortly!")
        return

    session.post(f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage", json={"chat_id": os.environ['TELEGRAM_CHAT_ID'], "text": f"☀️ Good Morning Family! Here is your daily briefing for {d['now'].strftime('%A, %B %d')}."})
    
    render_png(ui.card_weather(d), "weather.png")
    send_photo("weather.png", "1/3: Today's Weather & Outlook 🌦️")
    time.sleep(60)

    render_png(ui.card_advice(d), "advice.png")
    send_photo("advice.png", "2/3: Panchangam & Daily Advice 🪷")
    time.sleep(60)

    render_png(ui.card_events(d), "events.png")
    send_photo("events.png", "3/3: Upcoming Events & Bills 📅")

    for i in d["today"]:
        if i["kind"] == "birthday":
            try:
                render_png(ui.build_birthday_html(i["name"], i["age"]), "birthday.png", ".b")
                send_photo("birthday.png", f"Happy Birthday {i['name']}! 🎉")
            except: pass

if __name__ == "__main__":
    main()
