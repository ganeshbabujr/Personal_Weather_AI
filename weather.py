"""Daily family briefing: Premium Dashboard + Rain Watch + Gold Rates + Countdowns.

Run daily:   python weather.py
Run as watch: python weather.py --watch
"""
import os, sys, time, json, requests, csv, html
from datetime import datetime, timezone, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import ui

# Setup resilient API connection
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

def get_metals():
    try:
        with open("metals.json", "r") as f: return json.load(f)
    except FileNotFoundError: pass

    key = os.environ.get("GOLD_API_KEY")
    if not key: return None
    try:
        g = session.get("https://www.goldapi.io/api/XAU/INR", headers={"x-access-token": key}, timeout=10).json()
        s = session.get("https://www.goldapi.io/api/XAG/INR", headers={"x-access-token": key}, timeout=10).json()
        data = {"gold22": int((g["price"] / 31.103) * 0.916), "silver": int(s["price"] / 31.103)}
        with open("metals.json", "w") as f: json.dump(data, f)
        return data
    except: return None

def openmeteo(lat, lon):
    try:
        r = session.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat, "longitude": lon, "timezone": "auto", "forecast_days": 6,
            "hourly": "precipitation_probability,temperature_2m,uv_index,cloud_cover",
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
        return {}

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
        if tithi_name == "Ekadasi": special.add("🙏 Ekadasi (ஏகாதசி)")
        if tithi_name == "Trayodashi": special.add(f"🛕 {'Sani ' if check_time.weekday() == 5 else ''}Pradosham (பிரதோஷம்)")
        if tithi_name == "Chaturthi": special.add("🐘 Chaturthi (சதுர்த்தி)")
        if tithi_name == "Shashti": special.add("🦚 Shashti (சஷ்டி)")

        nak_name = ["Aswini", "Bharani", "Karthigai", "Rohini", "Mrigasira", "Arudra", "Punarvasu", "Pushya", "Ashlesha",
                    "Magam", "Pooram", "Uthiram", "Hastham", "Chithirai", "Swathi", "Visakam", "Anusham", "Kettai",
                    "Moolam", "Pooradam", "Uthiradam", "Thiruvonam", "Avittam", "Sadayam", "Poorattadhi", "Uthirattadhi", "Revathi"][int(((moon_deg - 24.15) % 360) / (360/27.0))]
        nak_names.add(nak_name)

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
        "nalla": ["6:30-7:30 AM", "7:30-8:30 AM", "9:00-10:00 AM", "10:30-11:30 AM", "9:30-10:30 AM", "7:30-8:30 AM", "7:30-8:30 AM"][day_idx]
    }

def load_events():
    events = []
    sheet_url = os.environ.get("SHEET_CSV_URL")
    if sheet_url:
        try:
            r = session.get(sheet_url, timeout=10)
            r.raise_for_status()
            r.encoding = 'utf-8'
            reader = csv.DictReader(r.text.splitlines())
            for row in reader:
                if not row.get("name"): continue
                events.append({
                    "name": row["name"].strip(),
                    "date": row.get("date", "").strip(),
                    "type": row.get("type", "event").strip().lower(),
                    "repeat": row.get("repeat", "").strip().lower(),
                    "year": row.get("year", "").strip(),
                    "day": row.get("day", "").strip()
                })
        except Exception as e:
            print("Failed to load Google Sheet:", e)
    return events

def matches(e, day):
    rep = e.get("repeat")
    if rep == "daily": return True
    if rep == "monthly": return str(day.day) == str(e.get("day", ""))
    if rep == "bimonthly_odd": return str(day.day) == str(e.get("day", "")) and day.month % 2 != 0
    if rep == "bimonthly_even": return str(day.day) == str(e.get("day", "")) and day.month % 2 == 0
    if rep == "yearly": return str(e.get("date", "")) in (day.isoformat(), day.strftime("%m-%d"))
    return str(e.get("date", "")) == day.isoformat()

def holiday_table(year, state):
    try:
        import holidays
        return holidays.country_holidays("IN", subdiv=state or None, years=[year, year + 1])
    except: return {}

def items_for(day, events, hol, upcoming=False):
    out = []
    ICONS = {"birthday": "🎂", "anniversary": "💐", "event": "📌", "reminder": "⏰", "bill": "⚡", "temple": "🛕", "holiday": "🏖️"}
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
        out.append({"icon": "🎉" if any(k in hol[day].lower() for k in ("diwali","deepavali","pongal","holi","new year")) else ICONS.get("holiday", "🏖️"), "text": hol[day], "kind": "holiday"})
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
         "main": cur["weather"][0]["main"], "night": night, "sunrise": sunrise, "sunset": sunset, 
         "aqi": aq["main"]["aqi"], "pm25": aq["components"]["pm2_5"], "panchangam": get_panchangam(now, sunrise, sunset), "metals": get_metals()}
    
    d["t_min"] = min([s["main"]["temp_min"] for s in slots] + [d["temp"]])
    d["t_max"] = max([s["main"]["temp_max"] for s in slots] + [d["temp"]])

    hourly = {}
    if om:
        h = om["hourly"]
        for i, ts in enumerate(h["time"]):
            dt = datetime.fromisoformat(ts)
            if dt.date() == today: hourly[dt.hour] = {"pop": h["precipitation_probability"][i] or 0, "uv": h["uv_index"][i], "temp": h["temperature_2m"][i], "cloud": h["cloud_cover"][i]}
    d["hourly"] = hourly
    d["humidity"] = cur["main"].get("humidity")

    d["daily"] = []
    if om:
        dl = om["daily"]
        for i in range(1, len(dl["time"])):
            d["daily"].append({"date": datetime.fromisoformat(dl["time"][i]).date(), "code": dl["weather_code"][i],
                               "max": dl["temperature_2m_max"][i], "min": dl["temperature_2m_min"][i],
                               "pop": dl["precipitation_probability_max"][i] or 0})

    wet = [hr for hr in sorted(hourly) if hr >= now.hour and hourly[hr]["pop"] >= 20]
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
            it["days_left"] = i 
            d["upcoming"].append(it)
    d["upcoming"] = d["upcoming"][:8] 

    adv = []
    if d["uv"] and d["uv"] >= 6: adv.append(("☀️", f"High UV ({d['uv']:.0f}). Please use sun protection or an umbrella."))
    if d["feels"] >= 35: adv.append(("🌡️", "It's feeling quite hot today. Stay hydrated."))
    if d["rain"]:
        adv.append(("☔", f"{'Rain expected right now' if d['rain']['now'] else 'Rain expected around ' + ui.fmt_h(d['rain']['start'])}. Take an umbrella."))
        adv.append(("🧺", "Not a good day to dry clothes outside."))
    else: adv.append(("🧺", "Dry day ahead—good for drying clothes outside."))
    if d["aqi"] >= 4: adv.append(("😷", "Air quality is poor. Elders and children should stay indoors or wear a mask."))
    if 40 <= d["wind"] < float(os.environ.get("WIND_LIMIT") or 60): adv.append(("💨", f"Strong winds up to {d['wind']:.0f} km/h. Secure loose items and be careful on two-wheelers."))
    if d["feels"] <= 20: adv.append(("🧥", "It feels cool today. Keep warm clothes handy."))
    if d["humidity"] and d["humidity"] >= 85 and not d["rain"]: adv.append(("💧", "Very humid today. Clothes may take longer to dry."))
    d["advice"] = adv

    return d

def render_png(html_str, path, selector=".card"):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 400, "height": 100}, device_scale_factor=3)
        page.set_content(html_str, wait_until="networkidle")
        try: page.evaluate("document.fonts.ready")
        except Exception: pass
        try: page.locator(selector).screenshot(path=path)
        except: page.screenshot(path=path, full_page=True)
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
            render_png(ui.card_rain_alert(d), "alert.png", ".card")
            send_photo("alert.png", ui.caption_rain(d))
        return

    session.post(f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage", json={"chat_id": os.environ['TELEGRAM_CHAT_ID'], "text": f"☀️ Good Morning Family! Here is your daily briefing for {d['now'].strftime('%A, %B %d')}."})
    
    render_png(ui.card_weather(d), "weather.png")
    send_photo("weather.png", ui.caption_weather(d))
    time.sleep(10)

    render_png(ui.card_advice(d), "advice.png")
    send_photo("advice.png", ui.caption_advice(d))
    time.sleep(10)

    render_png(ui.card_events(d), "events.png")
    send_photo("events.png", ui.caption_events(d))

    for i in d["today"]:
        if i["kind"] == "birthday":
            try:
                render_png(ui.build_birthday_html(i["name"], i["age"]), "birthday.png", ".card")
                send_photo("birthday.png", f"Happy Birthday {i['name']}! 🎉")
            except Exception as e: print("Birthday render failed:", e)

if __name__ == "__main__":
    main()
