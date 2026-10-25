import html

esc = html.escape
FONT = "https://fonts.googleapis.com/css2?family=Inter:wght@400;550;630;650;700;750;770;800&display=swap"
CSS = """
:root {
  --ink: #172a3a; --muted: #6c7d8b; --line: #e7eceb; --paper: #ffffff; --canvas: #f4f7f6;
  --teal: #167d73; --teal-dark: #105d58; --teal-soft: #e8f5f1;
  --amber: #bd7527; --amber-soft: #fff4de; --violet: #7561af;
  --shadow: 0 18px 50px rgba(31, 54, 67, .07), 0 2px 8px rgba(31, 54, 67, .035);
}
* { box-sizing: border-box; }
/* Forced Mobile Width & Enlarged Fonts */
body { margin: 0; background: var(--canvas); color: var(--ink); font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; width: 540px; padding: 15px; }

.card-wrapper { display: flex; flex-direction: column; gap: 16px; width: 100%; }
.dash-card { background: var(--paper); border: 1px solid #e9eeed; border-radius: 28px; box-shadow: var(--shadow); overflow: hidden; }

/* Weather Card */
.weather-card { position: relative; isolation: isolate; min-height: 0; padding: 32px 28px; color: #f7fbff; background: linear-gradient(123deg, #19394b 0%, #24596a 52%, #307b83 100%); border: 0; }
.weather-card:before, .weather-card:after { content: ""; position: absolute; z-index: -1; border-radius: 50%; pointer-events: none; }
.weather-card:before { width: 320px; height: 320px; right: -105px; top: -120px; background: radial-gradient(circle at 35% 40%, #c7e5d955, #b5d7e011 65%, transparent 69%); }
.weather-card:after { width: 240px; height: 240px; right: 105px; bottom: -195px; border: 1px solid #ffffff17; box-shadow: 0 0 0 28px #ffffff08, 0 0 0 58px #ffffff06; }
.location-label { color: #d1e3e6; font-size: 16px; display: flex; align-items: center; gap: 7px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 20px; }
.location-label svg { width: 18px; height: 18px; color: #b7e8d8; }
.weather-main { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.temperature { font-size: 110px; line-height: .9; letter-spacing: -.06em; font-weight: 400; }
.temperature sup { font-size: .4em; vertical-align: top; margin-left: 4px; }
.condition { margin-top: 15px; font-size: 26px; font-weight: 700; }
.feels { margin-top: 10px; font-size: 16px; color: #d1e0e3; }
.weather-stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 24px; }
.weather-stat { padding: 16px; border: 1px solid #ffffff21; background: #ffffff12; border-radius: 20px; backdrop-filter: blur(6px); }
.stat-label { display: flex; align-items: center; gap: 8px; color: #d1e3e6; font-size: 14px; font-weight: 650; }
.stat-label svg { width: 18px; height: 18px; color: #b9ecdc; }
.stat-value { margin-top: 8px; font-size: 22px; font-weight: 770; }
.stat-note { margin-top: 4px; font-size: 13px; color: #ccdcdf; }

/* Rain Window */
.rain-window { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: 24px; padding: 18px; border: 1px solid #d8f0ee38; border-radius: 20px; background: linear-gradient(110deg, #e5fbf015, #d5f5ff13); }
.rain-window-label { display: block; color: #bde8e1; font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.rain-window-times { display: flex; align-items: center; margin-top: 8px; }
.window-time { color: #fff; font-size: 22px; font-weight: 770; }
.window-caption { margin-top: 6px; color: #c2d9dc; font-size: 13px; line-height: 1.4; }
.chance-badge { padding: 12px 16px; border: 1px solid #ffffff26; border-radius: 16px; text-align: center; background: #ffffff14; }
.chance-badge span { display: block; color: #c7e2e3; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
.chance-badge strong { display: block; margin-top: 4px; color: #fff; font-size: 26px; line-height: 1.1; }

/* Rain Graph */
.rain-card { padding: 28px 24px; }
.rain-heading { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
.rain-icon { width: 48px; height: 48px; display: grid; place-items: center; border-radius: 16px; color: #3989c9; background: #edf6ff; }
.rain-icon svg { width: 26px; height: 26px; }
.rain-pill { display: inline-block; padding: 10px 16px; border-radius: 999px; color: #287eb8; background: #eef7ff; border: 1px solid #e0effb; font-size: 14px; font-weight: 750; margin-bottom: 15px; }
.rain-bars { height: 120px; display: flex; align-items: flex-end; gap: 8px; margin-top: 10px; border-bottom: 2px solid #dce5e8; padding-bottom: 2px; }
.rain-bar { flex: 1; height: var(--h); border-radius: 8px 8px 2px 2px; background: linear-gradient(180deg, #54a7e8, #3289d1); }
.rain-bar.early { background: linear-gradient(180deg, #b7dff8, #8fcaf0); }
.rain-times { display: flex; justify-content: space-between; margin-top: 10px; color: #809096; font-size: 13px; font-weight: 700; }
h2 { margin: 0; font-size: 24px; letter-spacing: -.035em; line-height: 1.2; }
.section-sub { color: var(--muted); font-size: 14px; margin-top: 6px; }

/* Calendar & Finance */
.calendar-card { padding: 28px 24px; background: linear-gradient(150deg, #fffefa, #fff 76%); }
.heading-icon { width: 48px; height: 48px; display: grid; place-items: center; border-radius: 16px; background: var(--amber-soft); color: var(--amber); }
.heading-icon svg { width: 26px; height: 26px; }
.calendar-day { margin: 24px 0; padding: 20px; border: 1px solid #f0e8d9; border-radius: 20px; background: linear-gradient(110deg, #fff6e5, #fffaf0); }
.day-kicker { color: #98601e; font-size: 14px; font-weight: 770; text-transform: uppercase; letter-spacing: .1em; }
.day-main { display: flex; align-items: baseline; flex-wrap: wrap; gap: 10px; margin-top: 10px; font-size: 28px; font-weight: 770; }
.day-main .divider { color: #d6b47c; font-weight: 400; }
.moon { color: #bd7b22; font-size: 22px; }
.pournami { display: flex; align-items: center; gap: 12px; color: #344b57; font-size: 16px; font-weight: 700; padding-bottom: 20px; border-bottom: 1px solid var(--line); margin-bottom: 20px; }
.full-moon { display: grid; place-items: center; width: 36px; height: 36px; border-radius: 12px; background: #f6f1ff; color: #7962b0; font-size: 20px; }
.timing-label { margin: 24px 0 12px; color: var(--muted); font-size: 13px; text-transform: uppercase; letter-spacing: .11em; font-weight: 800; }
.timings { display: grid; grid-template-columns: 1fr; gap: 12px; }
.timing { padding: 14px 16px; background: #f7f9f8; border: 1px solid #eff2f1; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; }
.timing-name { color: #788891; font-size: 15px; font-weight: 650; }
.timing-time { color: #233b4a; font-size: 18px; font-weight: 750; }
.timing.good { background: #edf8f2; border-color: #e0f1e7; }
.timing.good .timing-name { color: #428369; }

/* Sun */
.sun-card { padding: 24px; }
.sun-title { display: flex; align-items: center; justify-content: space-between; font-size: 18px; font-weight: 770; }
.sun-title small { color: var(--muted); font-size: 14px; font-weight: 550; }
.sun-track { position: relative; height: 60px; margin: 24px 0 10px; }
.sun-track:before { content: ""; position: absolute; left: 5%; right: 5%; top: 30px; border-top: 3px dashed #d8e2df; }
.sun-track:after { content: ""; position: absolute; left: 5%; right: 5%; top: 10px; height: 40px; border-top: 2px solid #f2e5ca; border-radius: 100% 100% 0 0 / 100% 100% 0 0; }
.sun-point { position: absolute; top: 16px; z-index: 2; display: grid; gap: 6px; justify-items: center; transform: translateX(-50%); font-size: 15px; color: #556b75; font-weight: 700; }
.sun-point svg { width: 28px; height: 28px; padding: 4px; border-radius: 50%; background: #fff; color: #d88b38; box-shadow: 0 0 0 2px #f1e5d3; }
.sun-point.rise { left: 10%; } .sun-point.set { left: 90%; }
.daylight-pill { position: absolute; z-index: 3; left: 50%; top: 10px; transform: translateX(-50%); padding: 6px 14px; background: white; border: 2px solid #edf0ef; border-radius: 999px; color: #829096; font-size: 13px; font-weight: 700; }

/* Advice & Family */
.advice-card, .family-card { padding: 28px 24px; }
.advice-head { display: flex; align-items: center; gap: 14px; margin-bottom: 24px; }
.advice-icon { width: 48px; height: 48px; display: grid; place-items: center; border-radius: 16px; color: #bd7527; background: #fff4e3; }
.advice-icon svg { width: 26px; height: 26px; }
.advice-items { display: grid; gap: 12px; }
.advice { display: flex; align-items: center; gap: 14px; padding: 16px; background: #fafbfa; border: 1px solid #eef1ef; border-radius: 18px; }
.advice-symbol { display: grid; place-items: center; width: 36px; height: 36px; flex: none; border-radius: 10px; background: white; font-size: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.advice-text { color: #334a56; font-size: 16px; font-weight: 650; line-height: 1.4; }
.family-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 24px; }
.family-title-wrap { display: flex; align-items: center; gap: 14px; }
.family-icon { width: 48px; height: 48px; display: grid; place-items: center; border-radius: 16px; color: var(--teal); background: #eaf5f0; }
.family-icon svg { width: 26px; height: 26px; }
.count-pill { padding: 8px 14px; background: #f4f6f6; border: 1px solid #e9eeed; border-radius: 999px; color: #687c85; font-size: 14px; font-weight: 750; }
.family-columns { display: grid; grid-template-columns: 1fr; gap: 28px; }
.list-title { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; color: #778790; font-size: 13px; text-transform: uppercase; letter-spacing: .1em; font-weight: 800; }
.list-title:after { content: ""; flex: 1; border-top: 2px solid #edf0ef; }
.event-list { list-style: none; padding: 0; margin: 0; }
.event { display: flex; align-items: center; gap: 14px; padding: 14px 0; border-bottom: 1px solid #f0f3f2; }
.event:last-child { border-bottom: 0; }
.event-icon { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 12px; background: #f6f8f7; font-size: 22px; flex: none; }
.event-details { flex: 1; }
.event-name { font-size: 18px; font-weight: 750; line-height: 1.2; color: #1e293b; }
.event-badge { color: #a55b2b; background: #fff2e9; border: 1px solid #f7e4d6; padding: 6px 10px; border-radius: 8px; font-size: 12px; font-weight: 800; text-transform: uppercase; }
.event-badge.upcoming { color: #697990; background: #f1f4f8; border-color: #e8edf2; }

svg { fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
"""

def template(content):
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}">
    <style>{CSS}</style></head><body><div class="card-wrapper">{content}</div></body></html>"""

def card_weather(d):
    if d.get("rain") and d["rain"]["chance"] >= 20: big_icon = "🌧️"
    elif d["main"] == "Clear": big_icon = "🌙" if d.get("night") else "☀️"
    else: big_icon = "☁️"

    wcol = "Dangerous" if d["wind"] >= 60 else "Strong" if d["wind"] >= 40 else "Breezy"
    aqi_name = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very poor"}.get(d["aqi"], "Unknown")
    uv_v = f"{d['uv']:.0f}" if d.get("uv") else "0"
    uv_d = "Very high" if d.get("uv", 0) >= 8 else "High" if d.get("uv", 0) >= 6 else "Low"

    rain_window = ""
    if d.get("rain"):
        start = "Now" if d['rain']['now'] else f"{d['rain']['start']%12 or 12}:00 {'AM' if d['rain']['start']<12 else 'PM'}"
        end = f"{d['rain']['end']%12 or 12}:00 {'AM' if d['rain']['end']<12 else 'PM'}"
        rain_window = f"""
        <div class="rain-window">
          <div><span class="rain-window-label">Rain Risk Window</span>
          <div class="rain-window-times"><span class="window-time">{start}</span><span style="color:#8bd3ca;font-size:20px;margin:0 10px;font-weight:bold">→</span><span class="window-time">{end}</span></div>
          </div>
          <div class="chance-badge"><span>Chance</span><strong>{d['rain']['chance']}%</strong></div>
        </div>"""

    def short_h(h): return f"{h%12 or 12}{'A' if h<12 else 'P'}"
    bars, times = "", ""
    if d.get("hourly"):
        for h in range(6, 22):
            if h in d["hourly"]:
                p = d["hourly"][h]["pop"]
                cl = "early" if p < 40 else ""
                bars += f'<span class="rain-bar {cl}" style="--h:{max(8, p)}%"></span>'
                if h % 3 == 0: times += f"<span>{short_h(h)}</span>"

    return template(f"""
      <article class="dash-card weather-card">
        <div class="location-label"><svg viewBox="0 0 24 24"><path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"></path><circle cx="12" cy="10" r="2.5"></circle></svg>{d['city']} WEATHER</div>
        <div class="weather-main">
          <div><div class="temperature">{d['temp']:.0f}<sup>°</sup></div><div class="condition">{d['cond']}</div><div class="feels">Feels like {d['feels']:.0f}° &middot; H: {d['t_max']:.0f}° L: {d['t_min']:.0f}°</div></div>
          <div style="font-size:120px;line-height:1;margin-right:2%;filter:drop-shadow(0 15px 20px rgba(7,28,40,0.3))">{big_icon}</div>
        </div>
        {rain_window}
        <div class="weather-stats">
          <div class="weather-stat"><div class="stat-label"><svg viewBox="0 0 24 24"><path d="M3 8h12a3 3 0 1 0-3-3M2 12h17a3 3 0 1 1-3 3M4 16h7a3 3 0 1 1-3 3"></path></svg>Wind</div><div class="stat-value">{d['wind']:.0f} km/h</div><div class="stat-note">{wcol}</div></div>
          <div class="weather-stat"><div class="stat-label"><svg viewBox="0 0 24 24"><path d="M12 3c3 4 6 7 6 11a6 6 0 0 1-12 0c0-4 3-7 6-11Z"></path><path d="M9 15a3 3 0 0 0 3 3"></path></svg>Air quality</div><div class="stat-value">{aqi_name}</div><div class="stat-note">AQI {d['aqi']}</div></div>
        </div>
      </article>

      <article class="dash-card rain-card">
        <div class="rain-heading"><div class="rain-icon"><svg viewBox="0 0 24 24"><path d="M20 15.5a4.5 4.5 0 0 0-.8-8.93A7 7 0 0 0 5.6 8.4 3.8 3.8 0 0 0 6 16h14"></path><path d="m8 19-1 2m6-2-1 2m6-2-1 2"></path></svg></div><div><h2>Hourly Rain Outlook</h2><div class="section-sub">Relative chance trend (6 AM - 9 PM)</div></div></div>
        <div class="rain-pill">{d['rain']['chance'] if d.get('rain') else 0}% peak chance today</div>
        <div class="rain-bars">{bars}</div>
        <div class="rain-times">{times}</div>
      </article>
    """)

def card_advice(d):
    p = d.get("panchangam", {})
    adv = "".join(f'<div class="advice"><div class="advice-symbol">{i}</div><div class="advice-text">{esc(t)}</div></div>' for i, t in d["advice"])
    sp = "".join(f'<div class="pournami"><span class="full-moon">{i.split(" ")[0]}</span><span>{esc(" ".join(i.split(" ")[1:]))}</span></div>' for i in p.get("special", []))

    gold_html = ""
    if d.get("metals"):
        gold_html = f"""
        <div class="timing-label" style="margin-top:28px">Today's Market Rates</div>
        <div class="timings">
          <div class="timing good"><span class="timing-name">22K Gold (1g)</span><span class="timing-time">₹{d['metals']['gold22']}</span></div>
          <div class="timing"><span class="timing-name">Silver (1g)</span><span class="timing-time">₹{d['metals']['silver']}</span></div>
        </div>"""

    return template(f"""
      <article class="dash-card calendar-card">
        <div class="card-heading" style="display:flex; gap:16px; margin-bottom:24px"><div class="heading-icon"><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"></rect><path d="M16 3v4M8 3v4M3 10h18"></path><path d="M8 14h.01M12 14h.01M16 14h.01M8 17h.01M12 17h.01"></path></svg></div><div><h2>Hindu Calendar</h2><div class="section-sub">People, timings & markets</div></div></div>
        <div class="calendar-day"><div class="day-kicker">Tamil calendar &middot; {d['now'].strftime('%A')}</div><div class="day-main"><span>{p.get('tamil_date')}</span><span class="divider">|</span><span class="moon">☾ {p.get('nakshatra')}</span></div></div>
        {sp}
        <div class="timing-label">Daily timings</div>
        <div class="timings">
          <div class="timing good"><span class="timing-name">நல்ல நேரம்</span><span class="timing-time">{p.get('nalla')}</span></div>
          <div class="timing"><span class="timing-name">ராகு காலம்</span><span class="timing-time">{p.get('rahu')}</span></div>
          <div class="timing"><span class="timing-name">எமகண்டம்</span><span class="timing-time">{p.get('yama')}</span></div>
          <div class="timing"><span class="timing-name">குளிகை</span><span class="timing-time">{p.get('kuli')}</span></div>
        </div>
        {gold_html}
      </article>

      <article class="dash-card sun-card">
        <div class="sun-title"><span>Sunrise & sunset</span><small>Local time</small></div>
        <div class="sun-track">
          <div class="sun-point rise"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2"></path></svg><span>{d['sunrise'].strftime('%I:%M %p').lstrip('0')}</span></div>
          <div class="daylight-pill">Daylight</div>
          <div class="sun-point set"><svg viewBox="0 0 24 24"><path d="M3 17h18M5 21h14M7 17a5 5 0 0 1 10 0M12 3v2m7.07.93-1.42 1.42M21 12h-2M5 12H3m1.93-6.07 1.42 1.42"></path></svg><span>{d['sunset'].strftime('%I:%M %p').lstrip('0')}</span></div>
        </div>
      </article>

      <article class="dash-card advice-card">
        <div class="advice-head"><div class="advice-icon"><svg viewBox="0 0 24 24"><path d="M12 3v2m7.07.93-1.42 1.42M21 12h-2M5 12H3m1.93-6.07 1.42 1.42M8 17l-1 4m9-4 1 4M7 13a5 5 0 0 1 10 0c0 2-1 3-2 4H9c-1-1-2-2-2-4Z"></path></svg></div><div><h2>Daily Advice</h2><div class="section-sub">A few useful things to keep in mind</div></div></div>
        <div class="advice-items">{adv}</div>
      </article>
    """)

def card_events(d):
    tdy = "".join(f'<li class="event"><span class="event-icon">{i["icon"]}</span><div class="event-details"><div class="event-name">{esc(i["text"])}</div></div><span class="event-badge">TODAY</span></li>' for i in d["today"])
    if not tdy: tdy = '<div style="font-size:15px;color:var(--muted);padding:10px 0;font-weight:500">No events today.</div>'
    
    up = ""
    for i in d["upcoming"]:
        cd_text = "Tomorrow" if i['days_left'] == 1 else f"In {i['days_left']} Days"
        up += f'<li class="event"><span class="event-icon">{i["icon"]}</span><div class="event-details"><div class="event-name">{esc(i["text"])}</div></div><span class="event-badge upcoming">{cd_text}</span></li>'
    if not up: up = '<div style="font-size:15px;color:var(--muted);padding:10px 0;font-weight:500">No upcoming events.</div>'

    count = len(d['today']) + len(d['upcoming'])
    
    return template(f"""
      <article class="dash-card family-card">
        <div class="family-top"><div class="family-title-wrap"><div class="family-icon"><svg viewBox="0 0 24 24"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"></path></svg></div><div><h2>Family Calendar</h2><div class="section-sub">People, plans & bills</div></div></div><span class="count-pill">{count} items</span></div>
        <div class="family-columns">
          <div><div class="list-title">Happening today</div><ul class="event-list">{tdy}</ul></div>
          <div><div class="list-title">Coming up</div><ul class="event-list">{up}</ul></div>
        </div>
      </article>
    """)

def build_birthday_html(name, age):
    age_line = f"Turns {age} today!" if age else "Wishing you a wonderful year ahead!"
    return template(f"""
    <div class="dash-card" style="background:linear-gradient(135deg,#7561af 0%,#a585cf 100%);padding:100px 40px;text-align:center;position:relative;overflow:hidden;border:none">
        <div style="font-size:160px;margin-bottom:30px;filter:drop-shadow(0 10px 20px rgba(0,0,0,0.15));position:relative;z-index:2">🎂</div>
        <div style="font-size:36px;font-weight:800;color:#e8dff5;letter-spacing:4px;text-transform:uppercase;margin-bottom:20px;position:relative;z-index:2">Happy Birthday</div>
        <div style="font-size:75px;font-weight:800;color:#ffffff;line-height:1.1;margin-bottom:40px;position:relative;z-index:2;letter-spacing:-1px">{esc(name)}</div>
        <div style="background:rgba(255,255,255,0.2);color:#ffffff;font-size:28px;font-weight:700;padding:16px 40px;border-radius:50px;display:inline-block;position:relative;z-index:2;backdrop-filter:blur(10px);border:2px solid rgba(255,255,255,0.3)">{esc(age_line)}</div>
    </div>
    """)
