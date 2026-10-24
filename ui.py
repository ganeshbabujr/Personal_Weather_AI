import html

esc = html.escape
FONT = "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap"
CSS = """
*{box-sizing:border-box;margin:0;padding:0;font-family:'Outfit',sans-serif}
body{width:800px;color:#0F172A;background:#0f172a}
.card{padding:40px;min-height:100vh;display:flex;flex-direction:column;gap:20px}
.theme-default{background:linear-gradient(145deg,#f8fafc,#e2e8f0)}
.theme-festival{background:radial-gradient(circle at top right,#fff7ed 0%,#ffedd5 100%);border:4px solid #f97316}
.theme-night{background:linear-gradient(145deg,#1e293b,#0f172a);color:#f8fafc}
.theme-night .box{background:rgba(255,255,255,0.05);color:#f8fafc;border:1px solid rgba(255,255,255,0.1)}
.theme-night .t{color:#e2e8f0}
.head{display:flex;justify-content:space-between;align-items:center;padding-bottom:20px}
.title{font-size:42px;font-weight:700;letter-spacing:-1px}
.date{font-size:24px;color:#64748b;margin-top:5px}
.theme-night .date{color:#94a3b8}
.bento{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}
.box{background:#fff;border-radius:32px;padding:30px;box-shadow:0 10px 30px rgba(0,0,0,0.03);border:1px solid rgba(255,255,255,0.5)}
.box-large{grid-column:span 2}
.t{font-size:24px;font-weight:600;color:#475569;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px}
.row{display:flex;align-items:center;gap:20px;font-size:28px;padding:12px 0;border-bottom:1px solid rgba(0,0,0,0.05)}
.row:last-child{border-bottom:none}
.theme-night .row{border-bottom:1px solid rgba(255,255,255,0.1)}
.i{font-size:38px;width:50px;text-align:center}
.v{font-size:48px;font-weight:700;line-height:1.1}
.val-sub{font-size:22px;color:#64748b;margin-top:5px}
.theme-night .val-sub{color:#94a3b8}
.gold-grid{display:grid;grid-template-columns:1fr 1fr;gap:15px;text-align:center;margin-top:10px}
.gold-val{font-size:32px;font-weight:700;color:#b45309}
"""

def layout(title, d, content, theme="default"):
    if d.get("night") and theme == "default": theme = "night"
    icon = "🎊" if theme == "festival" else "🌙" if theme == "night" else "☀️"
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}"><style>{CSS}</style></head>
    <body><div class="card theme-{theme}">
    <div class="head"><div><div class="title">{title}</div><div class="date">{d["now"].strftime('%A, %d %b %Y')}</div></div>
    <div style="font-size:60px">{icon}</div></div>
    {content}</div></body></html>"""

def card_weather(d):
    bars = "".join(f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end"><div style="width:100%;background:{"#38bdf8" if d["hourly"][h]["pop"]>=50 else "#94a3b8" if d.get("night") else "#e2e8f0"};height:{max(10, d["hourly"][h]["pop"])}px;border-radius:10px"></div><div style="margin-top:10px;font-size:18px">{h%12 or 12}</div></div>' for h in range(6,22,2) if h in d["hourly"])
    
    r_start = f"Starting {d['rain']['start']}:00" if d.get('rain') else "No rain today"
    c = f"""
    <div class="bento">
        <div class="box box-large" style="display:flex;justify-content:space-between;align-items:center;background:linear-gradient(135deg,#38bdf8,#0284c7);color:#fff;border:none">
            <div><div style="font-size:120px;font-weight:700;line-height:1;letter-spacing:-4px">{d['temp']:.0f}°</div><div style="font-size:32px;margin-top:10px">{d['cond']}</div></div>
            <div style="text-align:right"><div style="font-size:100px">{d['icon']}</div><div style="font-size:24px;opacity:0.9">H:{d['t_max']:.0f}° L:{d['t_min']:.0f}°</div></div>
        </div>
        <div class="box"><div class="t">🌧️ Rain</div><div class="v">{d['rain']['chance'] if d.get('rain') else 0}%</div><div class="val-sub">{r_start}</div></div>
        <div class="box"><div class="t">💨 Wind</div><div class="v">{d['wind']:.0f}</div><div class="val-sub">km/h</div></div>
        <div class="box"><div class="t">🫁 AQI</div><div class="v">{d['aqi']}</div><div class="val-sub">PM2.5: {d['pm25']:.0f}</div></div>
        <div class="box"><div class="t">🧴 UV Index</div><div class="v">{d['uv'] if d.get('uv') else 0}</div><div class="val-sub">Peak</div></div>
        <div class="box box-large"><div class="t">Hourly Rain Chance</div><div style="display:flex;gap:10px;height:100px;margin-top:20px">{bars}</div></div>
    </div>"""
    return layout(f"{d['city']} Weather", d, c)

def card_advice(d):
    p = d.get("panchangam", {})
    adv = "".join(f'<div class="row"><span class="i">{i}</span><span>{esc(t)}</span></div>' for i, t in d["advice"])
    
    gold_html = ""
    if d.get("metals"):
        gold_html = f"""<div class="box box-large" style="background:#fffbeb;border-color:#fde68a"><div class="t" style="color:#d97706">💰 Today's Market Rates</div>
        <div class="gold-grid">
            <div><div style="font-size:22px;color:#92400e">22K Gold (1g)</div><div class="gold-val">₹{d['metals']['gold22']}</div></div>
            <div><div style="font-size:22px;color:#92400e">Silver (1g)</div><div class="gold-val" style="color:#475569">₹{d['metals']['silver']}</div></div>
        </div></div>"""

    c = f"""<div class="bento">
        <div class="box box-large"><div class="t">Hindu Calendar</div>
            <div style="font-size:32px;font-weight:600;color:#b45309;margin-bottom:15px">📅 {p.get('tamil_date')} &nbsp;|&nbsp; 🌙 {p.get('nakshatra')}</div>
            {"".join(f'<div class="row" style="font-size:26px"><span class="i">{i.split(" ")[0]}</span><span>{esc(" ".join(i.split(" ")[1:]))}</span></div>' for i in p.get("special", []))}
        </div>
        <div class="box"><div class="t" style="color:#16a34a">நல்ல நேரம்</div><div style="font-size:28px;font-weight:600">{p.get('nalla')}</div></div>
        <div class="box"><div class="t" style="color:#dc2626">ராகு காலம்</div><div style="font-size:28px;font-weight:600">{p.get('rahu')}</div></div>
        {gold_html}
        <div class="box box-large"><div class="t">Daily Guidance</div>{adv}</div>
    </div>"""
    return layout("Daily Guide", d, c, d.get("theme", "default"))

def card_events(d):
    tdy = "".join(f'<div class="row"><span class="i">{i["icon"]}</span><span style="font-weight:600">{esc(i["text"])}</span></div>' for i in d["today"]) or '<div class="val-sub" style="font-size:26px">No events today.</div>'
    up = "".join(f'<div class="row"><span class="i">{i["icon"]}</span><span>{esc(i["text"])} <span style="font-size:22px;color:#64748b;margin-left:10px">({i["when"]})</span></span></div>' for i in d["upcoming"]) or '<div class="val-sub" style="font-size:26px">No upcoming events.</div>'
    
    bg = "background:#14532d;border-color:#166534" if d.get("night") else "background:#f0fdf4;border-color:#bbf7d0"
    tc = "#4ade80" if d.get("night") else "#166534"
    c = f"""<div class="bento">
        <div class="box box-large" style="{bg}"><div class="t" style="color:{tc}">Happening Today</div>{tdy}</div>
        <div class="box box-large"><div class="t">Upcoming in 30 Days</div>{up}</div>
    </div>"""
    return layout("Family Calendar", d, c, d.get("theme", "default"))

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
    *{box-sizing:border-box;margin:0;padding:0;font-family:'Outfit',sans-serif}
    .rain-bg {{ background: radial-gradient(circle at 50% -20%, #1e293b 0%, #020617 100%); padding: 60px; min-height: 100vh; display: flex; flex-direction: column; width: 800px; }}
    .badge {{ display: inline-flex; align-items: center; gap: 12px; background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; padding: 12px 24px; border-radius: 50px; font-size: 24px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin: 0 auto; }}
    .city {{ font-size: 64px; font-weight: 600; color: #fff; text-align: center; margin: 40px 0 10px; letter-spacing: -1px; }}
    .ta-city {{ font-size: 28px; color: #94a3b8; text-align: center; margin-bottom: 50px; }}
    .bento {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 30px; }}
    .box {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 32px; padding: 40px 30px; text-align: center; }}
    .lbl {{ font-size: 24px; color: #94a3b8; margin-bottom: 16px; font-weight: 400; }}
    .val {{ font-size: 54px; color: #38bdf8; font-weight: 600; line-height: 1; }}
    .msg-box {{ background: linear-gradient(90deg, rgba(56,189,248,0.1) 0%, rgba(56,189,248,0) 100%); border-left: 6px solid #38bdf8; padding: 40px; border-radius: 12px 32px 32px 12px; }}
    .en-msg {{ font-size: 32px; font-weight: 500; color: #f8fafc; line-height: 1.4; margin-bottom: 16px; }}
    .ta-msg {{ font-size: 28px; color: #cbd5e1; line-height: 1.5; }}
    .foot {{ text-align: center; color: #475569; font-size: 22px; margin-top: auto; padding-top: 40px; }}
    </style></head><body><div class="rain-bg">
    <div style="text-align:center; font-size: 140px; margin-bottom: 25px; line-height: 1;">⛈️</div>
    <div style="text-align:center"><div class="badge">Sudden Rain Alert</div></div>
    <div class="city">{esc(d['city'])}</div>
    <div class="ta-city">திடீர் மழை எச்சரிக்கை</div>
    
    <div class="bento">
        <div class="box"><div class="lbl">Expected Start</div><div class="val">{start}</div></div>
        <div class="box"><div class="lbl">Probability</div><div class="val">{chance}%</div></div>
    </div>
    
    <div class="msg-box">
        <div class="en-msg">{en_msg}</div>
        <div class="ta-msg">{ta_msg}</div>
    </div>
    
    <div class="foot">System Update: {fmt(d['now'])}</div>
    </div></body></html>"""

def build_birthday_html(name, age):
    age_line = f"Turns {age} today" if age else "Many happy returns"
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}"><style>
    *{{box-sizing:border-box;margin:0;padding:0;font-family:'Outfit',sans-serif}}
    body{{width:800px}}
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
