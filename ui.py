import html

esc = html.escape
FONT = "https://fonts.googleapis.com/css2?family=Inter:wght@400;550;630;650;700;750;800&display=swap"

CSS = """
:root {
  --ink: #172a3a; --muted: #6c7d8b; --paper: #ffffff; --canvas: #f4f7f6;
  --teal: #167d73; --teal-dark: #105d58; --teal-soft: #e8f5f1;
  --amber: #bd7527; --amber-soft: #fff4de;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: transparent; color: var(--ink); font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; width: 480px; padding: 15px; }

.dash-card { background: var(--paper); border: 1px solid #e7eceb; border-radius: 28px; box-shadow: 0 12px 30px rgba(27,48,60,.06); overflow: hidden; width: 100%; margin-bottom: 15px; }

/* Weather Card */
.weather-card { position: relative; isolation: isolate; padding: 28px 24px; color: #f7fbff; background: linear-gradient(125deg,#193747 0%,#20566a 54%,#2c7880 100%); border: 0; }
.weather-card:before { content: ""; position: absolute; z-index: -1; border-radius: 50%; width: 340px; height: 340px; right: -90px; top: -155px; background: radial-gradient(circle at 35% 40%,#c7e5d955,#b5d7e011 65%,transparent 69%); }
.location-label { color: #d1e3e6; font-size: 14px; font-weight: 750; text-transform: uppercase; letter-spacing: .08em; display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.location-label svg { width: 16px; height: 16px; color: #aee3d3; }
.weather-main { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.temperature { font-size: 88px; line-height: .9; letter-spacing: -.06em; font-weight: 350; }
.temperature sup { font-size: .4em; vertical-align: top; margin-left: 4px; }
.condition { margin-top: 12px; font-size: 22px; font-weight: 700; }
.feels { margin-top: 8px; font-size: 14px; color: #c7dbdf; }

.quick-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
.quick-stat { padding: 14px; border: 1px solid #ffffff20; background: #ffffff12; border-radius: 18px; backdrop-filter: blur(6px); }
.quick-label { display: flex; align-items: center; gap: 6px; color: #c9dfe1; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }
.quick-label svg { width: 14px; height: 14px; color: #abe2d4; }
.quick-value { margin-top: 6px; font-size: 18px; font-weight: 750; }
.quick-note { margin-top: 4px; font-size: 12px; color: #c5d9dc; }

.rain-window { display: flex; align-items: center; justify-content: space-between; padding: 16px; border: 1px solid #d8f0ee35; border-radius: 20px; background: linear-gradient(110deg,#e5fbf014,#d5f5ff12); margin-bottom: 24px; }
.rain-label { display: block; color: #bde8e1; font-size: 10px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.rain-range { display: flex; align-items: center; gap: 10px; margin-top: 6px; }
.rain-range strong { color: #fff; font-size: 18px; }
.rain-range b { color: #8bd3ca; font-size: 18px; }
.chance { padding: 10px 14px; border: 1px solid #ffffff25; border-radius: 16px; text-align: center; background: #ffffff13; }
.chance span { display: block; color: #c7e2e3; font-size: 10px; font-weight: 750; text-transform: uppercase; }
.chance strong { display: block; margin-top: 4px; color: #fff; font-size: 22px; }

.hourly-head { margin-bottom: 12px; }
.hourly-head strong { font-size: 16px; font-weight: 750; display: block; }
.hourly-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }
.hour { padding: 10px 6px; text-align: center; border: 1px solid #ffffff1d; border-radius: 16px; background: #ffffff0c; }
.hour time { display: block; color: #c9dfe0; font-size: 11px; font-weight: 750; }
.hour svg { display: block; width: 38px; height: 36px; margin: 8px auto; }
.hour .cloud { fill: #e6f2f7; stroke: #aac5ce; stroke-width: 1.2; }
.hour .drop { fill: none; stroke: #79c8ef; stroke-width: 2.5; stroke-linecap: round; }
.hour-label { display: block; color: #edf7f6; font-size: 10px; font-weight: 700; line-height: 1.2; }

/* Calendar & Finance */
.calendar-card { padding: 28px 24px; background: linear-gradient(150deg,#fffefa,#fff 75%); }
.card-title { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.title-icon { width: 44px; height: 44px; display: grid; place-items: center; border-radius: 14px; background: var(--amber-soft); color: var(--amber); }
.title-icon svg { width: 22px; height: 22px; }
.card-title h2 { font-size: 20px; font-weight: 800; letter-spacing: -.02em; }

.panchangam-hero { display: flex; align-items: center; justify-content: space-between; padding: 20px; border: 1px solid #f0e5d1; border-radius: 20px; background: linear-gradient(115deg,#fff4df,#fffaf2 72%); margin-bottom: 20px; }
.panchangam-kicker { color: #a26a29; font-size: 11px; font-weight: 820; letter-spacing: .13em; text-transform: uppercase; }
.panchangam-main { margin-top: 8px; font-size: 26px; font-weight: 800; color: #243d4a; }
.panchangam-tamil { margin-top: 6px; color: #897253; font-size: 14px; font-weight: 700; }
.moon-seal { width: 56px; height: 56px; display: grid; place-items: center; border-radius: 18px; background: #fff; color: #bd7b27; font-size: 28px; box-shadow: 0 5px 16px #7a572014; }

.timing-list { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px; }
.timing { padding: 14px; border: 1px solid #edf0ef; border-radius: 16px; background: #f9fbfa; }
.timing.good { background: #edf8f2; border-color: #e0f1e7; }
.timing.avoid { background: #f7f5fc; border-color: #eeebf6; }
.timing-type { display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: .05em; }
.timing.good .timing-type { color: #428369; }
.timing.avoid .timing-type { color: #75699d; }
.timing-time { display: block; margin-top: 8px; color: #293f4c; font-size: 16px; font-weight: 800; }
.timing-caption { margin-top: 4px; color: #89969a; font-size: 12px; font-weight: 600; }

/* Advice & Family */
.list-heading { display: flex; align-items: center; gap: 10px; margin: 24px 0 12px; color: #849197; font-size: 11px; font-weight: 820; letter-spacing: .11em; text-transform: uppercase; }
.list-heading:after { content: ""; flex: 1; border-top: 2px solid #edf0ef; }
.event-list { list-style: none; }
.event { display: grid; grid-template-columns: 42px minmax(0,1fr) auto; align-items: center; gap: 12px; padding: 14px 0; border-bottom: 1px solid #f0f3f2; }
.event:last-child { border-bottom: 0; }
.event-icon { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 12px; background: #f5f8f7; font-size: 20px; }
.event-name { font-size: 15px; font-weight: 750; color: #172a3a; }
.event-badge { padding: 8px 10px; color: #a45c2d; background: #fff2e9; border: 1px solid #f6e5da; border-radius: 10px; font-size: 11px; font-weight: 820; white-space: nowrap; }
.event-badge.upcoming { color: #677c8a; background: #f1f5f8; border-color: #e8edf2; }

.advice { display: grid; grid-template-columns: 40px minmax(0,1fr); gap: 14px; align-items: start; padding: 16px; border: 1px solid #edf0ef; border-radius: 18px; background: #fafbfa; margin-bottom: 12px; }
.advice-icon { width: 40px; height: 40px; display: grid; place-items: center; border-radius: 12px; background: #fff; font-size: 22px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }
.advice-title { color: #829096; font-size: 11px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
.advice-copy { margin-top: 6px; color: #344b57; font-size: 15px; font-weight: 700; line-height: 1.4; }

svg { fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
"""

def template(content):
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}">
    <style>{CSS}</style></head><body>{content}</body></html>"""

def get_hourly_html(h, pop):
    def short_h(hr): return f"{hr%12 or 12}{'A' if hr<12 else 'P'}"
    if pop >= 20:
        icon = '<svg viewBox="0 0 48 45"><path class="cloud" d="M34 27H14a8 8 0 1 1 0-16c1.4 0 2.7.4 3.9 1.1A11 11 0 0 1 39 14a6 6 0 0 1-5 13Z"/><path class="drop" d="m16 32-2 5m9-5-2 5m12-5-2 5"/></svg>'
        label = "Likely" if pop >= 50 else "Possible"
    else:
        icon = '<svg viewBox="0 0 48 45"><path class="cloud" d="M34 27H14a8 8 0 1 1 0-16c1.4 0 2.7.4 3.9 1.1A11 11 0 0 1 39 14a6 6 0 0 1-5 13Z"/></svg>'
        label = "Cloudy"
        
    return f'<div class="hour"><time>{short_h(h)}</time>{icon}<span class="hour-label">{label}</span></div>'

def card_weather(d):
    if d.get("rain") and d["rain"]["chance"] >= 20: big_icon = "🌧️"
    elif d["main"] == "Clear": big_icon = "🌙" if d.get("night") else "☀️"
    else: big_icon = "☁️"

    aqi_name = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very poor"}.get(d["aqi"], "Unknown")
    uv_v = f"{d['uv']:.0f}" if d.get("uv") else "0"

    rain_window = ""
    if d.get("rain"):
        start = "Now" if d['rain']['now'] else f"{d['rain']['start']%12 or 12}:00 {'AM' if d['rain']['start']<12 else 'PM'}"
        end = f"{d['rain']['end']%12 or 12}:00 {'AM' if d['rain']['end']<12 else 'PM'}"
        rain_window = f"""
        <div class="rain-window">
          <div><span class="rain-label">Rain Risk Window</span>
          <div class="rain-range"><strong>{start}</strong><b>→</b><strong>{end}</strong></div></div>
          <div class="chance"><span>Chance</span><strong>{d['rain']['chance']}%</strong></div>
        </div>"""

    hours_html = ""
    if d.get("hourly"):
        count = 0
        for h in range(6, 24, 3): 
            if h in d["hourly"] and count < 6:
                hours_html += get_hourly_html(h, d["hourly"][h]["pop"])
                count += 1

    return template(f"""
      <article class="dash-card weather-card">
        <div class="location-label"><svg viewBox="0 0 24 24"><path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"></path><circle cx="12" cy="10" r="2.5"></circle></svg>{d['city']} WEATHER</div>
        <div class="weather-main">
          <div><div class="temperature">{d['temp']:.0f}<sup>°</sup></div><div class="condition">{d['cond']}</div><div class="feels">Feels {d['feels']:.0f}° &middot; H:{d['t_max']:.0f}° L:{d['t_min']:.0f}°</div></div>
          <div style="font-size:140px;line-height:1;filter:drop-shadow(0 15px 20px rgba(7,28,40,0.3))">{big_icon}</div>
        </div>
        
        <div class="quick-stats">
          <div class="quick-stat"><div class="quick-label"><svg viewBox="0 0 24 24"><path d="M3 8h12a3 3 0 1 0-3-3M2 12h17a3 3 0 1 1-3 3M4 16h7a3 3 0 1 1-3 3"></path></svg>Wind</div><div class="quick-value">{d['wind']:.0f} km/h</div></div>
          <div class="quick-stat"><div class="quick-label"><svg viewBox="0 0 24 24"><path d="M12 3c3 4 6 7 6 11a6 6 0 0 1-12 0c0-4 3-7 6-11Z"></path><path d="M9 15a3 3 0 0 0 3 3"></path></svg>Air quality</div><div class="quick-value">{aqi_name}</div></div>
        </div>
        
        {rain_window}
        
        <div class="hourly-head"><strong>Hourly Outlook</strong></div>
        <div class="hourly-grid">{hours_html}</div>
      </article>
    """)

def card_advice(d):
    p = d.get("panchangam", {})
    
    # Process Advice List
    adv_html = ""
    titles = {"☀️": "Sun Protection", "🌡️": "Heat Advisory", "☔": "Rain Alert", "🧺": "Outdoor Plans"}
    for icon, text in d["advice"]:
        title = titles.get(icon, "Notice")
        adv_html += f'<div class="advice"><div class="advice-icon">{icon}</div><div><div class="advice-title">{title}</div><div class="advice-copy">{esc(text)}</div></div></div>'

    gold_html = ""
    if d.get("metals"):
        gold_html = f"""
        <div class="list-heading" style="margin-top:30px">Today's Market Rates</div>
        <div class="timing-list">
          <div class="timing good"><div class="timing-type">22K Gold (1g)</div><span class="timing-time">₹{d['metals']['gold22']}</span></div>
          <div class="timing"><div class="timing-type">Silver (1g)</div><span class="timing-time">₹{d['metals']['silver']}</span></div>
        </div>"""

    return template(f"""
      <article class="dash-card calendar-card">
        <div class="card-title"><div class="title-icon"><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"></rect><path d="M16 3v4M8 3v4M3 10h18"></path><path d="M8 14h.01M12 14h.01M16 14h.01"></path></svg></div><h2>Daily Guide & Panchangam</h2></div>
        
        <div class="panchangam-hero">
          <div><div class="panchangam-kicker">Tamil Calendar</div><div class="panchangam-main">{p.get('tamil_date')}</div><div class="panchangam-tamil">🌙 {p.get('nakshatra')}</div></div>
          <div class="moon-seal">{"🌕" if "Pournami" in p.get("special", []) else "☾"}</div>
        </div>

        <div class="list-heading">Daily Timings</div>
        <div class="timing-list">
          <div class="timing good"><div class="timing-type">Nalla Neram</div><span class="timing-time">{p.get('nalla')}</span><div class="timing-caption">நல்ல நேரம்</div></div>
          <div class="timing avoid"><div class="timing-type">Rahu Kalam</div><span class="timing-time">{p.get('rahu')}</span><div class="timing-caption">ராகு காலம்</div></div>
          <div class="timing avoid"><div class="timing-type">Yamagandam</div><span class="timing-time">{p.get('yama')}</span><div class="timing-caption">எமகண்டம்</div></div>
          <div class="timing avoid"><div class="timing-type">Gulikai</div><span class="timing-time">{p.get('kuli')}</span><div class="timing-caption">குளிகை</div></div>
        </div>
        
        {gold_html}

        <div class="list-heading" style="margin-top:30px">Daily Advice</div>
        <div>{adv_html}</div>
      </article>
    """)

def card_events(d):
    tdy = "".join(f'<li class="event"><span class="event-icon">{i["icon"]}</span><div class="event-name">{esc(i["text"])}</div><span class="event-badge">TODAY</span></li>' for i in d["today"])
    if not tdy: tdy = '<div style="font-size:14px;color:var(--muted);padding:10px 0;font-weight:600">No events scheduled for today.</div>'
    
    up = ""
    for i in d["upcoming"]:
        cd_text = "Tomorrow" if i['days_left'] == 1 else f"In {i['days_left']} Days"
        up += f'<li class="event"><span class="event-icon">{i["icon"]}</span><div class="event-name">{esc(i["text"])}</div><span class="event-badge upcoming">{cd_text}</span></li>'
    if not up: up = '<div style="font-size:14px;color:var(--muted);padding:10px 0;font-weight:600">No upcoming events found.</div>'

    return template(f"""
      <article class="dash-card calendar-card">
        <div class="card-title"><div class="title-icon" style="background:#eaf5f0;color:var(--teal)"><svg viewBox="0 0 24 24"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"></path></svg></div><h2>Family Calendar</h2></div>
        
        <div class="list-heading">Happening Today</div>
        <ul class="event-list">{tdy}</ul>
        
        <div class="list-heading" style="margin-top:24px">Coming Up Soon</div>
        <ul class="event-list">{up}</ul>
      </article>
    """)

def card_rain_alert(d):
    def fmt(dt): return dt.strftime("%I:%M %p").lstrip("0")
    def fmt_h(h): return f"{h % 12 or 12}:00 {'AM' if h < 12 else 'PM'}"
    start = "Now" if d['rain']['now'] else fmt_h(d['rain']['start'])
    chance = d['rain']['chance']
    end_time = fmt_h(d['rain']['end'])
    
    en_msg = f"Rain expected to continue until {end_time}." if d['rain']['now'] else f"Rain expected to start around {start}."
    ta_msg = f"{end_time} வரை மழை தொடர வாய்ப்புள்ளது." if d['rain']['now'] else f"{start} அளவில் மழை தொடங்கலாம்."

    return template(f"""
    <div class="dash-card" style="background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);padding:40px 30px;color:#fff;text-align:center;border:none">
        <div style="font-size:120px;margin-bottom:20px;filter:drop-shadow(0 15px 25px rgba(0,0,0,0.5))">⛈️</div>
        <div style="font-size:36px;font-weight:800;color:#fca5a5;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px">Sudden Rain Alert</div>
        <div style="font-size:20px;color:#cbd5e1;font-weight:600;margin-bottom:30px">திடீர் மழை எச்சரிக்கை</div>
        
        <div style="display:flex;gap:15px;margin-bottom:30px">
            <div style="flex:1;background:rgba(255,255,255,0.05);padding:20px;border-radius:20px;border:1px solid rgba(255,255,255,0.1)">
                <div style="font-size:14px;color:#94a3b8;font-weight:700;text-transform:uppercase;margin-bottom:10px">Start Time</div>
                <div style="font-size:28px;color:#38bdf8;font-weight:800">{start}</div>
            </div>
            <div style="flex:1;background:rgba(255,255,255,0.05);padding:20px;border-radius:20px;border:1px solid rgba(255,255,255,0.1)">
                <div style="font-size:14px;color:#94a3b8;font-weight:700;text-transform:uppercase;margin-bottom:10px">Probability</div>
                <div style="font-size:28px;color:#38bdf8;font-weight:800">{chance}%</div>
            </div>
        </div>
        
        <div style="background:linear-gradient(90deg, rgba(56,189,248,0.15) 0%, rgba(56,189,248,0) 100%);border-left:4px solid #38bdf8;padding:24px;border-radius:12px;text-align:left">
            <div style="font-size:20px;font-weight:700;color:#f8fafc;margin-bottom:12px">{en_msg}</div>
            <div style="font-size:18px;color:#cbd5e1;font-weight:600">{ta_msg}</div>
        </div>
    </div>
    """)

def build_birthday_html(name, age):
    age_line = f"Turns {age} today!" if age else "Wishing you a wonderful year ahead!"
    return template(f"""
    <div class="dash-card" style="background:linear-gradient(135deg,#7561af 0%,#a585cf 100%);padding:80px 30px;text-align:center;position:relative;overflow:hidden;border:none">
        <div style="position:absolute;top:-50px;left:-50px;width:250px;height:250px;background:radial-gradient(circle,rgba(255,255,255,0.2) 0%,transparent 70%);border-radius:50%;z-index:1"></div>
        <div style="position:absolute;bottom:-80px;right:-50px;width:300px;height:300px;background:radial-gradient(circle,rgba(255,255,255,0.15) 0%,transparent 70%);border-radius:50%;z-index:1"></div>
        
        <div style="font-size:130px;margin-bottom:20px;filter:drop-shadow(0 10px 20px rgba(0,0,0,0.2));position:relative;z-index:2">🎂</div>
        <div style="font-size:24px;font-weight:800;color:#e8dff5;letter-spacing:4px;text-transform:uppercase;margin-bottom:16px;position:relative;z-index:2">Happy Birthday</div>
        <div style="font-size:52px;font-weight:800;color:#ffffff;line-height:1.1;margin-bottom:30px;position:relative;z-index:2;letter-spacing:-1px">{esc(name)}</div>
        <div style="background:rgba(255,255,255,0.2);color:#ffffff;font-size:18px;font-weight:750;padding:14px 30px;border-radius:50px;display:inline-block;position:relative;z-index:2;backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.3)">{esc(age_line)}</div>
    </div>
    """)
