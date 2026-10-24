import os, sys, time, json, requests, yaml, html
from datetime import datetime, timezone, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import ui

# Setup resilient API connection
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

def get_metals():
    key = os.environ.get("GOLD_API_KEY")
    if not key: return None
    try:
        g = session.get("https://www.goldapi.io/api/XAU/INR", headers={"x-access-token": key}, timeout=10).json()
        s = session.get("https://www.goldapi.io/api/XAG/INR", headers={"x-access-token": key}, timeout=10).json()
        # 1 Troy Ounce = 31.103 grams. 22K is ~91.6% of 24K.
        return {"gold22": int((g["price"] / 31.103) * 0.916), "silver": int(s["price"] / 31.103)}
    except: return None

def collect():
    # Fetch base weather data (omitted standard owm/openmeteo functions for brevity; use your existing ones replacing requests.get with session.get)
    key = os.environ["OWM_API_KEY"]
    zip_code = os.environ.get("ZIP_CODE") or "600001,IN"
    geo = session.get(f"https://api.openweathermap.org/geo/1.0/zip?zip={zip_code}&appid={key}").json()
    cur = session.get(f"https://api.openweathermap.org/data/2.5/weather?lat={geo['lat']}&lon={geo['lon']}&units=metric&appid={key}").json()
    
    tz = timezone(timedelta(seconds=cur["timezone"]))
    now = datetime.now(tz)
    
    # Base dictionary setup (Integrate your existing Panchangam and OpenMeteo logic here)
    d = {"city": cur["name"], "now": now, "temp": cur["main"]["temp"], "cond": cur["weather"][0]["description"].title(), "main": cur["weather"][0]["main"], "metals": get_metals()}
    
    # Load Events & Theme Logic
    try:
        with open("events.yaml", encoding="utf-8") as f: events = yaml.safe_load(f) or []
    except: events = []
    
    d["today"] = [] # Use your existing matches() logic here
    d["upcoming"] = []
    
    # Dynamic Theme
    d["theme"] = "default"
    festivals = ["diwali", "deepavali", "pongal", "new year", "ugadi", "navratri"]
    if any(any(f in str(e).lower() for f in festivals) for e in d["today"]):
        d["theme"] = "festival"

    return d

def render_png(html_str, path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 840, "height": 100})
        page.set_content(html_str)
        page.locator(".card").screenshot(path=path)
        b.close()
    return path

def send_photo(path, cap):
    with open(path, "rb") as f:
        session.post(f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendPhoto", data={"chat_id": os.environ['TELEGRAM_CHAT_ID'], "caption": cap}, files={"photo": f}, timeout=60)

def main():
    # Example placeholder for full integrated data collection
    d = collect() # Make sure to merge your existing detailed data collection logic inside this function
    
    render_png(ui.card_weather(d), "weather.png")
    send_photo("weather.png", "1/3: Today's Weather 🌦️")
    time.sleep(60)

    render_png(ui.card_advice(d), "advice.png")
    send_photo("advice.png", "2/3: Panchangam & Advice 🪷")
    time.sleep(60)

    render_png(ui.card_events(d), "events.png")
    send_photo("events.png", "3/3: Events & Bills 📅")

if __name__ == "__main__":
    main()
