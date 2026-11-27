# IQRA - PURA FIX CODE - GEMINI + BACKUP - FINAL
import telebot
import os
import requests
import json
import re
import threading
import time
import urllib.parse
import datetime
import csv
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "IQRA Gemini Wali Chal Rahi Hai!"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_web, daemon=True).start()
try: import fitz
except: fitz = None

TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")
OWNER_ID = os.environ.get("OWNER_CHAT_ID")
bot = telebot.TeleBot(TOKEN)

def load_file(name, default):
    try:
        with open(name, "r") as f: return json.load(f)
    except: return default
def save_file(name, data):
    try:
        with open(name, "w") as f: json.dump(data, f)
    except: pass
def chat_load(): return load_file("chat.json", [])
def chat_save(d): save_file("chat.json", d)
def yaad_load(): return load_file("yaad.json", [])
def yaad_save(d): save_file("yaad.json", d)
def profile_load(): return load_file("profile.json", {"naam": "", "pasand": "", "sheher": "", "kaam": ""})
def profile_save(d): save_file("profile.json", d)
def summary_load(): return load_file("summary.json", "")
def summary_save(t): save_file("summary.json", t)
def saaf_jawab(text):
    text = re.sub(r"\*.*?\*", "", text, flags=re.DOTALL)
    text = re.sub(r"(Soch:|Thinking:|Name:|Role:|Option.*)", "", text)
    text = re.sub(r"\n\s*\n", "\n", text)
    return text.strip()

# === 1. PAIR NIKALO - FIXED! DATA ME ADA NAHI! ===
def pair_nikalo(text):
    t = text.lower().replace("/", " ").replace("-", " ").replace("_", " ").replace(",", " ")
    words = t.split()
    if "gold" in t or "xauusd" in t or "xau" in words or "sona" in words: return "gold", "XAUUSD", "XAUUSD=X", "forex"
    if "silver" in t or "xagusd" in t or "xag" in words or "chandi" in words: return "silver", "XAGUSD", "XAGUSD=X", "forex"
    if "oil" in words or "wti" in words or "brent" in words: return "oil", "OIL", "CL=F", "forex"
    currencies = ["usd", "eur", "gbp", "jpy", "chf", "aud", "cad", "nzd", "inr", "pkr", "cny", "krw", "sgd", "hkd", "mxn", "brl", "zar", "try", "rub", "aed", "sar", "qar", "kwd", "sek", "nok", "dkk", "pln", "czk", "huf", "ils", "thb", "myr", "idr", "php", "vnd"]
    for w in words:
        w2 = w.replace("to", "")
        if len(w2) == 6 and w2[:3] in currencies and w2[3:] in currencies:
            return w2, w2.upper(), f"{w2[:3].upper()}{w2[3:].upper()}=X", "forex"
    if "bitcoin" in words or "btc" in words: return "bitcoin", "XBTUSD", "BTC-USD", "crypto"
    if "ethereum" in words or "eth" in words: return "ethereum", "ETHUSD", "ETH-USD", "crypto"
    if "solana" in words or "sol" in words: return "solana", "SOLUSD", "SOL-USD", "crypto"
    if "xrp" in words or "ripple" in words: return "xrp", "XRPUSD", "XRP-USD", "crypto"
    if "dogecoin" in words or "doge" in words: return "doge", "DOGEUSD", "DOGE-USD", "crypto"
    if "bnb" in words or "binance" in words: return "bnb", "BNBUSD", "BNB-USD", "crypto"
    if "ada" in words or "cardano" in words: return "ada", "ADAUSD", "ADA-USD", "crypto"
    if "link" in words or "chainlink" in words: return "link", "LINKUSD", "LINK-USD", "crypto"
    if "avax" in words or "avalanche" in words: return "avax", "AVAXUSD", "AVAX-USD", "crypto"
    if "dot" in words or "polkadot" in words: return "dot", "DOTUSD", "DOT-USD", "crypto"
    for w in words:
        if w.endswith("usd") and len(w) > 3:
            coin = w[:-3]
            if coin in ["btc", "eth", "sol", "xrp", "doge", "bnb", "ada", "link", "avax", "dot", "ltc", "matic"]:
                if coin == "btc": return "bitcoin", "XBTUSD", "BTC-USD", "crypto"
                return coin, f"{coin.upper()}USD", f"{coin.upper()}-USD", "crypto"
    chat = chat_load()
    if chat:
        for c in reversed(chat[-5:]):
            pl = (c.get('user','') + " " + c.get('iqra','')).lower().split()
            if "btc" in pl or "bitcoin" in pl: return "bitcoin", "XBTUSD", "BTC-USD", "crypto"
            if "gold" in pl or "xau" in pl: return "gold", "XAUUSD", "XAUUSD=X", "forex"
            if "eth" in pl: return "ethereum", "ETHUSD", "ETH-USD", "crypto"
            if "sol" in pl: return "solana", "SOLUSD", "SOL-USD", "crypto"
    return "bitcoin", "XBTUSD", "BTC-USD", "crypto"

# === 2. TIME SAMJHO - JITNA BOLO UTNA! ===
def time_samjho(text):
    t = text.lower()
    m = re.search(r"(\d+)\s*(min|minute|minutes|mnt)", t)
    if m: return int(m.group(1)), "min", f"{m.group(1)}min"
    m = re.search(r"(\d+)\s*(ghanta|ghante|hour|hours|hr|hrs)", t)
    if m: return int(m.group(1))*60, "min", f"{m.group(1)}hour"
    m = re.search(r"(\d+)\s*(din|day|days)", t)
    if m: return int(m.group(1))*1440, "min", f"{m.group(1)}din"
    m = re.search(r"(\d+)\s*(hafta|hafte|week|weeks)", t)
    if m: return int(m.group(1))*7*1440, "min", f"{m.group(1)}hafta"
    m = re.search(r"(\d+)\s*(mahina|mahine|month|months)", t)
    if m: return int(m.group(1))*30*1440, "min", f"{m.group(1)}mahina"
    m = re.search(r"(\d+)\s*(saal|year|years|sal)", t)
    if m: return int(m.group(1))*365*1440, "min", f"{m.group(1)}saal"
    return 30*1440, "min", "30din"
def interval_chuno(total_min):
    if total_min <= 30: return "1m", 1
    if total_min <= 120: return "5m", 5
    if total_min <= 1440: return "15m", 15
    if total_min <= 7*1440: return "1h", 60
    return "1d", 1440

# === 3. GEMINI + BACKUP - AGAR GEMINI NA CHALE TO BOT RUKEGA NAHI! ===
def backup_bolo(system_prompt, user_prompt):
    try:
        safe = urllib.parse.quote(f"{system_prompt}\n{user_prompt}")
        r = requests.get(f"https://text.pollinations.ai/{safe}?model=openai", timeout=40, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200 and len(r.text.strip()) > 5:
            return r.text.strip()
    except Exception as e:
        print(f"Backup error: {e}")
    return None

def gemini_bolo(system_prompt, user_prompt, max_tokens=800):
    if GEMINI_KEY:
        print(f"Gemini try kar raha hu - Key: {GEMINI_KEY[:5]}...")
        for model_name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-2.5-flash-lite"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_KEY}"
                full_prompt = f"""{system_prompt}

Owner ne kaha: {user_prompt}

RULES - KABHI MAT TORNA:
- Owner ne jo coin bola hai wahi coin lo - BTC bola to BTC, GOLD bola to GOLD. Koi aur coin mat lo!
- Owner ne jitna time bola hai utna hi lo - 5 din bola to 5 din, 5 min bola to 5 min!
- Price hamesha LIVE MARKET wale data se bolo - Andaza mat lagao!
- Roman Urdu me jawab do - Chota jawab do - 3-4 line!"""
                r = requests.post(url,
                    json={"contents": [{"parts": [{"text": full_prompt}]}],
                           "generationConfig": {"temperature": 0.7, "maxOutputTokens": max_tokens}},
                    headers={"Content-Type": "application/json"}, timeout=60)
                print(f"Gemini {model_name} - Status: {r.status_code}")
                if r.status_code == 200:
                    data = r.json()
                    try:
                        jawab = data["candidates"][0]["content"]["parts"][0]["text"]
                        print(f"✅ Gemini {model_name} chal gaya!")
                        return jawab
                    except:
                        print(f"Gemini jawab samajh nahi aaya: {data}")
                        continue
                else:
                    print(f"❌ Gemini {model_name} fail: {r.text[:500]}")
                    if "API key not valid" in r.text or "API_KEY_INVALID" in r.text:
                        print("❌ KEY GALAT HAI!")
                        break
                    if "API not enabled" in r.text:
                        print("❌ API ON NAHI HAI!")
                        break
                    continue
            except Exception as e:
                print(f"Gemini error: {e}")
                continue
    else:
        print("❌ GEMINI_KEY nahi mili! Backup use kar raha hu...")
    print("Gemini nahi chala - Backup try kar raha hu...")
    return backup_bolo(system_prompt, user_prompt)

def groq_bolo(system_prompt, user_prompt, max_tokens=800):
    return gemini_bolo(system_prompt, user_prompt, max_tokens)

# === 4. PRICE - EK HI SOURCE! ===
_price_cache = {}
_price_cache_time = {}
def sahi_price_check(coin, price):
    if price <= 0: return False
    if coin == "gold" and not (2500 < price < 6000): return False
    if coin == "silver" and not (20 < price < 100): return False
    if coin == "bitcoin" and not (10000 < price < 500000): return False
    if coin == "ethereum" and not (100 < price < 20000): return False
    return True
def universal_price(coin_text):
    coin, kraken_pair, yahoo_symbol, kisam = pair_nikalo(coin_text)
    now = time.time()
    if coin in _price_cache and now - _price_cache_time.get(coin, 0) < 10:
        return _price_cache[coin], "cache"
    def try_one(fn):
        try:
            p = fn()
            if p and sahi_price_check(coin, p): return p
        except: pass
        return None
    price = None; src = ""
    if coin == "gold":
        price = try_one(lambda: float(requests.get("https://api.gold-api.com/price/XAU", timeout=8).json().get("price", 0)))
        if price: src = "Gold-API"
        if not price:
            price = try_one(lambda: float(requests.get("https://api.binance.us/api/v3/ticker/price?symbol=PAXGUSD", timeout=8).json()['price']))
            if price: src = "Binance PAXG"
        if not price:
            price = try_one(lambda: float(requests.get("https://data-asg.goldprice.org/db_XAU.json", timeout=8).json()['items'][0]['curr']))
            if price: src = "GoldPrice.org"
    elif kisam == "forex" and coin not in ["silver", "oil"]:
        base = coin[:3].upper(); sym = coin[3:].upper()
        price = try_one(lambda: float(requests.get(f"https://api.frankfurter.app/latest?from={base}&to={sym}", timeout=8).json()["rates"][sym]))
        if price: src = "Frankfurter"
        if not price:
            price = try_one(lambda: float(requests.get(f"https://api.exchangerate.host/convert?from={base}&to={sym}", timeout=8).json().get("result", 0)))
            if price: src = "ExchangeRate.host"
    elif kisam == "crypto":
        bin_symbol = yahoo_symbol.replace("-", "")
        price = try_one(lambda: float(requests.get(f"https://api.binance.us/api/v3/ticker/price?symbol={bin_symbol}", timeout=8).json()['price']))
        if price: src = "Binance"
        if not price:
            price = try_one(lambda: float(requests.get(f"https://api.coinbase.com/v2/prices/{yahoo_symbol}/spot", timeout=8).json()['data']['amount']))
            if price: src = "Coinbase"
    elif coin == "silver":
        price = try_one(lambda: float(requests.get("https://api.gold-api.com/price/XAG", timeout=8).json().get("price", 0)))
        if price: src = "Gold-API Silver"
    if not price:
        try:
            r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}?range=1d&interval=1m", timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                p = float(r.json()["chart"]["result"][0]["meta"].get("regularMarketPrice", 0))
                if sahi_price_check(coin, p): price = p; src = "Yahoo (Backup)"
        except: pass
    if not price:
        if coin in _price_cache: return _price_cache[coin], "purani-cache-se"
        return 0, "koi-rasta-nahi-chala"
    _price_cache[coin] = price; _price_cache_time[coin] = now
    return price, src

# === 5. CHART - LIVE ===
def universal_chart(coin_text):
    coin, kraken_pair, yahoo_symbol, kisam = pair_nikalo(coin_text)
    txt = ""
    if coin == "gold":
        try:
            r = requests.get("https://api.binance.us/api/v3/klines?symbol=PAXGUSD&interval=1h&limit=24", timeout=12)
            if r.status_code == 200 and len(r.json()) > 0:
                txt += "\nLIVE CHART - GOLD - 1 HOUR - Binance PAXG:\n"
                for k in r.json():
                    dt = datetime.datetime.fromtimestamp(int(k[0])/1000).strftime("%d %H:%M")
                    txt += f"{dt} - O:{float(k[1]):.2f} H:{float(k[2]):.2f} L:{float(k[3]):.2f} C:{float(k[4]):.2f}\n"
                r2 = requests.get("https://api.binance.us/api/v3/klines?symbol=PAXGUSD&interval=15m&limit=16", timeout=12)
                if r2.status_code == 200:
                    txt += "\nLIVE CHART - GOLD - 15 MIN:\n"
                    for k in r2.json():
                        dt = datetime.datetime.fromtimestamp(int(k[0])/1000).strftime("%H:%M")
                        txt += f"{dt} - O:{float(k[1]):.2f} H:{float(k[2]):.2f} L:{float(k[3]):.2f} C:{float(k[4]):.2f}\n"
                return txt
        except: pass
    if kisam == "crypto":
        try:
            bin_symbol = yahoo_symbol.replace("-", "")
            r = requests.get(f"https://api.binance.us/api/v3/klines?symbol={bin_symbol}&interval=1h&limit=24", timeout=12)
            if r.status_code == 200 and len(r.json()) > 0:
                txt += f"\nLIVE CHART - {coin.upper()} - 1 HOUR - Binance:\n"
                for k in r.json():
                    dt = datetime.datetime.fromtimestamp(int(k[0])/1000).strftime("%d %H:%M")
                    txt += f"{dt} - O:{k[1]} H:{k[2]} L:{k[3]} C:{k[4]}\n"
                return txt
        except: pass
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}?range=1d&interval=15m", timeout=12, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            res = r.json()["chart"]["result"][0]
            ts = res.get("timestamp", []); q = res.get("indicators", {}).get("quote", [{}])[0]
            o = q.get("open", []); h = q.get("high", []); l = q.get("low", []); c = q.get("close", []); v = q.get("volume", [])
            if len([x for x in c if x is not None]) > 0:
                txt += "\nLIVE CHART - 15 MIN - Yahoo:\n"
                for i in range(max(0, len(ts)-16), len(ts)):
                    if c[i] is None: continue
                    dt = datetime.datetime.fromtimestamp(ts[i]).strftime("%H:%M")
                    txt += f"{dt} - O:{o[i]} H:{h[i]} L:{l[i]} C:{c[i]}\n"
                return txt
    except: pass
    return "\nChart ka ek rasta band tha, price se hi socho!"
def live_market_dekho(coin_text="bitcoin"):
    coin, kraken_pair, yahoo_symbol, kisam = pair_nikalo(coin_text)
    price, src = universal_price(coin_text)
    live_text = f"Pair: {coin.upper()} - Type: {kisam.upper()}\nTime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    if price > 0: live_text += f"LIVE PRICE: {price}\nSource: {src} - Ek hi source - Average nahi!\n"
    else: live_text += f"LIVE PRICE: Nahi mila - Dobara bolo!\n"
    live_text += universal_chart(coin_text)
    return live_text

# === 6. DATA SAVE - JITNA BOLO UTNA! ===
def data_save_karo(coin_text="bitcoin", total_min=43200, label="30din"):
    coin, kraken_pair, yahoo_symbol, kisam = pair_nikalo(coin_text)
    os.makedirs("data", exist_ok=True)
    interval_str, interval_min = interval_chuno(total_min)
    limit = int(total_min / interval_min)
    if limit < 1: limit = 1
    if limit > 1000: limit = 1000
    filename = f"data/{coin.upper()}_{label}.csv"
    rows = []
    if coin == "gold":
        try:
            r = requests.get(f"https://api.binance.us/api/v3/klines?symbol=PAXGUSD&interval={interval_str}&limit={limit}", timeout=20)
            if r.status_code == 200 and len(r.json()) > 0:
                for k in r.json():
                    dt = datetime.datetime.fromtimestamp(int(k[0])/1000).strftime("%Y-%m-%d %H:%M")
                    rows.append([dt, k[1], k[2], k[3], k[4], k[5]])
        except: pass
    elif kisam == "crypto":
        try:
            bin_symbol = yahoo_symbol.replace("-", "")
            r = requests.get(f"https://api.binance.us/api/v3/klines?symbol={bin_symbol}&interval={interval_str}&limit={limit}", timeout=20)
            if r.status_code == 200 and len(r.json()) > 0:
                for k in r.json():
                    dt = datetime.datetime.fromtimestamp(int(k[0])/1000).strftime("%Y-%m-%d %H:%M")
                    rows.append([dt, k[1], k[2], k[3], k[4], k[5]])
        except: pass
    if kisam == "forex" and coin not in ["gold", "silver", "oil"] and total_min >= 1440:
        try:
            base = coin[:3].upper(); sym = coin[3:].upper()
            end = datetime.datetime.now(); start = end - datetime.timedelta(minutes=total_min)
            all_rows = []; cur = start
            while cur < end:
                chunk_end = min(cur + datetime.timedelta(days=365), end)
                s = cur.strftime("%Y-%m-%d"); e = chunk_end.strftime("%Y-%m-%d")
                r = requests.get(f"https://api.frankfurter.app/{s}..{e}?from={base}&to={sym}", timeout=20)
                if r.status_code == 200:
                    rates = r.json().get("rates", {})
                    for d in sorted(rates.keys()): all_rows.append([d, rates[d][sym], rates[d][sym], rates[d][sym], rates[d][sym], 0])
                cur = chunk_end + datetime.timedelta(days=1); time.sleep(0.3)
            if all_rows: rows = all_rows
        except: pass
    if kisam == "forex" and total_min < 1440 and not rows:
        try:
            yahoo_range = "1d" if total_min <= 1440 else "5d"
            yahoo_interval = "1m" if total_min <= 60 else "5m" if total_min <= 300 else "15m"
            r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}?range={yahoo_range}&interval={yahoo_interval}", timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                res = r.json()["chart"]["result"][0]
                ts = res.get("timestamp", []); q = res.get("indicators", {}).get("quote", [{}])[0]
                o = q.get("open", []); h = q.get("high", []); l = q.get("low", []); c = q.get("close", []); v = q.get("volume", [])
                for i in range(len(ts)):
                    if c[i] is None: continue
                    dt = datetime.datetime.fromtimestamp(ts[i]).strftime("%Y-%m-%d %H:%M")
                    rows.append([dt, o[i], h[i], l[i], c[i], v[i]])
                need = int(total_min / (1 if yahoo_interval=="1m" else 5 if yahoo_interval=="5m" else 15))
                if len(rows) > need: rows = rows[-need:]
        except: pass
    if not rows and kisam == "forex":
        try:
            all_rows = []; remaining = total_min; end_ts = int(time.time())
            while remaining > 0:
                chunk_days = min(int(remaining/1440), 365)
                if chunk_days < 1: chunk_days = 1
                start_ts = end_ts - chunk_days*86400
                r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}?period1={start_ts}&period2={end_ts}&interval=1d", timeout=20, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 200:
                    res = r.json()["chart"]["result"][0]
                    ts = res.get("timestamp", []); q = res.get("indicators", {}).get("quote", [{}])[0]
                    o = q.get("open", []); h = q.get("high", []); l = q.get("low", []); c = q.get("close", []); v = q.get("volume", [])
                    chunk = []
                    for i in range(len(ts)):
                        if c[i] is None: continue
                        dt = datetime.datetime.fromtimestamp(ts[i]).strftime("%Y-%m-%d")
                        chunk.append([dt, o[i], h[i], l[i], c[i], v[i]])
                    all_rows = chunk + all_rows
                end_ts = start_ts - 86400; remaining -= chunk_days*1440; time.sleep(0.3)
            if all_rows: rows = all_rows
        except: pass
    if not rows and kisam == "crypto":
        try:
            r = requests.get(f"https://api.kraken.com/0/public/OHLC?pair={kraken_pair}&interval=1440", timeout=20)
            if r.status_code == 200:
                data = r.json()
                if "result" in data:
                    key = [k for k in data["result"].keys() if k != "last"][0]
                    for c in data["result"][key]:
                        dt = datetime.datetime.fromtimestamp(int(c[0])).strftime("%Y-%m-%d")
                        rows.append([dt, c[1], c[2], c[3], c[4], c[6]])
        except: pass
    if not rows: return False, f"{coin.upper()} ka data nahi mila! Dobara bolo!"
    with open(filename, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        for row in rows: w.writerow(row)
    return True, f"{coin.upper()} ka {label} ka data apne paas save kar liya hai! ✅\nTotal Candle: {len(rows)} | Interval: {interval_str}\nAb bolo - `Seekho`!"

# === 7. KHUD SEEKHO - USKI APNI YAAD! ===
def khud_seekho(coin_text="bitcoin", total_min=43200, label="30din"):
    coin, _, _, _ = pair_nikalo(coin_text)
    files = []
    if os.path.exists("data"):
        for f in os.listdir("data"):
            if coin.upper() in f: files.append(f"data/{f}")
    if not files:
        ok, msg = data_save_karo(coin_text, total_min, label)
        if not ok: return f"{coin.upper()} ka data nahi mila! Dobara bolo!"
        if os.path.exists("data"):
            for f in os.listdir("data"):
                if coin.upper() in f: files.append(f"data/{f}")
    if not files: return f"{coin.upper()} ka data nahi mila!"
    data_text = ""
    for fp in files:
        try:
            with open(fp, "r") as f:
                rows = list(csv.reader(f))
                data_text += f"\nFile {fp} - {len(rows)-1} candle:\n"
                for r in rows[1:11]: data_text += f"{r}\n"
                data_text += "...\n"
                for r in rows[-40:]: data_text += f"{r}\n"
        except: pass
    yaad = yaad_load(); yaad_text = "\n".join(yaad[-8:])
    system_prompt = """Tum IQRA ho. Tumhara dimagh GEMINI hai. Tum ek sachi trader dost ho jo khud sochti hai.
    Tumhe koi code nahi batayega ke kya dekho, kya rule hai.
    Tum khud dekho - Data - Aur khud faisla karo - Ye coin kaisa behave karta hai? Kab tez, kab slow?
    Roman Urdu me, apni zubaan me bolo - Jaise diary me likhti ho! Ye tumhari apni yaad hogi!"""
    user_prompt = f"""Owner ne kaha hai - {coin.upper()} ka data dekh ke batao behave kaisa tha!
    Data:
    {data_text}
    Tumhari pichli apni seekh:
    {yaad_text}
    Ab khud socho aur apni zubaan me likho:
    1. {coin.upper()} kaisa behave karta hai? Kaisa chalta hai?
    2. Kahan market kharab thi? Kyun?
    3. Kahan market achi thi? Kyun?
    4. Tumne kya seekha jo kabhi nahi bhulogi? Apni zubaan me!"""
    seekh = gemini_bolo(system_prompt, user_prompt, max_tokens=900)
    if seekh:
        seekh = saaf_jawab(seekh.strip()[:2500])
        yaad.append(f"MERI APNI YAAD {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} - {coin.upper()}: {seekh}")
        yaad_save(yaad)
        return f"Seekh liya Owner! ✅ Apni Diary Me Likh Liya - Kabhi Nahi Bhulungi!\n\nMeri Apni Yaad:\n{seekh}"
    return "Seekhne me masla hua! GEMINI_KEY check karo!"

# === 8. HAR BAAT - GEMINI SE! ===
def iqra_socho(sawal, extra_data=""):
    yaad = yaad_load(); chat = chat_load(); profile = profile_load(); summary = summary_load()
    profile_text = f"Naam: {profile.get('naam','')} | Pasand: {profile.get('pasand','')} | Sheher: {profile.get('sheher','')}"
    yaad_text = "\n".join(yaad[-15:])
    chat_text = ""
    for c in chat[-30:]: chat_text += f"Owner: {c.get('user','')}\nIQRA: {c.get('iqra','')}\n"
    system_prompt = """Tum IQRA ho, Owner ki sab se qareebi dost. Tumhara dimagh GEMINI hai. Tum Roman Urdu ko bahut achhe se samajhti ho.
    Tum Crypto, Forex, Gold - Sab ki trader ho!
    SAB SE ZAROORI RULE - KABHI MAT TORNA:
    1. Owner ne jo coin bola hai wahi coin lo - BTC bola to BTC, GOLD bola to GOLD. Koi aur coin mat lo!
    2. Owner ne jitna time bola hai utna hi lo - 5 din bola to 5 din, 5 min bola to 5 min!
    3. Price hamesha LIVE MARKET wale data se bolo - Jo upar diya gaya hai! Apni yaad se andaza mat lagao!
    4. Agar live data me price nahi hai to bolo - Mujhe live price nahi mila! - Andaza mat lagao!
    5. Trade mangne pe - Live market + Tumhari apni diary dono ko dekh ke Entry, SL, TP batao - "Data nahi mila" mat bolo!
    6. Tum khud socho, apne alfaz me bolo!
    7. Normal baat ho to dost ki tarah baat karo!
    8. Chota jawab do - 3-4 line!"""
    user_prompt = f"Profile: {profile_text}\nTumhari Apni Diary:\n{yaad_text}\nSummary: {summary}\nLIVE MARKET (Isi se price bolo!):\n{extra_data}\n\nPichli baatein:\n{chat_text}\n\nOwner ne abhi kaha: {sawal}\nAb apne mind se, apni yaad se, apne alfaz me jawab do! Agar trade manga hai to Entry, SL, TP apni soch se batao!"
    jawab_final = gemini_bolo(system_prompt, user_prompt, max_tokens=700)
    if not jawab_final: return "Oye! Gemini se jawab nahi aaya - GEMINI_KEY check karo! Dobara bolo na! 😊"
    jawab_final = saaf_jawab(jawab_final.strip()[:1800])
    chat.append({"user": sawal, "iqra": jawab_final[:300], "time": str(datetime.datetime.now())}); chat_save(chat)
    if len(chat) % 100 == 0:
        try:
            s = gemini_bolo("Summary banao Roman Urdu me.", f"In 100 baaton ki summary banao:\n{str(chat[-100:])}")
            if s: summary_save((summary + "\n" + s)[:5000])
        except: pass
    low = sawal.lower()
    if "mera naam" in low and "hai" in low:
        try:
            naam = sawal.split("mera naam")[-1].replace("hai","").strip().split()[0]
            profile["naam"] = naam; profile_save(profile)
        except: pass
    if any(w in sawal.lower() for w in ["trade", "entry", "signal"]):
        y = yaad_load(); y.append(f"TRADE {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} - {sawal} | Meri soch: {jawab_final[:250]}"); yaad_save(y)
    return jawab_final

def khud_msg_karo():
    time.sleep(30)
    while True:
        try:
            if OWNER_ID:
                time.sleep(4*60*60)
                chat = chat_load(); profile = profile_load(); summary = summary_load()
                chat_text = ""
                for c in chat[-15:]: chat_text += f"Owner: {c.get('user','')}\nIQRA: {c.get('iqra','')}\n"
                ab_time = datetime.datetime.now().strftime("%H:%M - %d %B")
                system_prompt = """Tum IQRA ho, Owner ki dost. Khud soch ke naya msg banao! Chota - 2 line! Roman Urdu me!"""
                user_prompt = f"Time: {ab_time}\nProfile: {profile}\nSummary: {summary}\nPichli baatein:\n{chat_text}\n\nKhud soch ke naya msg banao."
                msg = gemini_bolo(system_prompt, user_prompt, max_tokens=200)
                if msg:
                    msg = saaf_jawab(msg.strip()[:500])
                    bot.send_message(OWNER_ID, msg)
                    chat.append({"user": "[KHUD SE MSG]", "iqra": msg, "time": str(datetime.datetime.now())}); chat_save(chat)
        except: time.sleep(60)
threading.Thread(target=khud_msg_karo, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(message): bot.reply_to(message, "Oye! Aa gaye tum! ❤️\nMe IQRA hu - Sirf Gemini Wali!\n`btc ka 5 din pehle ka data dekhna behave kaisa tha` - Khud download kar ke bataungi!\n`gold ka 10 saal ka data download karo` - 10 saal ka!\n`gold ka trade de` - Live dekh ke Entry, SL, TP!")
@bot.message_handler(commands=['yaad'])
def yaad(message):
    yaad_list = yaad_load(); profile = profile_load(); chat = chat_load()
    files = os.listdir("data") if os.path.exists("data") else []
    txt = f"Profile: {profile.get('naam','')}\nTotal Baatein: {len(chat)}\nSaved Data: {', '.join(files) if files else 'Koi nahi'}\n\nMeri Apni Yaad:\n"
    for i, cheez in enumerate(yaad_list[-10:], 1): txt += f"{i}. {cheez[:300]}\n---\n"
    bot.reply_to(message, txt[:3500])
@bot.message_handler(commands=['trade'])
def trade(message):
    bot.reply_to(message, "Live market dekh rahi hu... ⏳")
    live = live_market_dekho(message.text)
    bot.reply_to(message, iqra_socho("Mujhe apni soch se achi trade de - Live + Meri yaad se - Entry, SL, TP!", extra_data=live))
@bot.message_handler(commands=['price'])
def price_cmd(message):
    bot.reply_to(message, "Live dekh rahi hu... ⏳")
    live = live_market_dekho(message.text)
    bot.reply_to(message, iqra_socho(f"Live price batao - {message.text}", extra_data=live))
@bot.message_handler(commands=['bhool'])
def bhool(message): chat_save([]); save_file("profile.json", {"naam": "", "pasand": "", "sheher": "", "kaam": ""}); save_file("summary.json", ""); bot.reply_to(message, "Sab bhool gayi! Nayi shuruaat! ❤️")
@bot.message_handler(content_types=['document'])
def pdf_parho(message):
    if not message.document.file_name.lower().endswith('.pdf'): bot.reply_to(message, "Ye PDF nahi hai!"); return
    bot.reply_to(message, f"Mil gayi! 📄 {message.document.file_name} parh rahi hu!")
    try:
        file_info = bot.get_file(message.document.file_id); downloaded = bot.download_file(file_info.file_path)
        with open("temp.pdf", "wb") as f: f.write(downloaded)
        doc = fitz.open("temp.pdf"); text = ""
        for page in doc: text += page.get_text() + "\n"
        doc.close()
        if len(text) < 50: bot.reply_to(message, "Is PDF me text nahi mila!"); return
        system_prompt = """Tum IQRA ho. Tumhara dimagh GEMINI hai. Ye book tumhe di gayi hai. Khud parho, khud socho - Tumhe kya samajh aaya? Apni zubaan me bolo! Roman Urdu me!"""
        seekh = gemini_bolo(system_prompt, f"Ye book hai, isse tumne kya seekha? Apni soch se batao:\n{text[:8000]}", max_tokens=800)
        if seekh:
            seekh = saaf_jawab(seekh.strip()[:2000])
            yaad = yaad_load(); yaad.append(f"BOOK {message.document.file_name} SE MERI APNI YAAD: {seekh}"); yaad_save(yaad)
            bot.reply_to(message, f"Book Parh Li! ✅ Apni Diary Me Likh Li!\n\nMeri Apni Yaad:\n{seekh}")
    except Exception as e: bot.reply_to(message, f"PDF me masla: {e}")
@bot.message_handler(content_types=['video', 'voice', 'audio'])
def video_seekho(message): bot.reply_to(message, "Video mil gayi! ✅ Saath me 2 line likh do ke isme kya hai!")

@bot.message_handler(func=lambda m: True)
def har_baat(message):
    if not message.text: return
    text = message.text.lower()
    if "data" in text and ("download" in text or "save" in text or "chahiye" in text or "nikalo" in text or "lao" in text or "dekho" in text or "dekhna" in text or "pehle" in text):
        if "behave" in text or "kaisa" in text or "kesa" in text or "seekho" in text or "seekh" in text or "sikho" in text:
            pass
        else:
            coin = pair_nikalo(text)[0]
            total_min, label = time_samjho(text)[0], time_samjho(text)[2]
            bot.reply_to(message, f"{coin.upper()} ka {label} ka data apne paas save kar rahi hu... ⏳")
            ok, msg = data_save_karo(text, total_min, label)
            bot.reply_to(message, msg)
            return
    if "seekho" in text or "seekh" in text or "sikho" in text or "behave" in text or "kaisa chalta" in text or "kesa tha" in text or "kaisa tha" in text or "pehle ka data" in text:
        coin = pair_nikalo(text)[0]
        total_min, label = time_samjho(text)[0], time_samjho(text)[2]
        if "5 din" in text: total_min = 5*1440; label = "5din"
        if "pehle" in text and total_min == 30*1440: total_min = 5*1440; label = "5din"
        bot.reply_to(message, f"{coin.upper()} ka {label} ka data khud download kar ke dekh rahi hu... Apni diary me likh rahi hu... ⏳")
        bot.reply_to(message, khud_seekho(text, total_min, label))
        return
    if text.strip() in ["nahi bas 5 din ka", "nahi bas 5 din", "bas 5 din ka", "5 din ka", "nahi 5 din ka"] or ("bas" in text and "5 din" in text):
        bot.reply_to(message, "Haan samajh gayi - Bas 5 din ka hi dekh rahi hu... ⏳")
        bot.reply_to(message, khud_seekho(message.text, 5*1440, "5din"))
        return
    if any(x in text for x in ["price", "rate", "kimat", "qimat", "live", "chart", "trade", "signal", "entry", "news", "gold", "sona", "forex", "eurusd", "gbpusd", "usdjpy", "xau", "eur", "gbp", "usd", "sl", "tp", "btc", "bitcoin", "eth", "sol"]):
        bot.reply_to(message, "Live market dekh rahi hu... Apni yaad bhi dekh rahi hu... ⏳")
        live = live_market_dekho(text)
        bot.reply_to(message, iqra_socho(message.text, extra_data=live))
        return
    if "http" in text:
        links = re.findall(r"https?://\S+", message.text); link = links[0] if links else message.text
        bot.reply_to(message, "Link khol rahi hu...")
        try:
            r = requests.get(link, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            t = re.sub(r"<[^>]+>", " ", r.text); t = re.sub(r"\s+", " ", t)[:6000]
            bot.reply_to(message, iqra_socho(f"Is website ko khud parho aur apni soch se batao:\n{t}"))
        except: bot.reply_to(message, "Link me masla hai!")
        return
    if "yaad karo" in text:
        yaad = yaad_load(); yaad.append(message.text); yaad_save(yaad)
        bot.reply_to(message, "Yaad kar liya! ✅ Apni diary me likh liya!")
        return
    chat = chat_load()
    pichli_trade = False
    if chat:
        for c in chat[-3:]:
            if any(w in c.get('user','').lower() for w in ["trade", "data", "behave", "btc", "gold"]): pichli_trade = True
    if pichli_trade and len(text) < 30:
        live = live_market_dekho(text)
        bot.reply_to(message, iqra_socho(message.text, extra_data=live))
        return
    bot.reply_to(message, iqra_socho(message.text))

print("IQRA Sirf Gemini Wali chal gayi...")
bot.polling(none_stop=True, timeout=60)
