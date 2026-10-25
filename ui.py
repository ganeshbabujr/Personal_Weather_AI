import html

esc = html.escape
FONT = "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap"
BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0;font-family:'Outfit',sans-serif}
body{width:800px;background:#F9FAFB;color:#0F172A}
.card{background:#fff;border-radius:40px;margin:20px;overflow:hidden;box-shadow:0 15px 35px rgba(0,0,0,0.05);display:flex;flex-direction:column}
.head{color:#fff;padding:40px 45px;background:linear-gradient(135deg,#50657c,#7b8f9f)}
.title{font-size:36px;font-weight:600;opacity:0.95;letter-spacing:-0.5px}
.date{font-size:24px;font-weight:400;margin-top:5px;opacity:0.9}
.sec{padding:35px 45px}
.t{font-size:26px;font-weight:600;color:#1E293B;margin-bottom:20px}
.row{display:flex;align-items:center;gap:20px;font-size:26px;padding:15px 0;border-bottom:1px solid rgba(0,0,0,0.05)}
.row:last-child{border-bottom:none}
.i{font-size:36px;width:45px;text-align:center}
"""

def template(title, d, content, extra_css=""):
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}">
    <style>{BASE_CSS}{extra_css}</style></head>
    <body><div class="card">
    <div class="head"><div class="title">{title}</div><div class="date">{d["now"].strftime('%A, %d %b %Y')}</div></div>
    {content}</div></body></html>"""

def card_weather(d):
    # Dynamic Icon Logic
    if d.get("rain") and d["rain"]["chance"] >= 20:
        big_icon = "🌧️"
    elif d["main"] == "Clear":
        big_icon = "🌙" if d.get("night") else "☀️"
    else:
        big_icon = "☁️"
        
    wcol = "#dc2626" if d["wind"] >= 60 else "#d97706" if d["wind"] >= 40 else "#0F172A"
    wnote = "Dangerous" if d["wind"] >= 60 else "Strong" if d["wind"] >= 40 else "Calm to breezy"
    aqi_name = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very poor"}.get(d["aqi"], "Unknown")
    acol = {1: "#16a34a", 2: "#65a30d", 3: "#d97706", 4: "#ea580c", 5: "#9333ea"}.get(d["aqi"], "#0F172A")
    if d["uv"] is None:
        uv_v, uv_d, ucol = "0", "Low", "#0F172A"
    else:
        uv_v = f"{d['uv']:.0f}"
        uv_d = "Very high" if d["uv"] >= 8 else "High" if d["uv"] >= 6 else "Moderate" if d["uv"] >= 3 else "Low"
        ucol = "#dc2626" if d["uv"] >= 8 else "#ea580c" if d["uv"] >= 6 else "#0F172A"

    rain_v = "Now" if d["rain"] and d["rain"]["now"] else (f"{d['rain']['start']%12 or 12}:00 {'AM' if d['rain']['start']<12 else 'PM'}" if d["rain"] else "Dry")
    rain_d = f"{d['rain']['chance']}% chance" if d["rain"] else "No rain today"

    css = """
    .w-top{background:linear-gradient(135deg,#50657c,#7b8f9f);color:#fff;padding:0 45px 45px;display:flex;justify-content:space-between;align-items:center}
    .grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;padding:35px 45px}
    .box{background:#F8FAFC;border-radius:24px;padding:25px;box-shadow:0 2px 10px rgba(0,0,0,0.02)}
    .lbl{font-size:22px;color:#64748b;display:flex;align-items:center;gap:8px}
    .val{font-size:42px;font-weight:700;margin-top:10px;line-height:1}
    .sub{font-size:22px;color:#64748b;margin-top:8px}
    .bars{display:flex;align-items:flex-end;gap:8px;height:120px;margin-top:20px}
    .bar-col{flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center}
    .b-fill{width:100%;border-radius:6px 6px 4px 4px;min-height:8px}
    """
    
    top = f"""<div class="w-top">
        <div><div style="font-size:160px;font-weight:400;line-height:1;letter-spacing:-6px">{d['temp']:.0f}°</div>
        <div style="font-size:36px;font-weight:600;margin-top:15px">{d['cond']}</div>
        <div style="font-size:26px;margin-top:5px;opacity:0.9">Feels {d['feels']:.0f}°, high {d['t_max']:.0f}°, low {d['t_min']:.0f}°</div></div>
        <div style="font-size:180px;text-shadow:0 10px 30px rgba(0,0,0,0.1)">{big_icon}</div>
    </div>"""

    mid = f"""<div class="grid">
        <div class="box"><div class="lbl">🌧️ Rain</div><div class="val" style="color:#0284c7">{rain_v}</div><div class="sub">{rain_d}</div></div>
        <div class="box"><div class="lbl">💨 Wind</div><div class="val" style="color:{wcol}">{d['wind']:.0f}</div><div class="sub">km/h, {wnote}</div></div>
        <div class="box"><div class="lbl">🫁 Air</div><div class="val" style="color:{acol}">{aqi_name}</div><div class="sub">AQI {d['aqi']}, PM2.5 {d['pm25']:.0f}</div></div>
        <div class="box"><div class="lbl">🧴 UV peak</div><div class="val" style="color:{ucol}">{uv_v}</div><div class="sub">{uv_d}</div></div>
    </div>"""
    
    def short_h(h): return f"{h%12 or 12}{'A' if h<12 else 'P'}"
    bars = ""
    for h in range(6, 22):
        if h in d["hourly"]:
            p = d["hourly"][h]["pop"]
            color = "#3b82f6" if p >= 50 else "#93c5fd" if p >= 20 else "#e2e8f0"
            lab = short_h(h) if h % 3 == 0 else ""
            bars += f'<div class="bar-col"><div class="b-fill" style="height:{max(8, p*1.2):.0f}px;background:{color}"></div><div style="font-size:18px;color:#64748b;margin-top:8px;height:20px">{lab}</div></div>'
            
    call = f"High chance of rain now, {d['rain']['chance']}% chance" if d["rain"] and d["rain"]["now"] else ("Expected around " + f"{d['rain']['start']%12 or 12}:00 {'AM' if d['rain']['start']<12 else 'PM'}" if d["rain"] else "Dry through the day")
    bot = f'<div class="sec" style="padding-top:0"><div class="t">Rain chance by hour</div><div class="bars">{bars}</div><div style="font-size:26px;font-weight:600;margin-top:20px;color:#1e293b">{call}</div></div>'

    return template(f"{d['city']} Weather", d, top + mid + bot, css)

def card_advice(d):
    p = d.get("panchangam", {})
    adv = "".join(f'<div class="row"><span class="i">{i}</span><span>{esc(t)}</span></div>' for i, t in d["advice"])
    
    css = """
    .panch{background:#FFF9E6;padding:35px 45px}
    .pt{font-size:26px;font-weight:600;color:#92400e;margin-bottom:15px}
    .p-date{font-size:28px;font-weight:600;color:#b45309;margin-bottom:15px;display:flex;align-items:center;gap:10px}
    .grid4{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:25px}
    .pbox{background:#fff;border-radius:16px;padding:20px;box-shadow:0 4px 12px rgba(0,0,0,0.03)}
    .plbl{font-size:22px;color:#92400e;margin-bottom:8px}
    .pval{font-size:26px;font-weight:600;color:#1e293b}
    .sun{background:#f8fafc;padding:25px 45px;display:flex;justify-content:space-around;font-size:26px;border-bottom:1px solid #f1f5f9}
    """

    sp = "".join(f'<div style="font-size:26px;margin:10px 0;display:flex;align-items:center;gap:15px"><span style="font-size:32px">{i.split(" ")[0]}</span><span>{esc(" ".join(i.split(" ")[1:]))}</span></div>' for i in p.get("special", []))
    
    panch = f"""<div class="panch">
        <div class="pt">Hindu Calendar & Timings</div>
        <div class="p-date"><span>📅</span> {p.get('tamil_date')} &nbsp;|&nbsp; <span>🌙</span> {p.get('nakshatra')}</div>
        {sp}
        <div class="grid4">
            <div class="pbox"><div class="plbl">நல்ல நேரம்</div><div class="pval">{p.get('nalla')}</div></div>
            <div class="pbox"><div class="plbl">ராகு காலம்</div><div class="pval">{p.get('rahu')}</div></div>
            <div class="pbox"><div class="plbl">எமகண்டம்</div><div class="pval">{p.get('yama')}</div></div>
            <div class="pbox"><div class="plbl">குளிகை</div><div class="pval">{p.get('kuli')}</div></div>
        </div>
    </div>
    <div class="sun"><span>🌅 Sunrise {d['sunrise'].strftime('%I:%M %p').lstrip('0')}</span><span>🌇 Sunset {d['sunset'].strftime('%I:%M %p').lstrip('0')}</span></div>
    <div class="sec"><div class="t">Weather Advice</div>{adv}</div>"""
    
    return template("Daily Guide & Advice", d, panch, css)

def card_events(d):
    tdy = "".join(f'<div class="row"><span class="i">{i["icon"]}</span><span style="font-weight:700">{esc(i["text"])}</span></div>' for i in d["today"])
    if not tdy: tdy = '<div style="font-size:26px;color:#64748b;padding:15px 0">No events today.</div>'
    
    up = ""
    for i in d["upcoming"]:
        cd_text = "Tomorrow" if i['days_left'] == 1 else f"in {i['days_left']} days"
        badge = f'<div style="background:#f1f5f9;color:#475569;padding:6px 16px;border-radius:20px;font-size:22px;margin-left:auto;white-space:nowrap">{cd_text}</div>'
        sub = f'<div style="font-size:22px;color:#64748b;margin-top:4px;font-weight:400">{i.get("date_str", "")}</div>'
        up += f'<div class="row"><span class="i">{i["icon"]}</span><div><div style="font-weight:500">{esc(i["text"])}</div>{sub}</div>{badge}</div>'
    
    if not up: up = '<div style="font-size:26px;color:#64748b;padding:15px 0">No upcoming events.</div>'

    css = """
    .green-bg{background:#F4FAF5;padding:35px 45px}
    """
    c = f"""
    <div class="green-bg">
        <div class="t" style="color:#166534">Happening Today</div>
        {tdy}
    </div>
    <div class="sec">
        <div class="t">Upcoming Events & Bills</div>
        {up}
    </div>"""
    
    return template("Family Calendar", d, c, css)

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
    *{{box-sizing:border-box;margin:0;padding:0;font-family:'Outfit',sans-serif}}
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
    </style></head><body><div class="rain-bg">
    
    <div style="text-align:center; font-size: 160px; margin-bottom: 10px; line-height: 1; filter: drop-shadow(0 15px 25px rgba(0,0,0,0.6));">⛈️</div>
    <div class="alert-title">SUDDEN RAIN ALERT</div>
    <div class="alert-sub">திடீர் மழை எச்சரிக்கை</div>
    
    <div class="city">{esc(d['city'])}</div>
    
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
    age_line = f"Turns {age} today!" if age else "Wishing you a wonderful year ahead!"
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}">
    <style>
    *{{box-sizing:border-box;margin:0;padding:0;font-family:'Outfit',sans-serif}}
    body{{width:800px;background:#F9FAFB;padding:40px}}
    .b-card{{background:linear-gradient(135deg,#FF9A9E 0%,#FECFEF 100%);border-radius:50px;padding:80px 40px;text-align:center;box-shadow:0 20px 50px rgba(255,154,158,0.3);position:relative;overflow:hidden}}
    .icon{{font-size:160px;margin-bottom:20px;filter:drop-shadow(0 10px 20px rgba(0,0,0,0.15));position:relative;z-index:2}}
    .hbd{{font-size:55px;font-weight:700;color:#9d0a3d;letter-spacing:2px;text-transform:uppercase;margin-bottom:15px;position:relative;z-index:2}}
    .name{{font-size:85px;font-weight:800;color:#1e293b;line-height:1.1;margin-bottom:35px;position:relative;z-index:2}}
    .age-pill{{background:rgba(255,255,255,0.7);color:#9d0a3d;font-size:32px;font-weight:600;padding:15px 40px;border-radius:50px;display:inline-block;box-shadow:0 8px 20px rgba(0,0,0,0.05);position:relative;z-index:2}}
    .bg-shape1{{position:absolute;top:-50px;left:-50px;width:300px;height:300px;background:rgba(255,255,255,0.2);border-radius:50%;z-index:1}}
    .bg-shape2{{position:absolute;bottom:-100px;right:-50px;width:400px;height:400px;background:rgba(255,255,255,0.15);border-radius:50%;z-index:1}}
    </style></head><body>
    <div class="b-card">
        <div class="bg-shape1"></div>
        <div class="bg-shape2"></div>
        <div class="icon">🎂</div>
        <div class="hbd">Happy Birthday</div>
        <div class="name">{esc(name)}</div>
        <div class="age-pill">{esc(age_line)}</div>
    </div>
    </body></html>"""
