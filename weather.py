"""Daily family briefing: weather dashboard + panchangam + rates + family calendar.

Run daily:     python weather.py
Run weekly:    python weather.py --weekly     (also added automatically on Sundays)
Run as watch:  python weather.py --watch      (rain / wind / air-quality alerts, no repeats)
"""
import os, sys, time, json, math, requests, csv
from datetime import datetime, timezone, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import ui

# Setup resilient API connection
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

STATE_FILE = "alert_state.json"


# ------------------------------------------------------------------ data sources
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
            "latitude": lat, "longitude": lon, "timezone": "auto", "forecast_days": 8,
            "hourly": "precipitation_probability,precipitation,temperature_2m,uv_index,cloud_cover",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        }, timeout=20)
        r.raise_for_status()
        return r.json()
    except: return None

def open_aqi(lat, lon):
    """Real AQI number (US scale) from Open-Meteo's free air-quality API. Returns (aqi, pm2.5) or (None, None)."""
    try:
        r = session.get("https://air-quality-api.open-meteo.com/v1/air-quality", params={
            "latitude": lat, "longitude": lon, "current": "us_aqi,pm2_5"}, timeout=15)
        r.raise_for_status()
        c = r.json()["current"]
        return c.get("us_aqi"), c.get("pm2_5")
    except: return None, None

def aqi_level(v):
    """Map a US AQI number to the 1-5 scale the cards use."""
    return 1 if v <= 50 else 2 if v <= 100 else 3 if v <= 150 else 4 if v <= 200 else 5

def extra_places(key):
    """Weather for other places the family lives (EXTRA_ZIPS = '641001,IN;110001,IN')."""
    out = []
    for z in [x.strip() for x in (os.environ.get("EXTRA_ZIPS") or "").split(";") if x.strip()]:
        try:
            g = session.get("https://api.openweathermap.org/geo/1.0/zip", params={"zip": z, "appid": key}, timeout=15).json()
            cur = session.get("https://api.openweathermap.org/data/2.5/weather", params={
                "lat": g["lat"], "lon": g["lon"], "units": "metric", "appid": key}, timeout=15).json()
            om = openmeteo(g["lat"], g["lon"])
            pop = (om["daily"]["precipitation_probability_max"][0] or 0) if om else 0
            code = om["daily"]["weather_code"][0] if om else None
            out.append({"city": g.get("name") or cur["name"], "temp": cur["main"]["temp"], "pop": pop, "code": code})
        except Exception as e:
            print("Extra place failed:", z, e)
    return out


# ------------------------------------------------------------------ panchangam
TITHIS = ["Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami", "Navami", "Dashami",
          "Ekadasi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
          "Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami", "Navami", "Dashami",
          "Ekadasi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"]
NAKSHATRAS = ["Aswini", "Bharani", "Karthigai", "Rohini", "Mrigasira", "Arudra", "Punarvasu", "Pushya", "Ashlesha",
              "Magam", "Pooram", "Uthiram", "Hastham", "Chithirai", "Swathi", "Visakam", "Anusham", "Kettai",
              "Moolam", "Pooradam", "Uthiradam", "Thiruvonam", "Avittam", "Sadayam", "Poorattadhi", "Uthirattadhi", "Revathi"]
TAMIL_MONTHS = ['Chithirai', 'Vaikasi', 'Aani', 'Aadi', 'Avani', 'Purattasi', 'Aippasi', 'Karthigai', 'Margazhi', 'Thai', 'Masi', 'Panguni']
AYANAMSA = 24.15  # Lahiri, approx. for 2025-2026

def get_panchangam(dt, sunrise, sunset, lat, lon):
    """Tithi/nakshatra are read at sunrise (Pradosham at sunset). Tamil date counts days from the
    last sankranti, using the sun's sign at sunset. Uses your real latitude/longitude."""
    try:
        import ephem
    except ImportError:
        return {}

    obs = ephem.Observer()
    obs.lat, obs.lon, obs.elevation = str(lat), str(lon), 0

    def sun_moon(t):
        obs.date = t.astimezone(timezone.utc)
        return math.degrees(ephem.Ecliptic(ephem.Sun(obs)).lon), math.degrees(ephem.Ecliptic(ephem.Moon(obs)).lon)

    def tithi_idx(t):
        s, m = sun_moon(t)
        return int(((m - s) % 360) / 12.0)

    def nakshatra(t):
        _, m = sun_moon(t)
        return NAKSHATRAS[int(((m - AYANAMSA) % 360) / (360 / 27.0))]

    def sign_at_sunset(offset_days):
        s, _ = sun_moon(sunset + timedelta(days=offset_days))
        return int(((s - AYANAMSA) % 360) / 30)

    t_rise = tithi_idx(sunrise)
    t_set = tithi_idx(sunset + timedelta(minutes=45))
    name, name_set = TITHIS[t_rise], TITHIS[t_set]

    special = []
    if name == "Amavasya": special.append("🌑 Amavasya (அமாவாசை)")
    if name == "Purnima": special.append("🌕 Pournami (பௌர்ணமி)")
    if name == "Ekadasi": special.append("🙏 Ekadasi (ஏகாதசி)")
    if name_set == "Trayodashi": special.append(f"🛕 {'Sani ' if dt.weekday() == 5 else ''}Pradosham (பிரதோஷம்)")
    if name == "Chaturthi": special.append("🐘 Chaturthi (சதுர்த்தி)")
    if name == "Shashti": special.append("🦚 Shashti (சஷ்டி)")

    naks = []
    for n in (nakshatra(sunrise), nakshatra(sunset)):
        if n not in naks: naks.append(n)

    cur = sign_at_sunset(0)
    day_no = 1
    while day_no < 32 and sign_at_sunset(-day_no) == cur: day_no += 1

    day_idx = dt.weekday()
    part_dur = (sunset - sunrise) / 8
    def get_time(p): return f"{(sunrise + (part_dur * p)).strftime('%I:%M %p').lstrip('0')} - {(sunrise + (part_dur * (p+1))).strftime('%I:%M %p').lstrip('0')}"

    return {
        "special": special,
        "tithi": name, "paksha_en": "Shukla" if t_rise < 15 else "Krishna", "paksha_ta": "வளர்பிறை" if t_rise < 15 else "தேய்பிறை",
        "nakshatra": " / ".join(naks),
        "tamil_date": f"{TAMIL_MONTHS[cur]} {day_no}",
        "rahu": get_time([1, 6, 4, 5, 3, 2, 7][day_idx]), "yama": get_time([3, 2, 1, 0, 6, 5, 4][day_idx]), "kuli": get_time([5, 4, 3, 2, 1, 0, 6][day_idx]),
        "nalla": ["6:30-7:30 AM", "7:30-8:30 AM", "9:00-10:00 AM", "10:30-11:30 AM", "9:30-10:30 AM", "7:30-8:30 AM", "7:30-8:30 AM"][day_idx]
    }


# ------------------------------------------------------------------ family calendar (Google Sheet)
def load_events():
    """Sheet columns: name, date, type, repeat, year, day, wish, photo  (wish/photo only matter for birthdays)."""
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
                    "day": row.get("day", "").strip(),
                    "wish": (row.get("wish") or "").strip(),
                    "photo": (row.get("photo") or "").strip(),
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
        out.append({"icon": ICONS.get(kind, "📌"), "text": text, "kind": kind, "name": e["name"], "age": age,
                    "wish": e.get("wish"), "photo": e.get("photo")})
    if day in hol:
        out.append({"icon": "🎉" if any(k in hol[day].lower() for k in ("diwali","deepavali","pongal","holi","new year")) else ICONS.get("holiday", "🏖️"), "text": hol[day], "kind": "holiday"})
    return out


# ------------------------------------------------------------------ advice
def build_advice(d):
    """Each tip is (icon, English, Tamil)."""
    now, hourly, adv = d["now"], d["hourly"], []
    limit = float(os.environ.get("WIND_LIMIT") or 60)
    watch = {w.strip().lower() for w in (os.environ.get("WATCH") or "").split(",") if w.strip()}

    if d["rain"]:
        t = ui.fmt_h(d["rain"]["start"])
        if d["rain"]["now"]:
            adv.append(("☔", "Rain expected right now. Take an umbrella.", "இப்போது மழை வாய்ப்பு. குடை எடுத்துச் செல்லுங்கள்."))
        else:
            adv.append(("☔", f"Rain expected around {t}. Take an umbrella.", f"{t} அளவில் மழை வரலாம். குடை எடுத்துச் செல்லுங்கள்."))
        adv.append(("🧺", "Not a good day to dry clothes outside.", "இன்று துணிகளை வெளியே காயவைக்க வேண்டாம்."))
    else:
        adv.append(("🧺", "Dry day ahead. Good for drying clothes outside.", "இன்று மழை இல்லை. துணிகளை வெளியே காயவைக்கலாம்."))

    # school drop-off / pick-up
    for env, en_l, ta_l in (("SCHOOL_DROP", "School drop-off", "பள்ளிக்குச் செல்லும் நேரம்"),
                            ("SCHOOL_PICKUP", "School pick-up", "பள்ளி முடியும் நேரம்")):
        v = os.environ.get(env)
        if not v: continue
        try: hh, mm = [int(x) for x in v.split(":")]
        except ValueError: continue
        if (hh, mm) < (now.hour, now.minute): continue
        x = hourly.get(hh)
        if x and x["pop"] >= 30:
            t = f"{hh % 12 or 12}:{mm:02d} {'AM' if hh < 12 else 'PM'}"
            adv.append(("🎒", f"{en_l} ({t}): {x['pop']}% chance of rain. Send a raincoat or umbrella.",
                        f"{ta_l} ({t}): மழை வாய்ப்பு {x['pop']}%. ரெயின்கோட் அல்லது குடை கொடுத்து அனுப்புங்கள்."))

    if d["aqi"] >= 4:
        adv.append(("😷", "Air quality is poor. Elders and children should stay indoors or wear a mask.",
                    "காற்றுத் தரம் மோசம். முதியவர்களும் குழந்தைகளும் வீட்டிற்குள் இருங்கள், முகக்கவசம் அணியுங்கள்."))
    if 40 <= d["wind"] < limit:
        adv.append(("💨", f"Strong winds up to {d['wind']:.0f} km/h. Secure loose items and be careful on two-wheelers.",
                    f"பலத்த காற்று ({d['wind']:.0f} கி.மீ/மணி). தளர்வான பொருட்களைப் பாதுகாக்கவும், இருசக்கர வாகனத்தில் கவனம்."))
    if d["uv"] and d["uv"] >= 6:
        adv.append(("☀️", f"High UV ({d['uv']:.0f}). Please use sun protection or an umbrella.",
                    f"அதிக புற ஊதா ({d['uv']:.0f}). குடை அல்லது சன்ஸ்கிரீன் பயன்படுத்துங்கள்."))
    if d["feels"] >= 35:
        adv.append(("🌡️", "It's feeling quite hot today. Stay hydrated.", "இன்று வெப்பம் அதிகம். நிறைய தண்ணீர் குடியுங்கள்."))
    if d["feels"] <= 20:
        adv.append(("🧥", "It feels cool today. Keep warm clothes handy.", "இன்று குளிர்ச்சியாக உள்ளது. சூடான ஆடைகளை எடுத்துக்கொள்ளுங்கள்."))
    if d["humidity"] and d["humidity"] >= 85 and not d["rain"]:
        adv.append(("💧", "Very humid today. Clothes may take longer to dry.", "ஈரப்பதம் அதிகம். துணிகள் காய அதிக நேரம் ஆகும்."))

    # personal tips (WATCH = elders,asthma,kids)
    if "elders" in watch:
        if d["feels"] >= 35:
            adv.append(("👵", "Elders: avoid going out between 11 AM and 3 PM.", "முதியவர்கள் காலை 11 முதல் மதியம் 3 வரை வெளியே செல்வதைத் தவிர்க்கவும்."))
        elif d["rain"]:
            adv.append(("👵", "Floors get slippery in the rain. Elders, please walk carefully.", "மழையில் தரை வழுக்கும். முதியவர்கள் கவனமாக நடக்கவும்."))
        elif d["aqi"] >= 3:
            adv.append(("👵", "Air quality is not good for elders today. Better to stay indoors.", "இன்று காற்றுத் தரம் முதியவர்களுக்கு நல்லதல்ல. வீட்டிற்குள் இருப்பது நல்லது."))
    if "asthma" in watch and (d["aqi"] >= 3 or (d["humidity"] or 0) >= 85):
        adv.append(("🫁", "Asthma care: keep the inhaler handy and skip outdoor exercise today.", "ஆஸ்துமா உள்ளவர்கள் இன்ஹேலரை அருகில் வைத்துக்கொள்ளவும்; வெளியே உடற்பயிற்சி வேண்டாம்."))
    if "kids" in watch:
        if d["rain"]:
            adv.append(("🧒", "Kids: no outdoor play today because of the rain.", "மழையால் குழந்தைகள் இன்று வெளியே விளையாட வேண்டாம்."))
        elif d["uv"] and d["uv"] >= 6:
            adv.append(("🧒", "Kids: play outside only before 10 AM or after 4 PM.", "குழந்தைகள் காலை 10 மணிக்கு முன் அல்லது மாலை 4 மணிக்குப் பின் மட்டும் வெளியே விளையாடட்டும்."))
    return adv[:7]


# ------------------------------------------------------------------ collect everything
def collect(light=False):
    """light=True is used by the storm watch: weather only (no rates, calendar or panchangam)."""
    key = os.environ["OWM_API_KEY"]
    zip_code = os.environ.get("ZIP_CODE") or "600001,IN"
    geo = session.get(f"https://api.openweathermap.org/geo/1.0/zip?zip={zip_code}&appid={key}").json()
    lat, lon = geo["lat"], geo["lon"]
    cur = session.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={key}").json()
    fc = session.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={key}").json()
    aq = session.get(f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={key}").json()["list"][0]
    om = openmeteo(lat, lon)
    aqi_val, pm25 = open_aqi(lat, lon)

    tz = timezone(timedelta(seconds=fc["city"]["timezone"]))
    now = datetime.now(tz)
    today = now.date()
    def at(ts): return datetime.fromtimestamp(ts, tz)

    sunrise, sunset = at(cur["sys"]["sunrise"]), at(cur["sys"]["sunset"])
    night = now < sunrise or now > sunset
    slots = [s for s in fc["list"] if at(s["dt"]).date() == today and at(s["dt"]) + timedelta(hours=3) > now]

    d = {"city": cur["name"], "now": now, "temp": cur["main"]["temp"], "feels": cur["main"]["feels_like"], "cond": cur["weather"][0]["description"].title(),
         "main": cur["weather"][0]["main"], "night": night, "sunrise": sunrise, "sunset": sunset,
         "aqi": aqi_level(aqi_val) if aqi_val is not None else aq["main"]["aqi"], "aqi_val": aqi_val,
         "pm25": pm25 if pm25 is not None else aq["components"]["pm2_5"],
         "humidity": cur["main"].get("humidity"),
         "panchangam": {}, "metals": None, "places": []}
    if not light:
        d["panchangam"] = get_panchangam(now, sunrise, sunset, lat, lon)
        d["metals"] = get_metals()
        d["places"] = extra_places(key)

    d["t_min"] = min([s["main"]["temp_min"] for s in slots] + [d["temp"]])
    d["t_max"] = max([s["main"]["temp_max"] for s in slots] + [d["temp"]])

    hourly = {}
    if om:
        h = om["hourly"]
        for i, ts in enumerate(h["time"]):
            dt = datetime.fromisoformat(ts)
            if dt.date() == today:
                hourly[dt.hour] = {"pop": h["precipitation_probability"][i] or 0, "uv": h["uv_index"][i], "temp": h["temperature_2m"][i],
                                   "cloud": h["cloud_cover"][i], "mm": h["precipitation"][i] or 0}
    d["hourly"] = hourly

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
        hrs = range(wet[0], end + 1)
        peak = max(hourly[x]["mm"] for x in hrs)
        d["rain"] = {"start": wet[0], "end": end + 1, "chance": max([hourly[x]["pop"] for x in hrs]), "now": wet[0] <= now.hour,
                     "mm": sum(hourly[x]["mm"] for x in hrs), "level": "heavy" if peak >= 7.6 else "moderate" if peak >= 2.5 else "light"}

    d["wind"] = max([cur["wind"]["speed"], cur["wind"].get("gust", 0)] + [s["wind"]["speed"] for s in slots]) * 3.6
    uvs = [(v["uv"], hr) for hr, v in hourly.items() if v["uv"] is not None]
    d["uv"] = max(uvs)[0] if uvs else 0

    # alerts are (level, English, Tamil)
    d["alerts"] = []
    if d["wind"] >= float(os.environ.get("WIND_LIMIT") or 60):
        d["alerts"].append(("red", "High wind alert. Do not go outside.", "பலத்த காற்று எச்சரிக்கை. வெளியே செல்ல வேண்டாம்."))
    if d["aqi"] == 5:
        d["alerts"].append(("red", "Very poor air quality. Avoid outdoor activity.", "மிக மோசமான காற்றுத் தரம். வெளியே செல்வதைத் தவிர்க்கவும்."))

    d["today"], d["upcoming"], d["week_events"] = [], [], []
    if not light:
        events = load_events()
        hol = holiday_table(today.year, os.environ.get("HOLIDAY_STATE"))
        d["today"] = items_for(today, events, hol)
        everything = []
        for i in range(1, 31):
            day = today + timedelta(days=i)
            for it in items_for(day, events, hol, upcoming=True):
                it["days_left"] = i
                everything.append(it)
        d["upcoming"] = everything[:8]
        d["week_events"] = [x for x in everything if x["days_left"] <= 7]

    d["advice"] = build_advice(d)
    return d


# ------------------------------------------------------------------ Telegram helpers
def tg(method, **kw):
    return session.post(f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/{method}", timeout=90, **kw)

def render_png(html_str, path, selector=".card"):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 480, "height": 100}, device_scale_factor=3)
        page.set_content(html_str, wait_until="networkidle")
        try: page.evaluate("document.fonts.ready")
        except Exception: pass
        try: page.locator(selector).screenshot(path=path)
        except: page.screenshot(path=path, full_page=True)
        b.close()
    return path

def send_photo(path, cap=""):
    with open(path, "rb") as f:
        tg("sendPhoto", data={"chat_id": os.environ['TELEGRAM_CHAT_ID'], "caption": cap}, files={"photo": f}).raise_for_status()

def send_album(paths, cap):
    """All cards in ONE message (the caption sits under the first card)."""
    if len(paths) == 1: return send_photo(paths[0], cap)
    files, media = {}, []
    try:
        for i, p in enumerate(paths):
            files[f"p{i}"] = open(p, "rb")
            m = {"type": "photo", "media": f"attach://p{i}"}
            if i == 0: m["caption"] = cap
            media.append(m)
        tg("sendMediaGroup", data={"chat_id": os.environ['TELEGRAM_CHAT_ID'], "media": json.dumps(media)}, files=files).raise_for_status()
    finally:
        for f in files.values(): f.close()


# ------------------------------------------------------------------ alert memory (no repeat alerts)
def load_state():
    try:
        with open(STATE_FILE) as f: return json.load(f)
    except Exception: return {}

def save_state(state):
    with open(STATE_FILE, "w") as f: json.dump(state, f)

def should_send(state, kind, key, cooldown_hours, now):
    """False if this exact alert was already sent, or any alert of this kind went out inside the cooldown."""
    last = state.get(kind)
    if not last: return True
    if last.get("key") == key: return False
    return (now.timestamp() - last.get("ts", 0)) >= cooldown_hours * 3600

def mark_sent(state, kind, key, now):
    state[kind] = {"key": key, "ts": now.timestamp()}


# ------------------------------------------------------------------ main
def main():
    watch = "--watch" in sys.argv
    d = collect(light=watch)
    now = d["now"]
    chat = os.environ['TELEGRAM_CHAT_ID']

    if watch:
        state = load_state()
        today_key = now.date().isoformat()
        try:
            red = [a for a in d["alerts"] if a[0] == "red"]
            wind_alert = next((a for a in red if "wind" in a[1].lower()), None)
            aqi_alert = next((a for a in red if "air" in a[1].lower()), None)
            for kind, alert, cooldown in (("wind", wind_alert, 4), ("aqi", aqi_alert, 24)):
                if alert and should_send(state, kind, today_key, cooldown, now):
                    tg("sendMessage", json={"chat_id": chat, "text": f"⚠️ {alert[1]}\n{alert[2]}"}).raise_for_status()
                    mark_sent(state, kind, today_key, now)

            r = d["rain"]
            soon = r and ((r["start"] - now.hour) % 24) <= 2
            if soon and r["chance"] >= 50 and (r["mm"] >= 0.1):
                key = f"{today_key}-{r['start']}"
                if should_send(state, "rain", key, 3, now):
                    render_png(ui.card_rain_alert(d), "alert.png", ".card")
                    send_photo("alert.png", ui.caption_rain(d))
                    mark_sent(state, "rain", key, now)
        finally:
            save_state(state)
        return

    # ---- daily briefing: ONE album message
    cards = [("weather.png", ui.card_weather), ("advice.png", ui.card_advice), ("events.png", ui.card_events)]
    if now.weekday() == 6 or "--weekly" in sys.argv:
        cards.append(("week.png", ui.card_week))
    paths = []
    for fn, build in cards:
        try:
            html_str = build(d)
            if html_str:
                render_png(html_str, fn)
                paths.append(fn)
        except Exception as e:
            print("Card failed:", fn, e)
    if not paths:
        tg("sendMessage", json={"chat_id": chat, "text": ui.caption_daily(d)}).raise_for_status()
    else:
        cap = ui.caption_daily(d)
        try:
            send_album(paths, cap)
        except Exception as e:
            print("Album failed, sending one by one:", e)
            for i, p in enumerate(paths):
                send_photo(p, cap if i == 0 else "")
                time.sleep(3)

    for i in d["today"]:
        if i["kind"] == "birthday":
            try:
                render_png(ui.build_birthday_html(i["name"], i["age"], i.get("wish"), i.get("photo")), "birthday.png", ".card")
                send_photo("birthday.png", f"{ui.L('Happy Birthday', 'பிறந்தநாள் வாழ்த்துக்கள்')} {i['name']}! 🎉")
            except Exception as e: print("Birthday render failed:", e)

if __name__ == "__main__":
    main()
