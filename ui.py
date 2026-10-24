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
.bento{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}
.box{background:#fff;border-radius:32px;padding:30px;box-shadow:0 10px 30px rgba(0,0,0,0.03);border:1px solid rgba(255,255,255,0.5)}
.box-large{grid-column:span 2}
.t{font-size:24px;font-weight:600;color:#475569;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px}
.row{display:flex;align-items:center;gap:20px;font-size:28px;padding:12px 0;border-bottom:1px solid rgba(0,0,0,0.05)}
.row:last-child{border-bottom:none}
.i{font-size:38px;width:50px;text-align:center}
.v{font-size:48px;font-weight:700;line-height:1.1}
.val-sub{font-size:22px;color:#64748b;margin-top:5px}
.gold-grid{display:grid;grid-template-columns:1fr 1fr;gap:15px;text-align:center;margin-top:10px}
.gold-val{font-size:32px;font-weight:700;color:#b45309}
"""

def layout(title, d, content, theme="default"):
    if d.get("night") and theme == "default": theme = "night"
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}"><style>{CSS}</style></head>
    <body><div class="card theme-{theme}">
    <div class="head"><div><div class="title">{title}</div><div class="date">{d["now"].strftime('%A, %d %b %Y')}</div></div>
    <div style="font-size:60px">{"🎊" if theme=="festival" else "📱"}</div></div>
    {content}</div></body></html>"""

def card_weather(d):
    bars = "".join(f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end"><div style="width:100%;background:{"#38bdf8" if d["hourly"][h]["pop"]>=50 else "#e2e8f0"};height:{max(10, d["hourly"][h]["pop"])}px;border-radius:10px"></div><div style="margin-top:10px;font-size:18px">{h%12 or 12}</div></div>' for h in range(6,22,2) if h in d["hourly"])
    
    c = f"""
    <div class="bento">
        <div class="box box-large" style="display:flex;justify-content:space-between;align-items:center;background:linear-gradient(135deg,#38bdf8,#0284c7);color:#fff">
            <div><div style="font-size:120px;font-weight:700;line-height:1">{d['temp']:.0f}°</div><div style="font-size:32px;margin-top:10px">{d['cond']}</div></div>
            <div style="text-align:right"><div style="font-size:100px">{d['icon']}</div><div style="font-size:24px;opacity:0.9">H:{d['t_max']:.0f}° L:{d['t_min']:.0f}°</div></div>
        </div>
        <div class="box"><div class="t">🌧️ Rain</div><div class="v">{d['rain']['chance'] if d['rain'] else 0}%</div><div class="val-sub">{"Starting "+str(d['rain']['start'])+":00" if d['rain'] else "No rain"}</div></div>
        <div class="box"><div class="t">💨 Wind</div><div class="v">{d['wind']:.0f}</div><div class="val-sub">km/h</div></div>
        <div class="box"><div class="t">🫁 AQI</div><div class="v">{d['aqi']}</div><div class="val-sub">PM2.5: {d['pm25']:.0f}</div></div>
        <div class="box"><div class="t">🧴 UV Index</div><div class="v">{d['uv'] if d['uv'] else 0}</div><div class="val-sub">Peak</div></div>
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
            <div><div style="font-size:20px;color:#92400e">22K Gold (1g)</div><div class="gold-val">₹{d['metals']['gold22']}</div></div>
            <div><div style="font-size:20px;color:#92400e">Silver (1g)</div><div class="gold-val" style="color:#475569">₹{d['metals']['silver']}</div></div>
        </div></div>"""

    c = f"""<div class="bento">
        <div class="box box-large"><div class="t">Hindu Calendar</div>
            <div style="font-size:32px;font-weight:600;color:#b45309;margin-bottom:10px">📅 {p.get('tamil_date')} &nbsp;|&nbsp; 🌙 {p.get('nakshatra')}</div>
            {"".join(f'<div class="row" style="font-size:24px"><span class="i">{i.split(" ")[0]}</span><span>{esc(" ".join(i.split(" ")[1:]))}</span></div>' for i in p.get("special", []))}
        </div>
        <div class="box"><div class="t">நல்ல நேரம்</div><div style="font-size:26px;font-weight:600">{p.get('nalla')}</div></div>
        <div class="box"><div class="t">ராகு காலம்</div><div style="font-size:26px;font-weight:600">{p.get('rahu')}</div></div>
        {gold_html}
        <div class="box box-large"><div class="t">Daily Guidance</div>{adv}</div>
    </div>"""
    return layout("Daily Guide", d, c, d.get("theme", "default"))

def card_events(d):
    tdy = "".join(f'<div class="row"><span class="i">{i["icon"]}</span><span style="font-weight:600">{esc(i["text"])}</span></div>' for i in d["today"]) or '<div class="val-sub">No events today.</div>'
    up = "".join(f'<div class="row"><span class="i">{i["icon"]}</span><span>{esc(i["text"])} <span style="font-size:20px;color:#64748b">({i["when"]})</span></span></div>' for i in d["upcoming"]) or '<div class="val-sub">No upcoming events.</div>'
    
    c = f"""<div class="bento">
        <div class="box box-large" style="background:#f0fdf4;border-color:#bbf7d0"><div class="t" style="color:#166534">Today</div>{tdy}</div>
        <div class="box box-large"><div class="t">Upcoming in 30 Days</div>{up}</div>
    </div>"""
    return layout("Family Calendar", d, c, d.get("theme", "default"))
