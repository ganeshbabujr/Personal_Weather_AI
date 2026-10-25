import html

esc = html.escape
FONT = "https://fonts.googleapis.com/css2?family=Inter:wght@350;400;550;630;650;700;750;770;800&display=swap"
CSS = """
:root {
  --ink: #172a3a; --muted: #6c7d8b; --line: #e7eceb; --paper: #ffffff; --canvas: #f4f7f6;
  --teal: #167d73; --teal-dark: #105d58; --teal-soft: #e8f5f1;
  --amber: #bd7527; --amber-soft: #fff4de; --violet: #7561af;
  --shadow: 0 18px 50px rgba(31, 54, 67, .07), 0 2px 8px rgba(31, 54, 67, .035);
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--canvas); color: var(--ink); font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; width: 800px; padding: 20px; }

/* Wrapper to fool Playwright into capturing the whole group */
.card-wrapper { display: flex; flex-direction: column; gap: 18px; width: 100%; }

.dash-card { background: var(--paper); border: 1px solid #e9eeed; border-radius: 24px; box-shadow: var(--shadow); overflow: hidden; }

/* Weather Card */
.weather-card { position: relative; isolation: isolate; min-height: 0; padding: 26px 28px 22px; color: #f7fbff; background: linear-gradient(123deg, #19394b 0%, #24596a 52%, #307b83 100%); border: 0; }
.weather-card:before, .weather-card:after { content: ""; position: absolute; z-index: -1; border-radius: 50%; pointer-events: none; }
.weather-card:before { width: 320px; height: 320px; right: -105px; top: -120px; background: radial-gradient(circle at 35% 40%, #c7e5d955, #b5d7e011 65%, transparent 69%); }
.weather-card:after { width: 240px; height: 240px; right: 105px; bottom: -195px; border: 1px solid #ffffff17; box-shadow: 0 0 0 28px #ffffff08, 0 0 0 58px #ffffff06; }
.weather-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.location-label { color: #d1e3e6; font-size: 13px; display: flex; align-items: center; gap: 7px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.location-label svg { width: 15px; height: 15px; color: #b7e8d8; }
.weather-tag { font-size: 11px; color: #d9f6ec; background: #ffffff16; border: 1px solid #ffffff24; padding: 7px 10px; border-radius: 999px; font-weight: 700; }
.weather-main { display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-top: 23px; }
.temperature { font-size: 104px; line-height: .9; letter-spacing: -.085em; font-weight: 350; }
.temperature sup { font-size: .39em; vertical-align: top; line-height: 1.65; margin-left: 5px; letter-spacing: -.04em; font-weight: 450; }
.condition { margin-top: 13px; font-size: 23px; letter-spacing: -.035em; font-weight: 660; }
.feels { margin-top: 8px; font-size: 13px; color: #d1e0e3; }
.weather-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 9px; margin-top: 13px; }
.weather-stat { min-width: 0; padding: 12px 13px; border: 1px solid #ffffff21; background: #ffffff12; border-radius: 15px; backdrop-filter: blur(6px); }
.stat-label { display: flex; align-items: center; gap: 6px; color: #d1e3e6; font-size: 11px; font-weight: 630; }
.stat-label svg { width: 14px; height: 14px; color: #b9ecdc; }
.stat-value { margin-top: 6px; font-size: 16px; font-weight: 760; letter-spacing: -.025em; white-space: nowrap; }
.stat-note { margin-top: 2px; font-size: 10px; color: #ccdcdf; }

/* Rain Window */
.rain-window { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: 20px; padding: 13px 15px; border: 1px solid #d8f0ee38; border-radius: 17px; background: linear-gradient(110deg, #e5fbf015, #d5f5ff13); }
.rain-window-label { display: block; color: #bde8e1; font-size: 9px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.rain-window-times { display: flex; align-items: center; gap: 10px; margin-top: 5px; }
.window-time { color: #fff; font-size: 16px; font-weight: 780; letter-spacing: -.025em; }
.window-duration { margin-left: 3px; color: #c9e5e4; font-size: 10px; font-weight: 650; }
.window-caption { margin-top: 4px; color: #c2d9dc; font-size: 10px; line-height: 1.4; }
.chance-badge { min-width: 66px; padding: 8px 11px; border: 1px solid #ffffff26; border-radius: 13px; text-align: center; background: #ffffff14; }
.chance-badge span { display: block; color: #c7e2e3; font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
.chance-badge strong { display: block; margin-top: 2px; color: #fff; font-size: 19px; line-height: 1.1; }

/* Rain Graph */
.rain-card { padding: 20px 23px 20px; }
.rain-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.rain-heading { display: flex; align-items: center; gap: 11px; }
.rain-icon { width: 38px; height: 38px; display: grid; place-items: center; border-radius: 13px; color: #3989c9; background: #edf6ff; }
.rain-pill { padding: 7px 10px; border-radius: 999px; color: #287eb8; background: #eef7ff; border: 1px solid #e0effb; font-size: 11px; font-weight: 750; white-space: nowrap; }
.rain-bars { height: 100px; position: relative; display: flex; align-items: flex-end; justify-content: space-between; gap: 7px; margin: 17px 3px 0; padding: 0 1px; border-bottom: 1px solid #dce5e8; background: repeating-linear-gradient(to bottom, transparent 0, transparent 31px, #eef2f3 32px); }
.rain-bar { flex: 1; min-width: 5px; height: var(--h); border-radius: 7px 7px 2px 2px; background: linear-gradient(180deg, #54a7e8, #3289d1); box-shadow: inset 0 1px #ffffff38; }
.rain-bar.early { background: linear-gradient(180deg, #b7dff8, #8fcaf0); }
.rain-times { display: flex; justify-content: space-between; margin: 7px 1px 0; color: #809096; font-size: 10px; font-weight: 650; }
h2 { margin: 0; font-size: 18px; letter-spacing: -.035em; line-height: 1.2; }
.section-sub { color: var(--muted); font-size: 11px; margin-top: 4px; }

/* Calendar & Finance */
.calendar-card { padding: 23px 24px 22px; background: linear-gradient(150deg, #fffefa, #fff 76%); }
.card-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.heading-left { display: flex; align-items: center; gap: 11px; }
.heading-icon { width: 39px; height: 39px; display: grid; place-items: center; flex: none; border-radius: 13px; background: var(--amber-soft); color: var(--amber); }
.calendar-day { margin: 20px 0 17px; padding: 15px 16px; border: 1px solid #f0e8d9; border-radius: 17px; background: linear-gradient(110deg, #fff6e5, #fffaf0); }
.day-kicker { color: #98601e; font-size: 11px; font-weight: 750; text-transform: uppercase; letter-spacing: .1em; }
.day-main { display: flex; align-items: baseline; flex-wrap: wrap; gap: 8px; margin-top: 7px; font-size: 21px; font-weight: 770; letter-spacing: -.04em; }
.day-main .divider { color: #d6b47c; font-weight: 400; }
.moon { color: #bd7b22; font-size: 17px; }
.day-tamil { color: #6a7478; font-size: 12px; font-weight: 550; margin-top: 6px; }
.pournami { display: flex; align-items: center; gap: 9px; color: #344b57; font-size: 13px; font-weight: 650; padding: 0 3px 14px; border-bottom: 1px solid var(--line); }
.full-moon { display: grid; place-items: center; width: 28px; height: 28px; border-radius: 9px; background: #f6f1ff; color: #7962b0; font-size: 16px; }
.timing-label { margin: 15px 0 10px; color: var(--muted); font-size: 10px; text-transform: uppercase; letter-spacing: .11em; font-weight: 750; }
.timings { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.timing { padding: 9px 10px; background: #f7f9f8; border: 1px solid #eff2f1; border-radius: 12px; min-width: 0; }
.timing-name { display: block; color: #788891; font-size: 10px; font-weight: 650; }
.timing-time { display: block; margin-top: 4px; font-size: 12px; color: #233b4a; font-weight: 730; letter-spacing: -.025em; white-space: nowrap; }
.timing.good { background: #edf8f2; border-color: #e0f1e7; }
.timing.good .timing-name { color: #428369; }

/* Sun */
.sun-card { padding: 19px 22px 16px; }
.sun-title { display: flex; align-items: center; justify-content: space-between; font-size: 14px; font-weight: 750; }
.sun-title small { color: var(--muted); font-size: 11px; font-weight: 550; }
.sun-track { position: relative; height: 45px; margin: 16px 3px 1px; }
.sun-track:before { content: ""; position: absolute; left: 2%; right: 2%; top: 23px; border-top: 2px dashed #d8e2df; }
.sun-track:after { content: ""; position: absolute; left: 2%; right: 2%; top: 8px; height: 31px; border-top: 1px solid #f2e5ca; border-radius: 100% 100% 0 0 / 100% 100% 0 0; }
.sun-point { position: absolute; top: 14px; z-index: 2; display: grid; gap: 3px; justify-items: center; transform: translateX(-50%); font-size: 11px; color: #556b75; font-weight: 650; }
.sun-point svg { width: 20px; height: 20px; padding: 3px; border-radius: 50%; background: #fff; color: #d88b38; box-shadow: 0 0 0 1px #f1e5d3; }
.sun-point.rise { left: 8%; } .sun-point.set { left: 92%; }
.daylight-pill { position: absolute; z-index: 3; left: 50%; top: 9px; transform: translateX(-50%); padding: 4px 9px; background: white; border: 1px solid #edf0ef; border-radius: 999px; color: #829096; font-size: 9px; white-space: nowrap; }

/* Advice & Family */
.advice-card, .family-card { padding: 22px 24px 21px; }
.advice-head { display: flex; align-items: center; gap: 11px; margin-bottom: 12px; }
.advice-icon { width: 39px; height: 39px; display: grid; place-items: center; border-radius: 13px; color: #bd7527; background: #fff4e3; }
.advice-items { display: grid; gap: 8px; }
.advice { display: flex; align-items: flex-start; gap: 10px; padding: 10px 11px; background: #fafbfa; border: 1px solid #eef1ef; border-radius: 13px; }
.advice-symbol { display: grid; place-items: center; width: 25px; height: 25px; flex: none; border-radius: 8px; background: white; font-size: 14px; }
.advice-text { color: #334a56; font-size: 11px; font-weight: 620; line-height: 1.45; }
.family-top { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 14px; }
.family-title-wrap { display: flex; align-items: center; gap: 11px; }
.family-icon { width: 39px; height: 39px; display: grid; place-items: center; border-radius: 13px; color: var(--teal); background: #eaf5f0; }
.count-pill { padding: 7px 10px; background: #f4f6f6; border: 1px solid #e9eeed; border-radius: 999px; color: #687c85; font-size: 10px; font-weight: 700; white-space: nowrap; }
.family-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.list-title { display: flex; align-items: center; gap: 8px; margin: 4px 0 8px; color: #778790; font-size: 10px; text-transform: uppercase; letter-spacing: .1em; font-weight: 780; }
.list-title:after { content: ""; flex: 1; border-top: 1px solid #edf0ef; }
.event-list { list-style: none; padding: 0; margin: 0; }
.event { display: grid; grid-template-columns: 34px minmax(0,1fr) auto; align-items: center; gap: 9px; padding: 10px 0; border-bottom: 1px solid #f0f3f2; }
.event:last-child { border-bottom: 0; }
.event-icon { width: 32px; height: 32px; display: grid; place-items: center; border-radius: 11px; background: #f6f8f7; font-size: 17px; }
.event-name { font-size: 12px; font-weight: 700; line-height: 1.3; }
.event-meta { margin-top: 3px; color: var(--muted); font-size: 10px; }
.event-badge { color: #a55b2b; background: #fff2e9; border: 1px solid #f7e4d6; padding: 5px 7px; border-radius: 999px; font-size: 9px; font-weight: 750; white-space: nowrap; }
.event-badge.upcoming { color: #697990; background: #f1f4f8; border-color: #e8edf2; }

svg { fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
"""

def template(content):
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}">
    <style>{CSS}</style></head><body><div class="card" style="box-shadow:none; border:none; background:transparent; padding:0; margin:0;"><div class="card-wrapper">{content}</div></div></body></html>"""

def card_weather(d):
    # Dynamic Weather Icon
    if d.get("rain") and d["rain"]["chance"] >= 20:
        big_icon = "🌧️"
    elif d["main"] == "Clear":
        big_icon = "🌙" if d.get("night") else "☀️"
    else:
        big_icon = "☁️"

    # Format values
    wcol = "Dangerous" if d["wind"] >= 60 else "Strong" if d["wind"] >= 40 else "Calm to breezy"
    aqi_name = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very poor"}.get(d["aqi"], "Unknown")
    uv_v = f"{d['uv']:.0f}" if d.get("uv") else "0"
    uv_d = "Very high" if d.get("uv", 0) >= 8 else "High" if d.get("uv", 0) >= 6 else "Moderate" if d.get("uv", 0) >= 3 else "Low"

    # Rain Window HTML
    rain_window = ""
    if d.get("rain"):
        start = "Now" if d['rain']['now'] else f"{d['rain']['start']%12 or 12}:00 {'AM' if d['rain']['start']<12 else 'PM'}"
        end = f"{d['rain']['end']%12 or 12}:00 {'AM' if d['rain']['end']<12 else 'PM'}"
        rain_window = f"""
        <div class="rain-window">
          <div><span class="rain-window-label">Estimated rain-risk window</span>
          <div class="rain-window-times"><span class="window-time">{start}</span><span style="color:#8bd3ca;font-size:15px;margin:0 10px">→</span><span class="window-time">{end}</span></div>
          <div class="window-caption">Showers may be intermittent.</div></div>
          <div class="chance-badge"><span>Chance</span><strong>{d['rain']['chance']}%</strong></div>
        </div>"""

    # Hourly Rain Graph HTML
    def short_h(h): return f"{h%12 or 12}{'A' if h<12 else 'P'}"
    bars = ""
    times = ""
    if d.get("hourly"):
        for h in range(6, 22):
            if h in d["hourly"]:
                p = d["hourly"][h]["pop"]
                cl = "early" if p < 40 else ""
                bars += f'<span class="rain-bar {cl}" style="--h:{max(5, p)}%"></span>'
                if h % 3 == 0: times += f"<span>{short_h(h)}</span>"

    return template(f"""
      <article class="dash-card weather-card">
        <div class="weather-head">
          <div class="location-label"><svg viewBox="0 0 24 24"><path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"></path><circle cx="12" cy="10" r="2.5"></circle></svg>{d['city']} WEATHER</div>
          <span class="weather-tag">Current conditions</span>
        </div>
        <div class="weather-main">
          <div><div class="temperature">{d['temp']:.0f}<sup>°</sup></div><div class="condition">{d['cond']}</div><div class="feels">Feels like {d['feels']:.0f}° &middot; High {d['t_max']:.0f}° &middot; Low {d['t_min']:.0f}°</div></div>
          <div style="font-size:110px;line-height:1;margin-right:4%;filter:drop-shadow(0 13px 14px rgba(7,28,40,0.3))">{big_icon}</div>
        </div>
        {rain_window}
        <div class="weather-stats">
          <div class="weather-stat"><div class="stat-label"><svg viewBox="0 0 24 24"><path d="M3 8h12a3 3 0 1 0-3-3M2 12h17a3 3 0 1 1-3 3M4 16h7a3 3 0 1 1-3 3"></path></svg>Wind</div><div class="stat-value">{d['wind']:.0f} km/h</div><div class="stat-note">{wcol}</div></div>
          <div class="weather-stat"><div class="stat-label"><svg viewBox="0 0 24 24"><path d="M12 3c3 4 6 7 6 11a6 6 0 0 1-12 0c0-4 3-7 6-11Z"></path><path d="M9 15a3 3 0 0 0 3 3"></path></svg>Air quality</div><div class="stat-value">{aqi_name}</div><div class="stat-note">AQI {d['aqi']} &middot; PM2.5 {d['pm25']:.0f}</div></div>
          <div class="weather-stat"><div class="stat-label"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"></path></svg>UV peak</div><div class="stat-value">{uv_v} &middot; {uv_d}</div><div class="stat-note">Protect your skin</div></div>
        </div>
      </article>

      <article class="dash-card rain-card">
        <div class="rain-top"><div class="rain-heading"><div class="rain-icon"><svg viewBox="0 0 24 24"><path d="M20 15.5a4.5 4.5 0 0 0-.8-8.93A7 7 0 0 0 5.6 8.4 3.8 3.8 0 0 0 6 16h14"></path><path d="m8 19-1 2m6-2-1 2m6-2-1 2"></path></svg></div><div><h2>Hourly rain outlook</h2><div class="section-sub">Relative chance trend from 6 AM to 9 PM</div></div></div><span class="rain-pill">{d['rain']['chance'] if d.get('rain') else 0}% chance peak</span></div>
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
        <div class="timing-label" style="margin-top:20px">Today's Market Rates</div>
        <div class="timings">
          <div class="timing good"><span class="timing-name">22K Gold (1g)</span><span class="timing-time">₹{d['metals']['gold22']}</span></div>
          <div class="timing"><span class="timing-name">Silver (1g)</span><span class="timing-time">₹{d['metals']['silver']}</span></div>
        </div>"""

    return template(f"""
      <article class="dash-card calendar-card">
        <div class="card-heading"><div class="heading-left"><div class="heading-icon"><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"></rect><path d="M16 3v4M8 3v4M3 10h18"></path><path d="M8 14h.01M12 14h.01M16 14h.01M8 17h.01M12 17h.01"></path></svg></div><div><h2>Hindu calendar</h2><div class="section-sub">People, timings & markets</div></div></div></div>
        <div class="calendar-day"><div class="day-kicker">Tamil calendar &middot; {d['now'].strftime('%A')}</div><div class="day-main"><span>{p.get('tamil_date')}</span><span class="divider">|</span><span class="moon">☾ {p.get('nakshatra')}</span></div></div>
        {sp}
        <div class="timing-label">Daily timings</div>
        <div class="timings">
          <div class="timing good"><span class="timing-name">Nalla Neram &middot; நல்ல நேரம்</span><span class="timing-time">{p.get('nalla')}</span></div>
          <div class="timing"><span class="timing-name">Rahu Kalam &middot; ராகு காலம்</span><span class="timing-time">{p.get('rahu')}</span></div>
          <div class="timing"><span class="timing-name">Yamagandam &middot; எமகண்டம்</span><span class="timing-time">{p.get('yama')}</span></div>
          <div class="timing"><span class="timing-name">Gulikai &middot; குளிகை</span><span class="timing-time">{p.get('kuli')}</span></div>
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
        <div class="advice-head"><div class="advice-icon"><svg viewBox="0 0 24 24"><path d="M12 3v2m7.07.93-1.42 1.42M21 12h-2M5 12H3m1.93-6.07 1.42 1.42M8 17l-1 4m9-4 1 4M7 13a5 5 0 0 1 10 0c0 2-1 3-2 4H9c-1-1-2-2-2-4Z"></path></svg></div><div><h2>Daily advice</h2><div class="section-sub">A few useful things to keep in mind</div></div></div>
        <div class="advice-items">{adv}</div>
      </article>
    """)

def card_events(d):
    tdy = "".join(f'<li class="event"><span class="event-icon">{i["icon"]}</span><div><div class="event-name">{esc(i["text"])}</div></div><span class="event-badge">TODAY</span></li>' for i in d["today"])
    if not tdy: tdy = '<div style="font-size:12px;color:var(--muted);padding:10px 0">No events today.</div>'
    
    up = ""
    for i in d["upcoming"]:
        cd_text = "Tomorrow" if i['days_left'] == 1 else f"in {i['days_left']} days"
        up += f'<li class="event"><span class="event-icon">{i["icon"]}</span><div><div class="event-name">{esc(i["text"])}</div></div><span class="event-badge upcoming">{cd_text}</span></li>'
    if not up: up = '<div style="font-size:12px;color:var(--muted);padding:10px 0">No upcoming events.</div>'

    count = len(d['today']) + len(d['upcoming'])
    
    return template(f"""
      <article class="dash-card family-card">
        <div class="family-top"><div class="family-title-wrap"><div class="family-icon"><svg viewBox="0 0 24 24"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"></path></svg></div><div><h2>Family calendar</h2><div class="section-sub">People, plans & bills in one place</div></div></div><span class="count-pill">{count} items</span></div>
        <div class="family-columns">
          <div><div class="list-title">Happening today</div><ul class="event-list">{tdy}</ul></div>
          <div><div class="list-title">Coming up</div><ul class="event-list">{up}</ul></div>
        </div>
      </article>
    """)

def card_rain_alert(d):
    def fmt(dt): return dt.strftime("%I:%M %p").lstrip("0")
    def fmt_h(h): return f"{h % 12 or 12}:00 {'AM' if h < 12 else 'PM'}"
    start = "Now" if d['rain']['now'] else fmt_h(d['rain']['start'])
    chance = d['rain']['chance']
    end_time = fmt_h(d['rain']['end'])
    
    if d['rain']['now']:
        en_msg = f"Rain is expected to continue until {end_time}. Please secure outdoor items."
        ta_msg = f"{end_time} வரை மழை தொடர வாய்ப்புள்ளது. பாதுகாப்பாக இருக்கவும்."
    else:
        en_msg = f"Rain expected to start around {start} and last until {end_time}."
        ta_msg = f"{start} அளவில் மழை தொடங்கி {end_time} வரை தொடரலாம். பாதுகாப்பாக இருக்கவும்."

    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}">
    <style>
    *{{box-sizing:border-box;margin:0;padding:0;font-family:'Inter',sans-serif}}
    .rain-bg {{ background: radial-gradient(circle at 50% -20%, #1e293b 0%, #020617 100%); padding: 60px; min-height: 100vh; display: flex; flex-direction: column; width: 800px; }}
    .alert-title {{ font-size: 68px; font-weight: 800; background: linear-gradient(90deg, #ef4444, #fca5a5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 3px; text-transform: uppercase; text-align: center; margin-top: 15px; }}
    .alert-sub {{ font-size: 38px; color: #fca5a5; margin-top: 15px; font-weight: 500; text-align: center; letter-spacing: 1px; opacity: 0.9; }}
    .city {{ font-size: 52px; font-weight: 600; color: #fff; text-align: center; margin: 50px 0 35px; letter-spacing: -1px; }}
    .bento {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 30px; }}
    .box {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 32px; padding: 40px 30px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
    .lbl {{ font-size: 26px; color: #94a3b8; margin-bottom: 16px; font-weight: 400; }}
    .val {{ font-size: 58px; color: #38bdf8; font-weight: 600; line-height: 1; }}
    .msg-box {{ background: linear-gradient(90deg, rgba(56,189,248,0.1) 0%, rgba(56,189,248,0) 100%); border-left: 6px solid #38bdf8; padding: 40px; border-radius: 12px 32px 32px 12px; }}
    .en-msg {{ font-size: 34px; font-weight: 500; color: #f8fafc; line-height: 1.4; margin-bottom: 16px; }}
    .ta-msg {{ font-size: 30px; color: #cbd5e1; line-height: 1.5; }}
    .foot {{ text-align: center; color: #475569; font-size: 24px; margin-top: auto; padding-top: 40px; }}
    </style></head><body><div class="card rain-bg" style="border:none">
    
    <div style="text-align:center; font-size: 160px; margin-bottom: 10px; line-height: 1; filter: drop-shadow(0 15px 25px rgba(0,0,0,0.6));">⛈️</div>
    <div class="alert-title">SUDDEN RAIN ALERT</div>
    <div class="alert-sub">திடீர் மழை எச்சரிக்கை</div>
    <div class="city">{esc(d['city'])}</div>
    
    <div class="bento">
        <div class="box"><div class="lbl">Expected Start</div><div class="val">{start}</div></div>
        <div class="box"><div class="lbl">Probability</div><div class="val">{chance}%</div></div>
    </div>
    
    <div class="msg-box"><div class="en-msg">{en_msg}</div><div class="ta-msg">{ta_msg}</div></div>
    <div class="foot">System Update: {fmt(d['now'])}</div>
    </div></body></html>"""

def build_birthday_html(name, age):
    age_line = f"Turns {age} today!" if age else "Wishing you a wonderful year ahead!"
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}">
    <style>
    *{{box-sizing:border-box;margin:0;padding:0;font-family:'Inter',sans-serif}}
    body{{width:800px;background:#f4f7f6;padding:20px}}
    .b-card{{background:linear-gradient(135deg,#7561af 0%,#a585cf 100%);border-radius:40px;padding:80px 40px;text-align:center;box-shadow:0 18px 50px rgba(117,97,175,0.25);position:relative;overflow:hidden}}
    .icon{{font-size:140px;margin-bottom:20px;filter:drop-shadow(0 10px 20px rgba(0,0,0,0.15));position:relative;z-index:2}}
    .hbd{{font-size:45px;font-weight:800;color:#e8dff5;letter-spacing:3px;text-transform:uppercase;margin-bottom:15px;position:relative;z-index:2}}
    .name{{font-size:80px;font-weight:800;color:#ffffff;line-height:1.1;margin-bottom:35px;position:relative;z-index:2;letter-spacing:-1px}}
    .age-pill{{background:rgba(255,255,255,0.2);color:#ffffff;font-size:26px;font-weight:600;padding:12px 35px;border-radius:50px;display:inline-block;box-shadow:0 8px 20px rgba(0,0,0,0.05);position:relative;z-index:2;backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.3)}}
    .bg-shape1{{position:absolute;top:-50px;left:-50px;width:300px;height:300px;background:radial-gradient(circle,rgba(255,255,255,0.2) 0%,transparent 70%);border-radius:50%;z-index:1}}
    .bg-shape2{{position:absolute;bottom:-100px;right:-50px;width:400px;height:400px;background:radial-gradient(circle,rgba(255,255,255,0.15) 0%,transparent 70%);border-radius:50%;z-index:1}}
    </style></head><body>
    <div class="card b-card" style="border:none">
        <div class="bg-shape1"></div><div class="bg-shape2"></div>
        <div class="icon">🎂</div>
        <div class="hbd">Happy Birthday</div>
        <div class="name">{esc(name)}</div>
        <div class="age-pill">{esc(age_line)}</div>
    </div>
    </body></html>"""
