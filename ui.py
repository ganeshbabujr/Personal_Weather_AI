"""Card designs for the family briefing. Built to be read inside a WhatsApp chat.

Design rules used everywhere:
- 400px wide, rendered at 3x -> sharp even after WhatsApp compresses it
- smallest text is 13px (about 9pt on a phone), key facts are 17-22px
- the top ~400px of every card carries the headline facts, because chat
  previews crop tall images
- fully rectangular, opaque background (no transparent corners -> no black
  corners after Telegram/WhatsApp flatten the PNG)
"""
import html, re
from datetime import timedelta

esc = html.escape
FONT = "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Noto+Sans+Tamil:wght@500;700&display=swap"

TAMIL_MONTHS = {"Chithirai": "சித்திரை", "Vaikasi": "வைகாசி", "Aani": "ஆனி", "Aadi": "ஆடி", "Avani": "ஆவணி",
                "Purattasi": "புரட்டாசி", "Aippasi": "ஐப்பசி", "Karthigai": "கார்த்திகை", "Margazhi": "மார்கழி",
                "Thai": "தை", "Masi": "மாசி", "Panguni": "பங்குனி"}
DAYS_TA = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"]

CSS = """
:root { --ink:#17202e; --sub:#566376; --line:#e4e9f0; --sheet:#f2f5f9; --paper:#ffffff; }
* { box-sizing:border-box; margin:0; padding:0; }
body { background:#f2f5f9; color:var(--ink); -webkit-font-smoothing:antialiased;
       font-family:'Plus Jakarta Sans','Noto Sans Tamil','Noto Sans',sans-serif; }
.card { width:400px; background:var(--sheet); overflow:hidden; line-height:1.3; }
.ta { font-family:'Noto Sans Tamil','Plus Jakarta Sans',sans-serif; line-height:1.5; }

/* ---------- hero (weather) ---------- */
.hero { position:relative; padding:20px 20px 52px; color:#fff;
        background:linear-gradient(160deg,var(--g1),var(--g2)); }
.hero:after { content:""; position:absolute; right:-70px; top:-90px; width:260px; height:260px; border-radius:50%;
              background:radial-gradient(circle,#ffffff2e,#ffffff00 68%); }
.hero-top { display:flex; justify-content:space-between; align-items:center; font-size:15px; font-weight:700; position:relative; z-index:1; }
.hero-top .date { font-weight:600; opacity:.9; }
.hero-main { display:flex; align-items:center; justify-content:space-between; margin-top:10px; position:relative; z-index:1; }
.temp { font-size:104px; font-weight:800; letter-spacing:-.05em; line-height:1; }
.temp sup { font-size:.42em; vertical-align:top; position:relative; top:.22em; margin-left:2px; font-weight:700; }
.hero-emoji { font-size:98px; line-height:1; filter:drop-shadow(0 10px 14px #0003); }
.cond { margin-top:6px; font-size:24px; font-weight:800; position:relative; z-index:1; }
.feels { margin-top:4px; font-size:16px; font-weight:600; opacity:.92; position:relative; z-index:1; }
.verdict { margin-top:16px; padding:13px 15px; border-radius:16px; background:#ffffff2b; border:1px solid #ffffff40;
           font-size:17px; font-weight:700; line-height:1.35; position:relative; z-index:1; }

.sheet { position:relative; margin-top:-28px; background:var(--sheet); border-radius:28px 28px 0 0; padding:16px 16px 18px; }

/* ---------- stat tiles ---------- */
.stats { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
.stat { background:var(--paper); border-radius:16px; padding:12px 12px 11px; }
.stat .lbl { font-size:13px; font-weight:600; color:var(--sub); }
.stat .val { margin-top:5px; font-size:20px; font-weight:800; letter-spacing:-.01em; white-space:nowrap; }
.stat .note { margin-top:4px; font-size:13px; font-weight:700; display:flex; align-items:center; gap:5px; white-space:nowrap; }
.dot { width:9px; height:9px; border-radius:50%; background:var(--c,#999); flex:none; }

/* ---------- banners ---------- */
.banner { margin-top:10px; display:flex; align-items:center; justify-content:space-between; gap:10px; padding:15px 16px; border-radius:18px; color:#fff; }
.banner.rain { background:linear-gradient(110deg,#1e4fd8,#3b8cf5); }
.banner.dry  { background:linear-gradient(110deg,#168a5a,#37b57f); }
.banner .t1 { font-size:13px; font-weight:700; opacity:.9; }
.banner .t2 { margin-top:3px; font-size:21px; font-weight:800; white-space:nowrap; }
.banner .pct { text-align:center; background:#ffffff29; border-radius:14px; padding:8px 13px; }
.banner .pct b { display:block; font-size:24px; font-weight:800; line-height:1.1; }
.banner .pct span { font-size:12px; font-weight:700; opacity:.9; }

/* ---------- panels ---------- */
.panel { margin-top:10px; background:var(--paper); border-radius:20px; padding:15px 14px; }
.ptitle { font-size:16px; font-weight:800; margin-bottom:12px; padding:0 2px; }
.hours { display:grid; grid-template-columns:repeat(6,1fr); gap:4px; text-align:center; }
.hr .h { font-size:13px; font-weight:700; color:var(--sub); }
.hr .e { font-size:27px; line-height:1.25; margin:5px 0 3px; }
.hr .tp { font-size:17px; font-weight:800; }
.hr .pp { display:inline-block; margin-top:5px; padding:2px 7px; border-radius:99px; font-size:12.5px; font-weight:800; color:#9aa6b5; }
.hr .pp.wet { color:#1b55d6; background:#e5eeff; }

.days { display:flex; flex-direction:column; }
.day { display:grid; grid-template-columns:78px 30px 44px 34px 1fr 34px; align-items:center; gap:6px; padding:9px 0; border-top:1px solid var(--line); }
.day:first-child { border-top:0; padding-top:0; }
.day .dn { font-size:15px; font-weight:800; }
.day .de { font-size:22px; text-align:center; }
.day .dp { font-size:13px; font-weight:800; color:#9aa6b5; text-align:right; }
.day .dp.wet { color:#1b55d6; }
.day .lo { font-size:15px; font-weight:700; color:var(--sub); text-align:right; }
.day .hi { font-size:15px; font-weight:800; }
.bar { position:relative; height:7px; border-radius:9px; background:#e8edf3; }
.bar i { position:absolute; top:0; bottom:0; border-radius:9px; background:linear-gradient(90deg,#4fa8f5,#f59e3b); }

/* ---------- panchangam ---------- */
.hero.pan { padding-bottom:50px; background:linear-gradient(155deg,#6d1b2e,#b4412b 60%,#e08a2e); }
.pan-day { font-size:15px; font-weight:700; opacity:.92; position:relative; z-index:1; }
.pan-date { margin-top:8px; font-size:46px; font-weight:800; line-height:1.25; position:relative; z-index:1; }
.pan-en { margin-top:2px; font-size:17px; font-weight:600; opacity:.92; position:relative; z-index:1; }
.chips { margin-top:14px; display:flex; flex-wrap:wrap; gap:8px; position:relative; z-index:1; }
.chip { padding:8px 13px; border-radius:99px; background:#ffffff2e; border:1px solid #ffffff45; font-size:15px; font-weight:700; }
.chip.hot { background:#fff; color:#8a2a1c; border-color:#fff; }

.good { display:flex; align-items:center; gap:12px; padding:15px 16px; border-radius:18px; background:#e3f6ec; }
.good .gi { font-size:28px; }
.good .g1 { font-size:13px; font-weight:700; color:#237a52; }
.good .g2 { margin-top:2px; font-size:22px; font-weight:800; color:#0f4d33; }
.avoid-row { display:grid; grid-template-columns:12px 1fr auto; gap:11px; align-items:center; padding:11px 0; border-top:1px solid var(--line); }
.avoid-row:first-of-type { border-top:0; padding-top:2px; }
.avoid-row .nm { font-size:16px; font-weight:800; }
.avoid-row .ta2 { font-size:13px; font-weight:600; color:var(--sub); }
.avoid-row .tm { font-size:17px; font-weight:800; white-space:nowrap; }

.rates { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.rate { border-radius:16px; padding:13px 14px; }
.rate.g { background:#fff3d6; } .rate.s { background:#eaeef4; }
.rate .rl { font-size:13px; font-weight:700; color:var(--sub); }
.rate .rv { margin-top:4px; font-size:24px; font-weight:800; }

.tip { display:grid; grid-template-columns:34px 1fr; gap:12px; align-items:start; padding:13px 14px; border-radius:16px; background:var(--paper); margin-top:8px; border-left:5px solid var(--c); }
.tip .ti { font-size:26px; line-height:1.1; }
.tip .tt { font-size:13px; font-weight:800; color:var(--c); }
.tip .tc { margin-top:3px; font-size:16.5px; font-weight:700; line-height:1.4; }

/* ---------- events ---------- */
.hero.ev { padding-bottom:46px; background:linear-gradient(155deg,#12365c,#1b6f8c 70%,#2aa39a); }
.ev-big { margin-top:8px; font-size:34px; font-weight:800; line-height:1.15; position:relative; z-index:1; }
.ev-sub { margin-top:4px; font-size:16px; font-weight:600; opacity:.92; position:relative; z-index:1; }
.row { display:grid; grid-template-columns:50px 1fr auto; gap:12px; align-items:center; padding:12px 0; border-top:1px solid var(--line); }
.row:first-of-type { border-top:0; padding-top:2px; }
.row:last-child { padding-bottom:2px; }
.eic { width:50px; height:50px; border-radius:15px; display:grid; place-items:center; font-size:26px; background:var(--bg,#eef2f7); }
.edate { width:50px; height:54px; border-radius:15px; text-align:center; background:var(--bg,#eef2f7); padding-top:6px; }
.edate b { display:block; font-size:21px; font-weight:800; line-height:1.1; }
.edate span { font-size:12px; font-weight:800; color:var(--sub); }
.en { font-size:17px; font-weight:800; line-height:1.3; }
.es { margin-top:2px; font-size:13px; font-weight:600; color:var(--sub); }
.pill { padding:7px 11px; border-radius:99px; font-size:13px; font-weight:800; white-space:nowrap; background:#e9eef5; color:#3d4b5e; }
.pill.today { background:#ffe9d6; color:#a4470f; }
.pill.soon { background:#e3f6ec; color:#17724b; }
.empty { padding:6px 2px 4px; font-size:16px; font-weight:600; color:var(--sub); }
.foot { padding:14px 18px 18px; font-size:13px; font-weight:600; color:#8794a6; text-align:center; }

/* ---------- alert + birthday ---------- */
.alert { background:linear-gradient(170deg,#101a33,#23325c); color:#fff; padding:26px 20px 22px; text-align:center; }
.alert .big { font-size:96px; line-height:1.1; filter:drop-shadow(0 12px 16px #0008); }
.alert h1 { margin-top:6px; font-size:34px; font-weight:800; color:#ffb4a8; }
.alert .ta-h { margin-top:2px; font-size:19px; font-weight:700; color:#cdd6ea; }
.a-stats { margin-top:20px; display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
.a-stat { background:#ffffff14; border:1px solid #ffffff22; border-radius:16px; padding:12px 6px; }
.a-stat .l { font-size:13px; font-weight:700; color:#a9b6d3; }
.a-stat .v { margin-top:5px; font-size:22px; font-weight:800; color:#7fd0ff; }
.a-msg { margin-top:14px; text-align:left; padding:16px; border-radius:16px; background:#4aa8ff24; border-left:5px solid #4aa8ff; }
.a-msg .m1 { font-size:18px; font-weight:800; line-height:1.35; }
.a-msg .m2 { margin-top:8px; font-size:16px; font-weight:600; color:#d3dcf0; }
.a-tips { margin-top:12px; display:flex; gap:8px; }
.a-tip { flex:1; padding:11px 8px; border-radius:14px; background:#ffffff14; font-size:14px; font-weight:700; }

.bday { position:relative; text-align:center; color:#fff; padding:44px 20px 40px; min-height:520px; display:flex; flex-direction:column; justify-content:center; align-items:center;
        background:linear-gradient(150deg,#6a1fa6,#d6336c 55%,#ff8a3d); overflow:hidden; }
.bday .cf { position:absolute; width:14px; height:14px; border-radius:4px; opacity:.85; }
.bday .cake { font-size:112px; line-height:1.1; filter:drop-shadow(0 12px 16px #0004); position:relative; }
.bday .hb { margin-top:12px; font-size:30px; font-weight:600; position:relative; }
.bday .nm { margin-top:6px; font-weight:800; line-height:1.15; position:relative; word-break:break-word; }
.bday .ag { margin-top:20px; padding:11px 22px; border-radius:99px; background:#ffffff30; border:1px solid #ffffff55; font-size:21px; font-weight:800; position:relative; }
.bday .wish { margin-top:22px; font-size:19px; font-weight:600; line-height:1.5; max-width:330px; position:relative; }
.bday .love { position:absolute; bottom:20px; left:0; right:0; font-size:15px; font-weight:600; opacity:.9; }

svg { fill:none; stroke:currentColor; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }
"""


def template(content):
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}">
    <style>{CSS}</style></head><body>{content}</body></html>"""


# ------------------------------------------------------------------ helpers
def fmt_h(h):
    h = h % 24
    return f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}"

def short_time(dt):
    return dt.strftime("%I:%M %p").lstrip("0")

def inr(n):
    s = str(int(n))
    if len(s) <= 3: return s
    head, tail = s[:-3], s[-3:]
    return re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", head) + "," + tail

def aqi_info(aqi):
    return {1: ("Good", "#22a06b"), 2: ("Fair", "#7bb82e"), 3: ("Moderate", "#e0a100"),
            4: ("Poor", "#f06a1d"), 5: ("Very poor", "#d92d2d")}.get(aqi, ("Unknown", "#8794a6"))

def uv_info(uv):
    if uv < 3: return "Low", "#22a06b"
    if uv < 6: return "Moderate", "#e0a100"
    if uv < 8: return "High", "#f06a1d"
    if uv < 11: return "Very high", "#d92d2d"
    return "Extreme", "#9b2fd1"

def wind_info(w):
    if w < 20: return "Calm", "#22a06b"
    if w < 40: return "Breezy", "#e0a100"
    if w < 60: return "Strong", "#f06a1d"
    return "Dangerous", "#d92d2d"

def hum_info(h):
    if h < 40: return "Dry", "#e0a100"
    if h < 70: return "Comfortable", "#22a06b"
    if h < 85: return "Humid", "#e0a100"
    return "Very humid", "#f06a1d"

def wmo_emoji(code):
    if code is None: return "🌤️"
    if code == 0: return "☀️"
    if code in (1, 2): return "⛅"
    if code == 3: return "☁️"
    if code in (45, 48): return "🌫️"
    if code in (51, 53, 55, 56, 57): return "🌦️"
    if code in (61, 63, 80, 81): return "🌧️"
    if code in (65, 66, 67, 82): return "🌧️"
    if code in (71, 73, 75, 77, 85, 86): return "❄️"
    if code in (95, 96, 99): return "⛈️"
    return "🌤️"

def hour_emoji(night, pop, cloud):
    if pop >= 50: return "🌧️"
    if pop >= 20: return "🌦️"
    if cloud is not None and cloud >= 70: return "☁️"
    if cloud is not None and cloud >= 35: return "☁️" if night else "⛅"
    return "🌙" if night else "☀️"

def is_night(h, d):
    return h < d["sunrise"].hour or h >= d["sunset"].hour

def theme(d):
    """(gradient start, gradient end, big emoji) for the weather hero."""
    rain = d.get("rain") and d["rain"]["chance"] >= 50
    if rain or d["main"] in ("Rain", "Drizzle", "Thunderstorm"):
        return "#27365c", "#4c6a97", "⛈️" if d["main"] == "Thunderstorm" else "🌧️"
    if d.get("night"):
        return "#10173a", "#2d3a7a", "🌙" if d["main"] == "Clear" else "☁️"
    if d["main"] == "Clear":
        if d["feels"] >= 37: return "#d9622b", "#f3a847", "☀️"
        return "#1769d6", "#52b3f4", "☀️"
    if d.get("rain"): return "#3d5a80", "#7fa3c7", "🌦️"
    return "#4d6a8c", "#8fb0cf", "⛅" if d["main"] == "Clouds" else "🌫️"

def verdict(d):
    """One plain sentence that sums up the day."""
    for lvl, t in d.get("alerts", []):
        if lvl == "red": return "⚠️", t.replace("⚠️ ", "").replace("😷 ", "")
    r = d.get("rain")
    if r:
        if r["now"]: return "☔", f"Raining now, likely till {fmt_h(r['end'])}. Take an umbrella."
        return "☔", f"Rain likely {fmt_h(r['start'])} to {fmt_h(r['end'])}. Take an umbrella."
    if d["feels"] >= 38: return "🌡️", "Very hot day. Drink plenty of water."
    if d["aqi"] >= 4: return "😷", "Air is poor today. Elders and kids stay indoors."
    return "✅", "No rain expected. Good day to dry clothes outside."

def day_label(d_date, today):
    diff = (d_date - today).days
    return "Tomorrow" if diff == 1 else d_date.strftime("%a, %d")


# ------------------------------------------------------------------ card 1: weather
def card_weather(d):
    g1, g2, big = theme(d)
    now, today = d["now"], d["now"].date()
    v_icon, v_text = verdict(d)

    aq_name, aq_c = aqi_info(d["aqi"])
    uv = d.get("uv") or 0
    uv_name, uv_c = uv_info(uv)
    w_name, w_c = wind_info(d["wind"])
    hum = d.get("humidity")
    hum_name, hum_c = hum_info(hum) if hum is not None else ("", "#999")

    def stat(lbl, val, note="", c="#999"):
        n = f'<div class="note" style="color:{c}"><span class="dot" style="--c:{c}"></span>{note}</div>' if note else ""
        return f'<div class="stat"><div class="lbl">{lbl}</div><div class="val">{val}</div>{n}</div>'

    stats = "".join([
        stat("💨 Wind", f"{d['wind']:.0f} km/h", w_name, w_c),
        stat("🫁 Air quality", aq_name, f"PM2.5 · {d['pm25']:.0f}", aq_c),
        stat("☀️ UV index", f"{uv:.0f}", uv_name, uv_c),
        stat("💧 Humidity", f"{hum}%" if hum is not None else "–", hum_name, hum_c),
        stat("🌅 Sunrise", short_time(d["sunrise"])),
        stat("🌇 Sunset", short_time(d["sunset"])),
    ])

    r = d.get("rain")
    if r:
        start = "Now" if r["now"] else fmt_h(r["start"])
        banner = (f'<div class="banner rain"><div><div class="t1">☔ Rain expected today</div>'
                  f'<div class="t2">{start} → {fmt_h(r["end"])}</div></div>'
                  f'<div class="pct"><b>{r["chance"]}%</b><span>chance</span></div></div>')
    else:
        banner = ('<div class="banner dry"><div><div class="t1">☔ Rain today</div>'
                  '<div class="t2">No rain expected</div></div><div style="font-size:40px">🧺</div></div>')

    hours = ""
    if d.get("hourly"):
        cells = ""
        for h in list(range(now.hour, 24, 3))[:6]:
            x = d["hourly"].get(h)
            if not x: continue
            pop = x["pop"]
            temp = f"{x['temp']:.0f}°" if x.get("temp") is not None else ""
            cells += (f'<div class="hr"><div class="h">{fmt_h(h)}</div>'
                      f'<div class="e">{hour_emoji(is_night(h, d), pop, x.get("cloud"))}</div>'
                      f'<div class="tp">{temp}</div>'
                      f'<span class="pp {"wet" if pop >= 20 else ""}">{pop}%</span></div>')
        if cells:
            hours = f'<div class="panel"><div class="ptitle">Next hours · rain chance</div><div class="hours">{cells}</div></div>'

    days = ""
    if d.get("daily"):
        lo = min(x["min"] for x in d["daily"]); hi = max(x["max"] for x in d["daily"])
        span = max(hi - lo, 1)
        rows = ""
        for x in d["daily"][:5]:
            left = (x["min"] - lo) / span * 100
            width = max((x["max"] - x["min"]) / span * 100, 12)
            rows += (f'<div class="day"><div class="dn">{day_label(x["date"], today)}</div>'
                     f'<div class="de">{wmo_emoji(x["code"])}</div>'
                     f'<div class="dp {"wet" if x["pop"] >= 20 else ""}">{x["pop"]}%</div>'
                     f'<div class="lo">{x["min"]:.0f}°</div>'
                     f'<div class="bar"><i style="left:{left:.0f}%;width:{width:.0f}%"></i></div>'
                     f'<div class="hi">{x["max"]:.0f}°</div></div>')
        days = f'<div class="panel"><div class="ptitle">Next 5 days</div><div class="days">{rows}</div></div>'

    return template(f"""
    <article class="card">
      <div class="hero" style="--g1:{g1};--g2:{g2}">
        <div class="hero-top"><span>📍 {esc(d['city'])}</span><span class="date">{now.strftime('%a, %d %b')} · {short_time(now)}</span></div>
        <div class="hero-main"><div class="temp">{d['temp']:.0f}<sup>°C</sup></div><div class="hero-emoji">{big}</div></div>
        <div class="cond">{esc(d['cond'])}</div>
        <div class="feels">Feels like {d['feels']:.0f}° &nbsp;·&nbsp; High {d['t_max']:.0f}° &nbsp;·&nbsp; Low {d['t_min']:.0f}°</div>
        <div class="verdict">{v_icon} {esc(v_text)}</div>
      </div>
      <div class="sheet">
        <div class="stats">{stats}</div>
        {banner}
        {hours}
        {days}
      </div>
    </article>""")


# ------------------------------------------------------------------ card 2: panchangam + advice
ADVICE_STYLE = {"☀️": ("Sun protection", "#d98a00"), "🌡️": ("Heat", "#e0531d"), "☔": ("Rain", "#1f62e0"),
                "🧺": ("Laundry", "#168a5a"), "😷": ("Air quality", "#d92d2d"), "💨": ("Wind", "#6a5acd"),
                "🧥": ("Cool weather", "#2a7fa8"), "💧": ("Humid", "#2a7fa8")}

def card_advice(d):
    p = d.get("panchangam") or {}
    now = d["now"]
    wd = now.weekday()

    hero_inner = ""
    if p.get("tamil_date"):
        month_en, day_no = p["tamil_date"].rsplit(" ", 1)
        month_ta = TAMIL_MONTHS.get(month_en, month_en)
        chips = "".join(f'<span class="chip hot ta">{esc(s)}</span>' for s in p.get("special", []))
        if p.get("nakshatra"):
            chips += f'<span class="chip ta">⭐ {esc(p["nakshatra"])}</span>'
        hero_inner = (f'<div class="pan-date ta">{month_ta} {day_no}</div>'
                      f'<div class="pan-en">{esc(month_en)} {day_no} · {now.strftime("%A")}</div>'
                      f'<div class="chips">{chips}</div>')
    hero = (f'<div class="hero pan"><div class="pan-day ta">🪷 {DAYS_TA[wd]} · {now.strftime("%d %b %Y")}</div>{hero_inner}</div>')

    timing = ""
    if p.get("nalla"):
        timing += (f'<div class="good"><div class="gi">✅</div><div><div class="g1">Nalla neram · நல்ல நேரம்</div>'
                   f'<div class="g2">{esc(p["nalla"])}</div></div></div>')
    if p.get("rahu"):
        rows = [("Rahu kalam", "ராகு காலம்", p["rahu"], "#d92d2d"), ("Yamagandam", "எமகண்டம்", p["yama"], "#e0531d"),
                ("Gulikai", "குளிகை", p["kuli"], "#7a5ad0")]
        body = "".join(f'<div class="avoid-row"><span class="dot" style="--c:{c}"></span>'
                       f'<div><div class="nm">{n}</div><div class="ta2 ta">{t}</div></div><div class="tm">{esc(tm)}</div></div>'
                       for n, t, tm, c in rows)
        timing += f'<div class="panel"><div class="ptitle">Avoid new work · தவிர்க்க வேண்டிய நேரம்</div>{body}</div>'

    rates = ""
    if d.get("metals"):
        m = d["metals"]
        rates = (f'<div class="panel"><div class="ptitle">Today’s rates · per gram</div><div class="rates">'
                 f'<div class="rate g"><div class="rl">🥇 22K gold</div><div class="rv">₹{inr(m["gold22"])}</div></div>'
                 f'<div class="rate s"><div class="rl">🥈 Silver</div><div class="rv">₹{inr(m["silver"])}</div></div>'
                 f'</div></div>')

    tips = ""
    for icon, text in d["advice"]:
        title, c = ADVICE_STYLE.get(icon, ("Note", "#566376"))
        tips += f'<div class="tip" style="--c:{c}"><div class="ti">{icon}</div><div><div class="tt">{title}</div><div class="tc">{esc(text)}</div></div></div>'

    return template(f"""
    <article class="card">
      {hero}
      <div class="sheet">
        {timing}
        {rates}
        <div class="ptitle" style="margin:16px 2px 2px">Today’s advice</div>
        {tips}
      </div>
    </article>""")


# ------------------------------------------------------------------ card 3: events
KIND_BG = {"birthday": "#ffe4ee", "anniversary": "#ffe6e0", "bill": "#fff1cc", "temple": "#ffe9d6",
           "holiday": "#dff5e8", "reminder": "#e1ecff", "event": "#e9eef5"}

def card_events(d):
    today = d["now"].date()

    def sub(i):
        k = i.get("kind", "event")
        return {"birthday": "Birthday", "anniversary": "Anniversary", "bill": "Bill due", "temple": "Temple",
                "holiday": "Holiday", "reminder": "Reminder"}.get(k, "Event")

    tdy = "".join(
        f'<div class="row"><div class="eic" style="--bg:{KIND_BG.get(i.get("kind"), "#e9eef5")}">{i["icon"]}</div>'
        f'<div><div class="en">{esc(i["text"])}</div><div class="es">{sub(i)}</div></div><span class="pill today">Today</span></div>'
        for i in d["today"])
    if not tdy: tdy = '<div class="empty">Nothing scheduled today. Enjoy the day 🌿</div>'

    up = ""
    for i in d["upcoming"]:
        day = today + timedelta(days=i["days_left"])
        n = i["days_left"]
        label = "Tomorrow" if n == 1 else f"In {n} days"
        cls = "pill soon" if n <= 3 else "pill"
        up += (f'<div class="row"><div class="edate" style="--bg:{KIND_BG.get(i.get("kind"), "#e9eef5")}"><b>{day.day}</b><span>{day.strftime("%b")}</span></div>'
               f'<div><div class="en">{i["icon"]} {esc(i["text"])}</div><div class="es">{day.strftime("%A")} · {sub(i)}</div></div>'
               f'<span class="{cls}">{label}</span></div>')
    if not up: up = '<div class="empty">No events in the next 30 days.</div>'

    return template(f"""
    <article class="card">
      <div class="hero ev">
        <div class="hero-top"><span>👨‍👩‍👧‍👦 Family calendar</span><span class="date">{today.strftime('%d %b %Y')}</span></div>
        <div class="ev-big">{today.strftime('%A')}</div>
        <div class="ev-sub">{len(d['today'])} today · {len(d['upcoming'])} coming up</div>
      </div>
      <div class="sheet">
        <div class="panel" style="margin-top:0"><div class="ptitle">Today</div>{tdy}</div>
        <div class="panel"><div class="ptitle">Coming up</div>{up}</div>
      </div>
      <div class="foot">Have a lovely day, family 💛</div>
    </article>""")


# ------------------------------------------------------------------ rain alert
def card_rain_alert(d):
    r = d["rain"]
    start = "Now" if r["now"] else fmt_h(r["start"])
    end = fmt_h(r["end"])
    en = f"Rain will continue until {end}." if r["now"] else f"Rain is expected to start around {start}."
    ta = f"{end} வரை மழை தொடர வாய்ப்புள்ளது." if r["now"] else f"{start} அளவில் மழை தொடங்கலாம்."
    return template(f"""
    <article class="card alert">
      <div class="big">⛈️</div>
      <h1>Rain alert</h1>
      <div class="ta-h ta">திடீர் மழை எச்சரிக்கை</div>
      <div class="a-stats">
        <div class="a-stat"><div class="l">Starts</div><div class="v">{start}</div></div>
        <div class="a-stat"><div class="l">Until</div><div class="v">{end}</div></div>
        <div class="a-stat"><div class="l">Chance</div><div class="v">{r['chance']}%</div></div>
      </div>
      <div class="a-msg"><div class="m1">{esc(en)}</div><div class="m2 ta">{esc(ta)}</div></div>
      <div class="a-tips"><div class="a-tip">🧺 Bring clothes in</div><div class="a-tip">☂️ Take umbrella</div><div class="a-tip">🚗 Drive slowly</div></div>
    </article>""")


# ------------------------------------------------------------------ birthday
def build_birthday_html(name, age):
    n = len(name)
    size = 64 if n <= 8 else 52 if n <= 12 else 40 if n <= 18 else 32
    age_pill = f'<div class="ag">🎈 Turns {age} today</div>' if age else ""
    wish = "Wishing you health, joy and a wonderful year ahead."
    confetti = "".join(
        f'<i class="cf" style="left:{x}%;top:{y}%;background:{c};transform:rotate({r}deg)"></i>'
        for x, y, c, r in [(8, 6, "#ffd54a", 20), (84, 8, "#7fe3ff", 50), (22, 16, "#fff", 70), (70, 20, "#ffd54a", 10),
                           (92, 34, "#fff", 40), (6, 40, "#7fe3ff", 80), (12, 74, "#ffd54a", 30), (88, 70, "#fff", 60),
                           (30, 88, "#7fe3ff", 15), (76, 90, "#ffd54a", 75)])
    return template(f"""
    <article class="card bday">
      {confetti}
      <div class="cake">🎂</div>
      <div class="hb">Happy Birthday</div>
      <div class="nm" style="font-size:{size}px">{esc(name)}</div>
      {age_pill}
      <div class="wish">{wish}</div>
      <div class="love">With love from the family 💛</div>
    </article>""")


# ------------------------------------------------------------------ plain-text captions
# Shown under each image, so the key facts can be read without opening it.
def caption_weather(d):
    now = d["now"]
    _, vtext = verdict(d)
    aq_name, _ = aqi_info(d["aqi"])
    uv_name, _ = uv_info(d.get("uv") or 0)
    r = d.get("rain")
    if r:
        rain = f"☔ Rain {'now' if r['now'] else fmt_h(r['start'])} to {fmt_h(r['end'])} ({r['chance']}% chance)"
    else:
        rain = "☔ No rain expected today"
    lines = [
        f"🌤️ {d['city']} · {now.strftime('%a, %d %b')}",
        f"🌡️ {d['temp']:.0f}°C (feels {d['feels']:.0f}°) · High {d['t_max']:.0f}° / Low {d['t_min']:.0f}°",
        f"{d['cond']}",
        rain,
        f"💨 Wind {d['wind']:.0f} km/h · 🫁 Air {aq_name} · ☀️ UV {d.get('uv') or 0:.0f} ({uv_name})",
    ]
    if d.get("humidity") is not None: lines.append(f"💧 Humidity {d['humidity']}%")
    lines.append(f"🌅 {short_time(d['sunrise'])} · 🌇 {short_time(d['sunset'])}")
    lines.append(f"\n👉 {vtext}")
    return "\n".join(lines)[:1000]

def caption_advice(d):
    p = d.get("panchangam") or {}
    lines = []
    if p.get("tamil_date"):
        m, n = p["tamil_date"].rsplit(" ", 1)
        lines.append(f"🪷 {TAMIL_MONTHS.get(m, m)} {n} ({m}) · {d['now'].strftime('%A')}")
        if p.get("special"): lines.append(" · ".join(p["special"]))
        if p.get("nakshatra"): lines.append(f"⭐ Nakshatra: {p['nakshatra']}")
    if p.get("nalla"): lines.append(f"✅ Nalla neram: {p['nalla']}")
    if p.get("rahu"):
        lines.append(f"🚫 Rahu {p['rahu']}")
        lines.append(f"🚫 Yamagandam {p['yama']}")
        lines.append(f"🚫 Gulikai {p['kuli']}")
    if d.get("metals"):
        lines.append(f"🥇 22K gold ₹{inr(d['metals']['gold22'])}/g · 🥈 Silver ₹{inr(d['metals']['silver'])}/g")
    if d["advice"]:
        lines.append("")
        lines += [f"{i} {t}" for i, t in d["advice"]]
    return "\n".join(lines)[:1000]

def caption_events(d):
    today = d["now"].date()
    lines = ["📅 Today"]
    lines += [f"{i['icon']} {i['text']}" for i in d["today"]] or ["Nothing scheduled"]
    if d["upcoming"]:
        lines.append("\n⏳ Coming up")
        for i in d["upcoming"][:6]:
            day = today + timedelta(days=i["days_left"])
            when = "tomorrow" if i["days_left"] == 1 else f"{day.strftime('%a %d %b')}"
            lines.append(f"{i['icon']} {i['text']} · {when}")
    return "\n".join(lines)[:1000]

def caption_rain(d):
    r = d["rain"]
    when = "now" if r["now"] else f"around {fmt_h(r['start'])}"
    return (f"⛈️ Rain alert · {d['city']}\n"
            f"Rain {when}, until {fmt_h(r['end'])} ({r['chance']}% chance)\n"
            f"🧺 Bring clothes in · ☂️ Take an umbrella\n"
            f"மழை வருகிறது, குடை எடுத்துச் செல்லுங்கள்.")
