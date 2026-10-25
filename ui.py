"""Card designs for the family briefing, built to be read inside a WhatsApp chat.

Settings (environment variables, all optional):
  BRIEF_LANG  en (default) | ta      -> Tamil becomes the main language of every card
  BIG_TEXT    1                      -> about 15% larger text, for elders

Design rules:
- 400px wide, rendered at 3x, so it stays sharp after WhatsApp compresses it
- smallest text is 13px, key facts are 17-24px
- the top of every card carries the headline facts, because chat previews crop tall images
- fully rectangular with an opaque background (no black corners after flattening)
"""
import html, os, re, base64, mimetypes
from datetime import timedelta
from pathlib import Path

esc = html.escape
TA = (os.environ.get("BRIEF_LANG") or "en").strip().lower().startswith("ta")
BIG = (os.environ.get("BIG_TEXT") or "").strip().lower() in ("1", "true", "yes", "on")

def L(en, ta):
    """Pick the English or Tamil text."""
    return ta if TA else en

FONT = "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Noto+Sans+Tamil:wght@500;700&display=swap"

TAMIL_MONTHS = {"Chithirai": "சித்திரை", "Vaikasi": "வைகாசி", "Aani": "ஆனி", "Aadi": "ஆடி", "Avani": "ஆவணி",
                "Purattasi": "புரட்டாசி", "Aippasi": "ஐப்பசி", "Karthigai": "கார்த்திகை", "Margazhi": "மார்கழி",
                "Thai": "தை", "Masi": "மாசி", "Panguni": "பங்குனி"}
DAYS_TA = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"]
COND_TA = {"Clear": "தெளிவான வானம்", "Clouds": "மேகமூட்டம்", "Rain": "மழை", "Drizzle": "தூறல்",
           "Thunderstorm": "இடியுடன் மழை", "Mist": "மூடுபனி", "Haze": "புகைமூட்டம்", "Fog": "பனிமூட்டம்",
           "Smoke": "புகைமூட்டம்", "Dust": "புழுதி"}

CSS = """
:root { --ink:#17202e; --sub:#566376; --line:#e4e9f0; --sheet:#f2f5f9; --paper:#ffffff; }
* { box-sizing:border-box; margin:0; padding:0; }
body { background:#f2f5f9; color:var(--ink); -webkit-font-smoothing:antialiased;
       font-family:'Plus Jakarta Sans','Noto Sans Tamil','Noto Sans',sans-serif; }
.card { width:400px; background:var(--sheet); overflow:hidden; line-height:1.3; }
.ta { font-family:'Noto Sans Tamil','Plus Jakarta Sans',sans-serif; line-height:1.5; }

/* ---------- hero ---------- */
.hero { position:relative; padding:16px 18px 42px; color:#fff; background:linear-gradient(160deg,var(--g1),var(--g2)); }
.hero:after { content:""; position:absolute; right:-70px; top:-90px; width:260px; height:260px; border-radius:50%;
              background:radial-gradient(circle,#ffffff2e,#ffffff00 68%); }
.hero > * { position:relative; z-index:1; }
.hero-top { display:flex; justify-content:space-between; align-items:center; gap:8px; font-size:15px; font-weight:700; }
.hero-top .date { font-weight:600; opacity:.92; white-space:nowrap; }
.hero-main { display:flex; align-items:center; justify-content:space-between; margin-top:6px; }
.temp { font-size:88px; font-weight:800; letter-spacing:-.05em; line-height:1.05; }
.temp sup { font-size:.4em; vertical-align:top; position:relative; top:.25em; margin-left:2px; font-weight:700; }
.hero-emoji { font-size:80px; line-height:1; filter:drop-shadow(0 10px 14px #0003); }
.cond { margin-top:2px; font-size:22px; font-weight:800; }
.feels { margin-top:3px; font-size:15px; font-weight:600; opacity:.94; }
.fest { margin-top:10px; display:inline-block; padding:7px 13px; border-radius:99px; background:#ffffff33; border:1px solid #ffffff55; font-size:15px; font-weight:800; }
.verdict { margin-top:12px; padding:11px 13px; border-radius:15px; background:#ffffff2b; border:1px solid #ffffff40; font-size:16.5px; font-weight:700; line-height:1.35; }

.sheet { position:relative; margin-top:-26px; background:var(--sheet); border-radius:26px 26px 0 0; padding:14px 14px 16px; }

/* ---------- stat tiles ---------- */
.stats { display:grid; grid-template-columns:repeat(3,1fr); gap:7px; }
.stat { background:var(--paper); border-radius:15px; padding:10px 10px 9px; }
.stat .lbl { font-size:13px; font-weight:600; color:var(--sub); white-space:nowrap; }
.stat .val { margin-top:3px; font-size:19px; font-weight:800; letter-spacing:-.01em; white-space:nowrap; }
.stat .note { margin-top:3px; font-size:13px; font-weight:700; display:flex; align-items:center; gap:5px; white-space:nowrap; }
.dot { width:9px; height:9px; border-radius:50%; background:var(--c,#999); flex:none; }

/* ---------- banners ---------- */
.banner { margin-top:8px; display:flex; align-items:center; justify-content:space-between; gap:10px; padding:12px 14px; border-radius:17px; color:#fff; }
.banner.rain { background:linear-gradient(110deg,#1e4fd8,#3b8cf5); }
.banner.dry  { background:linear-gradient(110deg,#168a5a,#37b57f); }
.banner .t1 { font-size:13px; font-weight:700; opacity:.92; }
.banner .t2 { margin-top:2px; font-size:20px; font-weight:800; white-space:nowrap; }
.banner .pct { text-align:center; background:#ffffff29; border-radius:13px; padding:6px 12px; }
.banner .pct b { display:block; font-size:22px; font-weight:800; line-height:1.1; }
.banner .pct span { font-size:12px; font-weight:700; opacity:.92; }

/* ---------- panels ---------- */
.panel { margin-top:8px; background:var(--paper); border-radius:19px; padding:13px 13px; }
.ptitle { font-size:15px; font-weight:800; margin-bottom:9px; padding:0 2px; }
.hours { display:grid; grid-template-columns:repeat(6,1fr); gap:3px; text-align:center; }
.hr .h { font-size:13px; font-weight:700; color:var(--sub); }
.hr .e { font-size:25px; line-height:1.25; margin:3px 0 2px; }
.hr .tp { font-size:16.5px; font-weight:800; }
.hr .pp { display:inline-block; margin-top:4px; padding:2px 7px; border-radius:99px; font-size:12.5px; font-weight:800; color:#9aa6b5; }
.hr .pp.wet { color:#1b55d6; background:#e5eeff; }

.places { display:grid; grid-template-columns:1fr 1fr; gap:7px; }
.pl { display:flex; align-items:center; gap:8px; padding:9px 10px; background:var(--sheet); border-radius:13px; }
.pl .pe { font-size:24px; }
.pl .pn { font-size:14px; font-weight:800; line-height:1.2; }
.pl .ps { font-size:13px; font-weight:700; color:var(--sub); }
.pl .ps b { color:var(--ink); }

.days { display:flex; flex-direction:column; }
.day { display:grid; grid-template-columns:76px 30px 42px 32px 1fr 32px; align-items:center; gap:6px; padding:9px 0; border-top:1px solid var(--line); }
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
.hero.pan { padding-bottom:46px; background:linear-gradient(155deg,var(--g1),var(--g2)); }
.pan-day { font-size:15px; font-weight:700; opacity:.94; }
.pan-date { margin-top:6px; font-size:44px; font-weight:800; line-height:1.25; }
.pan-en { margin-top:0; font-size:16px; font-weight:600; opacity:.94; }
.chips { margin-top:12px; display:flex; flex-wrap:wrap; gap:7px; }
.chip { padding:7px 12px; border-radius:99px; background:#ffffff2e; border:1px solid #ffffff45; font-size:15px; font-weight:700; }
.chip.hot { background:#fff; color:#8a2a1c; border-color:#fff; }

.good { display:flex; align-items:center; gap:12px; padding:13px 15px; border-radius:17px; background:#e3f6ec; }
.good .gi { font-size:26px; }
.good .g1 { font-size:13px; font-weight:700; color:#237a52; }
.good .g2 { margin-top:2px; font-size:21px; font-weight:800; color:#0f4d33; }
.avoid-row { display:grid; grid-template-columns:12px 1fr auto; gap:11px; align-items:center; padding:9px 0; border-top:1px solid var(--line); }
.avoid-row:first-of-type { border-top:0; padding-top:2px; }
.avoid-row .nm { font-size:16px; font-weight:800; }
.avoid-row .ta2 { font-size:13px; font-weight:600; color:var(--sub); }
.avoid-row .tm { font-size:16.5px; font-weight:800; white-space:nowrap; }

.rates { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.rate { border-radius:15px; padding:11px 13px; }
.rate.g { background:#fff3d6; } .rate.s { background:#eaeef4; }
.rate .rl { font-size:13px; font-weight:700; color:var(--sub); }
.rate .rv { margin-top:3px; font-size:23px; font-weight:800; }

.tip { display:grid; grid-template-columns:34px 1fr; gap:11px; align-items:start; padding:12px 13px; border-radius:15px; background:var(--paper); margin-top:7px; border-left:5px solid var(--c); }
.tip .ti { font-size:25px; line-height:1.1; }
.tip .tt { font-size:13px; font-weight:800; color:var(--c); }
.tip .tc { margin-top:2px; font-size:16px; font-weight:700; line-height:1.4; }

/* ---------- events ---------- */
.hero.ev { padding-bottom:42px; background:linear-gradient(155deg,var(--g1),var(--g2)); }
.ev-big { margin-top:6px; font-size:32px; font-weight:800; line-height:1.2; }
.ev-sub { margin-top:2px; font-size:16px; font-weight:600; opacity:.94; }
.row { display:grid; grid-template-columns:50px 1fr auto; gap:12px; align-items:center; padding:11px 0; border-top:1px solid var(--line); }
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
.foot { padding:12px 18px 16px; font-size:13px; font-weight:600; color:#8794a6; text-align:center; }

/* ---------- alert + birthday ---------- */
.alert { background:linear-gradient(170deg,#101a33,#23325c); color:#fff; padding:24px 20px 20px; text-align:center; }
.alert .big { font-size:88px; line-height:1.1; filter:drop-shadow(0 12px 16px #0008); }
.alert h1 { margin-top:4px; font-size:32px; font-weight:800; color:#ffb4a8; }
.alert .ta-h { margin-top:2px; font-size:18px; font-weight:700; color:#cdd6ea; }
.a-stats { margin-top:18px; display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
.a-stat { background:#ffffff14; border:1px solid #ffffff22; border-radius:16px; padding:11px 6px; }
.a-stat .l { font-size:13px; font-weight:700; color:#a9b6d3; }
.a-stat .v { margin-top:4px; font-size:22px; font-weight:800; color:#7fd0ff; }
.a-msg { margin-top:12px; text-align:left; padding:15px; border-radius:16px; background:#4aa8ff24; border-left:5px solid #4aa8ff; }
.a-msg .m1 { font-size:18px; font-weight:800; line-height:1.35; }
.a-msg .m2 { margin-top:7px; font-size:16px; font-weight:600; color:#d3dcf0; }
.a-tips { margin-top:12px; display:flex; gap:8px; }
.a-tip { flex:1; padding:10px 8px; border-radius:14px; background:#ffffff14; font-size:14px; font-weight:700; }

.bday { position:relative; text-align:center; color:#fff; padding:40px 20px 56px; min-height:520px; display:flex; flex-direction:column; justify-content:center; align-items:center;
        background:linear-gradient(150deg,#6a1fa6,#d6336c 55%,#ff8a3d); overflow:hidden; }
.bday .cf { position:absolute; width:14px; height:14px; border-radius:4px; opacity:.85; }
.bday .cake { font-size:104px; line-height:1.1; filter:drop-shadow(0 12px 16px #0004); position:relative; }
.bday .photo { width:170px; height:170px; border-radius:50%; object-fit:cover; border:6px solid #fff; box-shadow:0 12px 26px #0004; position:relative; }
.bday .badge { margin-top:-26px; font-size:44px; position:relative; }
.bday .hb { margin-top:12px; font-size:28px; font-weight:600; position:relative; }
.bday .nm { margin-top:6px; font-weight:800; line-height:1.2; position:relative; word-break:break-word; }
.bday .ag { margin-top:18px; padding:10px 22px; border-radius:99px; background:#ffffff30; border:1px solid #ffffff55; font-size:21px; font-weight:800; position:relative; }
.bday .wish { margin-top:20px; font-size:19px; font-weight:600; line-height:1.5; max-width:330px; position:relative; }
.bday .love { position:absolute; bottom:20px; left:0; right:0; font-size:15px; font-weight:600; opacity:.92; }

svg { fill:none; stroke:currentColor; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }
"""

# Bigger-text mode: the layout is squeezed to 348px and zoomed back to 400px, so text is 15% larger.
BIG_CSS = ".card { width:348px; zoom:1.15; } .bday, .alert { zoom:1.0; width:400px; } .stat .val { font-size:18px; }"


def template(content):
    extra = BIG_CSS if BIG else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONT}">
    <style>{CSS}{extra}</style></head><body>{content}</body></html>"""


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

AQI_NAMES = {1: ("Good", "நல்லது", "#22a06b"), 2: ("Moderate", "மிதமானது", "#d9a400"), 3: ("Caution", "கவனம்", "#f08a1d"),
             4: ("Poor", "மோசம்", "#e8541d"), 5: ("Very poor", "மிக மோசம்", "#d92d2d")}

def aqi_info(aqi):
    en, ta, c = AQI_NAMES.get(aqi, ("Unknown", "தெரியவில்லை", "#8794a6"))
    return L(en, ta), c

def uv_info(uv):
    if uv < 3: return L("Low", "குறைவு"), "#22a06b"
    if uv < 6: return L("Moderate", "மிதமானது"), "#d9a400"
    if uv < 8: return L("High", "அதிகம்"), "#e8731d"
    if uv < 11: return L("Very high", "மிக அதிகம்"), "#d92d2d"
    return L("Extreme", "அதீதம்"), "#9b2fd1"

def wind_info(w):
    if w < 20: return L("Calm", "அமைதி"), "#22a06b"
    if w < 40: return L("Breezy", "லேசான காற்று"), "#d9a400"
    if w < 60: return L("Strong", "பலத்த காற்று"), "#e8731d"
    return L("Dangerous", "ஆபத்து"), "#d92d2d"

def hum_info(h):
    if h < 40: return L("Dry", "வறண்டது"), "#d9a400"
    if h < 70: return L("Comfortable", "இதமானது"), "#22a06b"
    if h < 85: return L("Humid", "ஈரப்பதம்"), "#d9a400"
    return L("Very humid", "மிக ஈரப்பதம்"), "#e8731d"

def rain_level(level):
    return {"light": L("Light rain", "லேசான மழை"), "moderate": L("Moderate rain", "மிதமான மழை"),
            "heavy": L("Heavy rain", "கனமழை")}.get(level, L("Rain", "மழை"))

def wmo_emoji(code):
    if code is None: return "🌤️"
    if code == 0: return "☀️"
    if code in (1, 2): return "⛅"
    if code == 3: return "☁️"
    if code in (45, 48): return "🌫️"
    if code in (51, 53, 55, 56, 57): return "🌦️"
    if code in (61, 63, 65, 66, 67, 80, 81, 82): return "🌧️"
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

def cond_text(d):
    return COND_TA.get(d["main"], d["cond"]) if TA else d["cond"]

def day_name(day, today, short=True):
    if (day - today).days == 1: return L("Tomorrow", "நாளை")
    if TA: return f"{DAYS_TA[day.weekday()]} {day.day}"
    return day.strftime("%a, %d") if short else day.strftime("%A")

def weekday_name(day):
    return DAYS_TA[day.weekday()] if TA else day.strftime("%A")


# ---------- festivals: (keywords, gradient start, gradient end, emoji, English greeting, Tamil greeting)
FESTIVALS = [
    (("deepavali", "diwali"), "#4a1030", "#e9822a", "🪔", "Happy Deepavali!", "தீபாவளி நல்வாழ்த்துக்கள்!"),
    (("pongal",), "#1f6f3a", "#f0b429", "🌾", "Happy Pongal!", "பொங்கல் நல்வாழ்த்துக்கள்!"),
    (("tamil new year", "puthandu"), "#8a1c4a", "#f2a33a", "🌺", "Happy Tamil New Year!", "தமிழ்ப் புத்தாண்டு நல்வாழ்த்துக்கள்!"),
    (("ganesh", "vinayaka"), "#9a3412", "#f59e0b", "🐘", "Happy Vinayaka Chaturthi!", "விநாயகர் சதுர்த்தி நல்வாழ்த்துக்கள்!"),
    (("dussehra", "vijayadashami", "ayudha"), "#7c2d12", "#ea580c", "🪔", "Happy Vijayadashami!", "விஜயதசமி நல்வாழ்த்துக்கள்!"),
    (("christmas",), "#14532d", "#b91c1c", "🎄", "Merry Christmas!", "கிறிஸ்துமஸ் நல்வாழ்த்துக்கள்!"),
    (("eid",), "#064e3b", "#0d9488", "🌙", "Eid Mubarak!", "ஈத் முபாரக்!"),
    (("republic day",), "#e8731a", "#138808", "🇮🇳", "Happy Republic Day!", "குடியரசு தின வாழ்த்துக்கள்!"),
    (("independence day",), "#e8731a", "#138808", "🇮🇳", "Happy Independence Day!", "சுதந்திர தின வாழ்த்துக்கள்!"),
    (("new year",), "#1e1b4b", "#6d28d9", "🎆", "Happy New Year!", "புத்தாண்டு நல்வாழ்த்துக்கள்!"),
]

def festival(d):
    for it in d.get("today", []):
        if it.get("kind") != "holiday": continue
        name = it["text"].lower()
        for keys, g1, g2, emoji, en, ta in FESTIVALS:
            if any(k in name for k in keys):
                return {"g1": g1, "g2": g2, "emoji": emoji, "text": f"{emoji} {L(en, ta)}"}
    return None

def theme(d):
    """(gradient start, gradient end, big emoji) for the weather hero."""
    fest = festival(d)
    rain = d.get("rain") and d["rain"]["chance"] >= 50
    if rain or d["main"] in ("Rain", "Drizzle", "Thunderstorm"):
        g1, g2, e = "#27365c", "#4c6a97", "⛈️" if d["main"] == "Thunderstorm" else "🌧️"
    elif d.get("night"):
        g1, g2, e = "#10173a", "#2d3a7a", "🌙" if d["main"] == "Clear" else "☁️"
    elif d["main"] == "Clear":
        g1, g2, e = ("#d9622b", "#f3a847", "☀️") if d["feels"] >= 37 else ("#1769d6", "#52b3f4", "☀️")
    elif d.get("rain"):
        g1, g2, e = "#3d5a80", "#7fa3c7", "🌦️"
    else:
        g1, g2, e = "#4d6a8c", "#8fb0cf", "⛅" if d["main"] == "Clouds" else "🌫️"
    if fest: g1, g2 = fest["g1"], fest["g2"]
    return g1, g2, e

def verdict(d):
    """One plain sentence that sums up the day."""
    for a in d.get("alerts", []):
        if a[0] == "red": return "⚠️", L(a[1], a[2])
    r = d.get("rain")
    if r:
        if r["now"]:
            return "☔", L(f"Raining now, likely till {fmt_h(r['end'])}. Take an umbrella.",
                          f"இப்போது மழை, {fmt_h(r['end'])} வரை தொடரலாம். குடை எடுத்துச் செல்லுங்கள்.")
        return "☔", L(f"Rain likely {fmt_h(r['start'])} to {fmt_h(r['end'])}. Take an umbrella.",
                      f"{fmt_h(r['start'])} முதல் {fmt_h(r['end'])} வரை மழை வாய்ப்பு. குடை எடுத்துச் செல்லுங்கள்.")
    if d["feels"] >= 38: return "🌡️", L("Very hot day. Drink plenty of water.", "மிகவும் வெப்பமான நாள். நிறைய தண்ணீர் குடியுங்கள்.")
    if d["aqi"] >= 4: return "😷", L("Air is poor today. Elders and kids stay indoors.", "காற்றுத் தரம் மோசம். முதியவர்களும் குழந்தைகளும் வீட்டிற்குள் இருங்கள்.")
    return "✅", L("No rain expected. Good day to dry clothes outside.", "மழை இல்லை. துணிகளை வெளியே காயவைக்க நல்ல நாள்.")


# ------------------------------------------------------------------ card 1: weather (compact)
def card_weather(d):
    g1, g2, big = theme(d)
    now = d["now"]
    v_icon, v_text = verdict(d)
    fest = festival(d)

    aq_name, aq_c = aqi_info(d["aqi"])
    aq_val = f"AQI {d['aqi_val']:.0f}" if d.get("aqi_val") is not None else aq_name
    uv = d.get("uv") or 0
    uv_name, uv_c = uv_info(uv)
    w_name, w_c = wind_info(d["wind"])
    hum = d.get("humidity")
    hum_name, hum_c = hum_info(hum) if hum is not None else ("", "#999")

    def stat(lbl, val, note="", c="#999"):
        n = f'<div class="note" style="color:{c}"><span class="dot" style="--c:{c}"></span>{note}</div>' if note else ""
        return f'<div class="stat"><div class="lbl">{lbl}</div><div class="val">{val}</div>{n}</div>'

    stats = "".join([
        stat(L("💨 Wind", "💨 காற்று"), f"{d['wind']:.0f} km/h", w_name, w_c),
        stat(L("🫁 Air", "🫁 காற்றுத் தரம்"), aq_val, aq_name, aq_c),
        stat(L("☀️ UV index", "☀️ புற ஊதா"), f"{uv:.0f}", uv_name, uv_c),
        stat(L("💧 Humidity", "💧 ஈரப்பதம்"), f"{hum}%" if hum is not None else "–", hum_name, hum_c),
        stat(L("🌅 Sunrise", "🌅 உதயம்"), short_time(d["sunrise"])),
        stat(L("🌇 Sunset", "🌇 அஸ்தமனம்"), short_time(d["sunset"])),
    ])

    r = d.get("rain")
    if r:
        start = L("Now", "இப்போது") if r["now"] else fmt_h(r["start"])
        mm = f" · ~{r['mm']:.1f} mm" if r.get("mm", 0) >= 0.1 else ""
        banner = (f'<div class="banner rain"><div><div class="t1">☔ {rain_level(r.get("level"))}{mm}</div>'
                  f'<div class="t2">{start} → {fmt_h(r["end"])}</div></div>'
                  f'<div class="pct"><b>{r["chance"]}%</b><span>{L("chance", "வாய்ப்பு")}</span></div></div>')
    else:
        banner = (f'<div class="banner dry"><div><div class="t1">{L("☔ Rain today", "☔ இன்று மழை")}</div>'
                  f'<div class="t2">{L("No rain expected", "மழை இல்லை")}</div></div><div style="font-size:36px">🧺</div></div>')

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
            hours = (f'<div class="panel"><div class="ptitle">{L("Next hours · rain chance", "அடுத்த மணிநேரம் · மழை வாய்ப்பு")}</div>'
                     f'<div class="hours">{cells}</div></div>')

    places = ""
    if d.get("places"):
        cells = ""
        for p in d["places"][:4]:
            cells += (f'<div class="pl"><div class="pe">{wmo_emoji(p.get("code"))}</div><div>'
                      f'<div class="pn">{esc(p["city"])}</div>'
                      f'<div class="ps"><b>{p["temp"]:.0f}°</b> · ☔ {p["pop"]}%</div></div></div>')
        places = (f'<div class="panel"><div class="ptitle">{L("Family elsewhere today", "மற்ற ஊர்களில் இன்று")}</div>'
                  f'<div class="places">{cells}</div></div>')

    fest_html = f'<div class="fest ta">{esc(fest["text"])}</div>' if fest else ""
    date_txt = f"{DAYS_TA[now.weekday()] if TA else now.strftime('%a')}, {now.strftime('%d %b')} · {short_time(now)}"
    return template(f"""
    <article class="card">
      <div class="hero" style="--g1:{g1};--g2:{g2}">
        <div class="hero-top"><span>📍 {esc(d['city'])}</span><span class="date">{date_txt}</span></div>
        <div class="hero-main"><div class="temp">{d['temp']:.0f}<sup>°C</sup></div><div class="hero-emoji">{big}</div></div>
        <div class="cond ta">{esc(cond_text(d))}</div>
        <div class="feels">{L('Feels', 'உணர்வு')} {d['feels']:.0f}° &nbsp;·&nbsp; {L('High', 'அதிகம்')} {d['t_max']:.0f}° &nbsp;·&nbsp; {L('Low', 'குறைவு')} {d['t_min']:.0f}°</div>
        {fest_html}
        <div class="verdict ta">{v_icon} {esc(v_text)}</div>
      </div>
      <div class="sheet">
        <div class="stats">{stats}</div>
        {banner}
        {hours}
        {places}
      </div>
    </article>""")


# ------------------------------------------------------------------ card 2: panchangam + advice
ADVICE_STYLE = {"☀️": (("Sun protection", "சூரிய பாதுகாப்பு"), "#d98a00"), "🌡️": (("Heat", "வெப்பம்"), "#e0531d"),
                "☔": (("Rain", "மழை"), "#1f62e0"), "🧺": (("Laundry", "துணி காய"), "#168a5a"),
                "😷": (("Air quality", "காற்றுத் தரம்"), "#d92d2d"), "💨": (("Wind", "காற்று"), "#6a5acd"),
                "🧥": (("Cool weather", "குளிர்"), "#2a7fa8"), "💧": (("Humid", "ஈரப்பதம்"), "#2a7fa8"),
                "🎒": (("School", "பள்ளி"), "#7a4cd0"), "👵": (("For elders", "முதியவர்களுக்கு"), "#b4532a"),
                "🫁": (("Asthma care", "ஆஸ்துமா கவனம்"), "#c2410c"), "🧒": (("For kids", "குழந்தைகளுக்கு"), "#0f8f6f")}

def card_advice(d):
    p = d.get("panchangam") or {}
    now = d["now"]
    fest = festival(d)
    g1, g2 = (fest["g1"], fest["g2"]) if fest else ("#6d1b2e", "#e08a2e")

    hero_inner = ""
    if p.get("tamil_date"):
        month_en, day_no = p["tamil_date"].rsplit(" ", 1)
        month_ta = TAMIL_MONTHS.get(month_en, month_en)
        chips = "".join(f'<span class="chip hot ta">{esc(s)}</span>' for s in p.get("special", []))
        if p.get("tithi"):
            paksha = L(p.get("paksha_en", ""), p.get("paksha_ta", ""))
            chips += f'<span class="chip ta">🌓 {esc(paksha)} {esc(p["tithi"])}</span>'
        if p.get("nakshatra"):
            chips += f'<span class="chip ta">⭐ {esc(p["nakshatra"])}</span>'
        hero_inner = (f'<div class="pan-date ta">{month_ta} {day_no}</div>'
                      f'<div class="pan-en">{esc(month_en)} {day_no} · {now.strftime("%A")}</div>'
                      f'<div class="chips">{chips}</div>')
    fest_html = f'<div class="fest ta">{esc(fest["text"])}</div>' if fest else ""
    hero = (f'<div class="hero pan" style="--g1:{g1};--g2:{g2}"><div class="pan-day ta">🪷 {DAYS_TA[now.weekday()]} · {now.strftime("%d %b %Y")}</div>{hero_inner}{fest_html}</div>')

    timing = ""
    if p.get("nalla"):
        timing += (f'<div class="good"><div class="gi">✅</div><div><div class="g1 ta">Nalla neram · நல்ல நேரம்</div>'
                   f'<div class="g2">{esc(p["nalla"])}</div></div></div>')
    if p.get("rahu"):
        rows = [("Rahu kalam", "ராகு காலம்", p["rahu"], "#d92d2d"), ("Yamagandam", "எமகண்டம்", p["yama"], "#e8541d"),
                ("Gulikai", "குளிகை", p["kuli"], "#7a5ad0")]
        body = "".join(f'<div class="avoid-row"><span class="dot" style="--c:{c}"></span>'
                       f'<div><div class="nm ta">{ta if TA else n}</div><div class="ta2 ta">{n if TA else ta}</div></div><div class="tm">{esc(tm)}</div></div>'
                       for n, ta, tm, c in rows)
        timing += f'<div class="panel"><div class="ptitle ta">{L("Avoid new work", "தவிர்க்க வேண்டிய நேரம்")}</div>{body}</div>'

    rates = ""
    if d.get("metals"):
        m = d["metals"]
        rates = (f'<div class="panel"><div class="ptitle">{L("Today’s rates · per gram", "இன்றைய விலை · கிராமுக்கு")}</div><div class="rates">'
                 f'<div class="rate g"><div class="rl">🥇 {L("22K gold", "22K தங்கம்")}</div><div class="rv">₹{inr(m["gold22"])}</div></div>'
                 f'<div class="rate s"><div class="rl">🥈 {L("Silver", "வெள்ளி")}</div><div class="rv">₹{inr(m["silver"])}</div></div>'
                 f'</div></div>')

    tips = ""
    for icon, en, ta in d["advice"]:
        (t_en, t_ta), c = ADVICE_STYLE.get(icon, (("Note", "குறிப்பு"), "#566376"))
        tips += (f'<div class="tip" style="--c:{c}"><div class="ti">{icon}</div><div><div class="tt ta">{L(t_en, t_ta)}</div>'
                 f'<div class="tc ta">{esc(L(en, ta))}</div></div></div>')

    return template(f"""
    <article class="card">
      {hero}
      <div class="sheet">
        {timing}
        {rates}
        <div class="ptitle" style="margin:14px 2px 0">{L("Today’s advice", "இன்றைய குறிப்புகள்")}</div>
        {tips}
      </div>
    </article>""")


# ------------------------------------------------------------------ card 3: events
KIND_BG = {"birthday": "#ffe4ee", "anniversary": "#ffe6e0", "bill": "#fff1cc", "temple": "#ffe9d6",
           "holiday": "#dff5e8", "reminder": "#e1ecff", "event": "#e9eef5"}
KIND_LBL = {"birthday": ("Birthday", "பிறந்தநாள்"), "anniversary": ("Anniversary", "திருமண நாள்"),
            "bill": ("Bill due", "கட்டணம் செலுத்த வேண்டும்"), "temple": ("Temple", "கோவில்"),
            "holiday": ("Holiday", "விடுமுறை"), "reminder": ("Reminder", "நினைவூட்டல்"), "event": ("Event", "நிகழ்வு")}

def kind_label(i):
    en, ta = KIND_LBL.get(i.get("kind", "event"), KIND_LBL["event"])
    return L(en, ta)

def countdown(n):
    return L("Tomorrow", "நாளை") if n == 1 else L(f"In {n} days", f"{n} நாட்களில்")

def event_rows(items, today):
    out = ""
    for i in items:
        n = i["days_left"]
        day = today + timedelta(days=n)
        cls = "pill soon" if n <= 3 else "pill"
        out += (f'<div class="row"><div class="edate" style="--bg:{KIND_BG.get(i.get("kind"), "#e9eef5")}"><b>{day.day}</b><span>{day.strftime("%b")}</span></div>'
                f'<div><div class="en ta">{i["icon"]} {esc(i["text"])}</div><div class="es ta">{weekday_name(day)} · {kind_label(i)}</div></div>'
                f'<span class="{cls} ta">{countdown(n)}</span></div>')
    return out

def card_events(d):
    today = d["now"].date()
    tdy = "".join(
        f'<div class="row"><div class="eic" style="--bg:{KIND_BG.get(i.get("kind"), "#e9eef5")}">{i["icon"]}</div>'
        f'<div><div class="en ta">{esc(i["text"])}</div><div class="es ta">{kind_label(i)}</div></div><span class="pill today ta">{L("Today", "இன்று")}</span></div>'
        for i in d["today"])
    if not tdy: tdy = f'<div class="empty ta">{L("Nothing scheduled today. Enjoy the day 🌿", "இன்று நிகழ்வுகள் எதுவும் இல்லை 🌿")}</div>'
    up = event_rows(d["upcoming"], today) or f'<div class="empty ta">{L("No events in the next 30 days.", "அடுத்த 30 நாட்களில் நிகழ்வுகள் இல்லை.")}</div>'
    fest = festival(d)
    g1, g2 = (fest["g1"], fest["g2"]) if fest else ("#12365c", "#2aa39a")
    sub = L(f"{len(d['today'])} today · {len(d['upcoming'])} coming up", f"இன்று {len(d['today'])} · வரவிருப்பவை {len(d['upcoming'])}")
    return template(f"""
    <article class="card">
      <div class="hero ev" style="--g1:{g1};--g2:{g2}">
        <div class="hero-top"><span class="ta">👨‍👩‍👧‍👦 {L("Family calendar", "குடும்ப நாட்காட்டி")}</span><span class="date">{today.strftime('%d %b %Y')}</span></div>
        <div class="ev-big ta">{weekday_name(today)}</div>
        <div class="ev-sub ta">{sub}</div>
      </div>
      <div class="sheet">
        <div class="panel" style="margin-top:0"><div class="ptitle ta">{L("Today", "இன்று")}</div>{tdy}</div>
        <div class="panel"><div class="ptitle ta">{L("Coming up", "வரவிருப்பவை")}</div>{up}</div>
      </div>
      <div class="foot ta">{L("Have a lovely day, family 💛", "இனிய நாளாக அமையட்டும் 💛")}</div>
    </article>""")


# ------------------------------------------------------------------ card 4: week ahead (Sundays)
def card_week(d):
    days = (d.get("daily") or [])[:7]
    if not days: return None
    today = d["now"].date()
    lo = min(x["min"] for x in days); hi = max(x["max"] for x in days)
    span = max(hi - lo, 1)
    rows = ""
    for x in days:
        left = (x["min"] - lo) / span * 100
        width = max((x["max"] - x["min"]) / span * 100, 12)
        rows += (f'<div class="day"><div class="dn ta">{day_name(x["date"], today)}</div>'
                 f'<div class="de">{wmo_emoji(x["code"])}</div>'
                 f'<div class="dp {"wet" if x["pop"] >= 20 else ""}">{x["pop"]}%</div>'
                 f'<div class="lo">{x["min"]:.0f}°</div>'
                 f'<div class="bar"><i style="left:{left:.0f}%;width:{width:.0f}%"></i></div>'
                 f'<div class="hi">{x["max"]:.0f}°</div></div>')

    wet = max(days, key=lambda x: x["pop"]); hot = max(days, key=lambda x: x["max"]); dry = min(days, key=lambda x: x["pop"])
    chips = ""
    if wet["pop"] >= 30: chips += f'<span class="chip ta">☔ {L("Wettest", "அதிக மழை")}: {day_name(wet["date"], today)} ({wet["pop"]}%)</span>'
    chips += f'<span class="chip ta">🌡️ {L("Hottest", "அதிக வெப்பம்")}: {day_name(hot["date"], today)} {hot["max"]:.0f}°</span>'
    chips += f'<span class="chip ta">🧺 {L("Best to dry clothes", "துணி காய நல்ல நாள்")}: {day_name(dry["date"], today)}</span>'

    week_ev = [e for e in d.get("week_events", [])]
    ev_html = ""
    if week_ev:
        ev_html = (f'<div class="panel"><div class="ptitle ta">{L("This week’s events", "இந்த வார நிகழ்வுகள்")}</div>'
                   f'{event_rows(week_ev, today)}</div>')
    return template(f"""
    <article class="card">
      <div class="hero ev" style="--g1:#2d2a74;--g2:#2f7fd0">
        <div class="hero-top"><span class="ta">🗓️ {L("Week ahead", "இந்த வார முன்னோட்டம்")}</span><span class="date">{days[0]['date'].strftime('%d %b')} – {days[-1]['date'].strftime('%d %b')}</span></div>
        <div class="chips">{chips}</div>
      </div>
      <div class="sheet">
        <div class="panel" style="margin-top:0"><div class="days">{rows}</div></div>
        {ev_html}
      </div>
    </article>""")


# ------------------------------------------------------------------ rain alert
def card_rain_alert(d):
    r = d["rain"]
    start = L("Now", "இப்போது") if r["now"] else fmt_h(r["start"])
    end = fmt_h(r["end"])
    en = f"Rain will continue until {end}." if r["now"] else f"Rain is expected to start around {start}."
    ta = f"{end} வரை மழை தொடர வாய்ப்புள்ளது." if r["now"] else f"{start} அளவில் மழை தொடங்கலாம்."
    mm = f" (~{r['mm']:.1f} mm)" if r.get("mm", 0) >= 0.1 else ""
    extra_en = f"{rain_level(r.get('level'))}{mm}" if not TA else ""
    first, second = (ta, en) if TA else (en, ta)
    return template(f"""
    <article class="card alert">
      <div class="big">⛈️</div>
      <h1 class="ta">{L("Rain alert", "மழை எச்சரிக்கை")}</h1>
      <div class="ta-h ta">{L("திடீர் மழை எச்சரிக்கை", "Rain alert")}</div>
      <div class="a-stats">
        <div class="a-stat"><div class="l ta">{L("Starts", "தொடக்கம்")}</div><div class="v ta">{start}</div></div>
        <div class="a-stat"><div class="l ta">{L("Until", "வரை")}</div><div class="v">{end}</div></div>
        <div class="a-stat"><div class="l ta">{L("Chance", "வாய்ப்பு")}</div><div class="v">{r['chance']}%</div></div>
      </div>
      <div class="a-msg"><div class="m1 ta">{esc(first)}</div><div class="m2 ta">{esc(second)}{(' · ' + esc(rain_level(r.get('level')) + mm)) if TA else ''}</div></div>
      <div class="a-tips"><div class="a-tip ta">🧺 {L("Bring clothes in", "துணிகளை எடுங்கள்")}</div><div class="a-tip ta">☂️ {L("Take umbrella", "குடை எடுங்கள்")}</div><div class="a-tip ta">🚗 {L("Drive slowly", "மெதுவாக ஓட்டவும்")}</div></div>
      {'<div style="margin-top:10px;font-size:15px;font-weight:700;color:#9fd3ff">' + esc(extra_en) + '</div>' if extra_en else ''}
    </article>""")


# ------------------------------------------------------------------ birthday
def photo_uri(name, photo=None):
    """Find a photo for this person: the `photo` column, or photos/<name>.jpg in the repo."""
    if photo and str(photo).startswith("http"): return photo
    cands = [Path(photo)] if photo else []
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    for ext in ("jpg", "jpeg", "png", "webp"):
        cands += [Path("photos") / f"{slug}.{ext}", Path("photos") / f"{name.lower()}.{ext}"]
    for p in cands:
        try:
            if p.is_file():
                mime = mimetypes.guess_type(p.name)[0] or "image/jpeg"
                return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"
        except Exception:
            pass
    return None

def build_birthday_html(name, age, wish=None, photo=None):
    n = len(name)
    size = 60 if n <= 8 else 50 if n <= 12 else 40 if n <= 18 else 32
    age_pill = f'<div class="ag ta">🎈 {L(f"Turns {age} today", f"இன்று {age} வயது")}</div>' if age else ""
    default_wish = L("Wishing you health, joy and a wonderful year ahead.", "ஆரோக்கியமும் மகிழ்ச்சியும் நிறைந்த இனிய ஆண்டாக அமையட்டும்.")
    uri = photo_uri(name, photo)
    top = (f'<img class="photo" src="{esc(uri)}"><div class="badge">🎂</div>' if uri else '<div class="cake">🎂</div>')
    confetti = "".join(
        f'<i class="cf" style="left:{x}%;top:{y}%;background:{c};transform:rotate({r}deg)"></i>'
        for x, y, c, r in [(8, 6, "#ffd54a", 20), (84, 8, "#7fe3ff", 50), (22, 16, "#fff", 70), (70, 20, "#ffd54a", 10),
                           (92, 34, "#fff", 40), (6, 40, "#7fe3ff", 80), (12, 74, "#ffd54a", 30), (88, 70, "#fff", 60),
                           (30, 88, "#7fe3ff", 15), (76, 90, "#ffd54a", 75)])
    return template(f"""
    <article class="card bday">
      {confetti}
      {top}
      <div class="hb ta">{L("Happy Birthday", "பிறந்தநாள் வாழ்த்துக்கள்")}</div>
      <div class="nm ta" style="font-size:{size}px">{esc(name)}</div>
      {age_pill}
      <div class="wish ta">{esc(wish or default_wish)}</div>
      <div class="love ta">{L("With love from the family 💛", "குடும்பத்தின் அன்புடன் 💛")}</div>
    </article>""")


# ------------------------------------------------------------------ plain-text captions
# Shown under the first image, so the key facts can be read without opening it.
def _cut(lines, limit=1000):
    out, n = [], 0
    for ln in lines:
        if n + len(ln) + 1 > limit: break
        out.append(ln); n += len(ln) + 1
    return "\n".join(out)

def caption_daily(d):
    now = d["now"]
    p = d.get("panchangam") or {}
    fest = festival(d)
    _, vtext = verdict(d)
    aq_name, _ = aqi_info(d["aqi"])
    aq = f"AQI {d['aqi_val']:.0f} {aq_name}" if d.get("aqi_val") is not None else aq_name
    uv_name, _ = uv_info(d.get("uv") or 0)
    r = d.get("rain")
    if r:
        mm = f", ~{r['mm']:.1f} mm" if r.get("mm", 0) >= 0.1 else ""
        rain = L(f"☔ {rain_level(r.get('level'))} {'now' if r['now'] else fmt_h(r['start'])} to {fmt_h(r['end'])} ({r['chance']}%{mm})",
                 f"☔ {rain_level(r.get('level'))} {'இப்போது' if r['now'] else fmt_h(r['start'])} முதல் {fmt_h(r['end'])} வரை ({r['chance']}%{mm})")
    else:
        rain = L("☔ No rain expected today", "☔ இன்று மழை இல்லை")

    lines = []
    if fest: lines.append(fest["text"])
    lines += [
        f"🌤️ {d['city']} · {now.strftime('%a, %d %b')}",
        f"👉 {vtext}",
        f"🌡️ {d['temp']:.0f}°C ({L('feels', 'உணர்வு')} {d['feels']:.0f}°) · {L('High', 'அதிகம்')} {d['t_max']:.0f}° / {L('Low', 'குறைவு')} {d['t_min']:.0f}° · {cond_text(d)}",
        rain,
        f"💨 {d['wind']:.0f} km/h · 🫁 {aq} · ☀️ UV {d.get('uv') or 0:.0f} ({uv_name})" + (f" · 💧 {d['humidity']}%" if d.get("humidity") is not None else ""),
        f"🌅 {short_time(d['sunrise'])} · 🌇 {short_time(d['sunset'])}",
    ]
    if p.get("tamil_date"):
        m, n = p["tamil_date"].rsplit(" ", 1)
        line = f"🪷 {TAMIL_MONTHS.get(m, m)} {n}"
        if p.get("special"): line += " · " + " · ".join(p["special"])
        lines.append(line)
        if p.get("nakshatra"): lines.append(f"⭐ {p['nakshatra']}")
    if p.get("nalla"): lines.append(f"✅ {L('Nalla neram', 'நல்ல நேரம்')} {p['nalla']}")
    if p.get("rahu"): lines.append(f"🚫 {L('Rahu', 'ராகு')} {p['rahu']}")
    if d.get("metals"): lines.append(f"🥇 ₹{inr(d['metals']['gold22'])}/g · 🥈 ₹{inr(d['metals']['silver'])}/g")
    if d["today"]:
        lines.append("")
        lines += [f"{i['icon']} {i['text']}" for i in d["today"][:4]]
    soon = [i for i in d["upcoming"] if i["days_left"] <= 3]
    for i in soon[:2]:
        lines.append(f"⏳ {i['text']} · {countdown(i['days_left'])}")
    return _cut(lines)

def caption_rain(d):
    r = d["rain"]
    when = L("now", "இப்போது") if r["now"] else L(f"around {fmt_h(r['start'])}", f"{fmt_h(r['start'])} அளவில்")
    mm = f" (~{r['mm']:.1f} mm)" if r.get("mm", 0) >= 0.1 else ""
    return (f"⛈️ {L('Rain alert', 'மழை எச்சரிக்கை')} · {d['city']}\n"
            f"{rain_level(r.get('level'))}{mm} {when} → {fmt_h(r['end'])} ({r['chance']}%)\n"
            f"🧺 {L('Bring clothes in', 'துணிகளை எடுங்கள்')} · ☂️ {L('Take an umbrella', 'குடை எடுங்கள்')}")
