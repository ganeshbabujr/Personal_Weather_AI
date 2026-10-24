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
