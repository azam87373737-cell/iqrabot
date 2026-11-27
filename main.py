import telebot, os, requests, re, threading, datetime, csv, json, urllib.parse
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "IQRA LIVE"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_web, daemon=True).start()
try: import fitz
except: fitz = None

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_KEY = os.environ.get("GROQ_KEY")
bot = telebot.TeleBot(TOKEN)

def load(n, d):
    try:
        with open(n) as f: return json.load(f)
    except: return d
def save(n, d):
    try:
        with open(n, "w") as f: json.dump(d, f)
    except: pass

# ===== DIMAGH - 1. GROQ - GEMINI KHATAM =====
def gemini(system, user, max_tokens=1000):
    # Naam wahi hai taake baaki code na badle - andar GROQ hai
    if not GROQ_KEY:
        print("❌ GROQ_KEY nahi mili!")
        return None
    models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
    for model in models:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                json={"model": model,
                      "messages": [{"role": "system", "content": f"{system}\n\nTum IQRA ho. Apne dil se, apni soch se bolo. Code me kuch save nahi hai. Roman Urdu me bolo. Friendly bolo."},
                                   {"role": "user", "content": user}],
                      "temperature": 0.9, "max_tokens": max_tokens},
                headers={"Authorization": f"Bearer {GROQ_KEY.strip()}", "Content-Type": "application/json"}, timeout=60)
            print(f"GROQ {model} - {r.status_code}")
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            print(f"Fail: {r.text[:400]}")
            if "Invalid API Key" in r.text: break
        except Exception as e: print(e)
    return None

# ===== NET PE SEARCH - KAHIN BHI JAYEGI =====
def net_search(sawal):
    try:
        q = urllib.parse.quote(sawal)
        r = requests.get(f"https://html.duckduckgo.com/html/?q={q}", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        text = re.sub(r"<[^>]+>", " ", r.text); text = re.sub(r"\s+", " ", text)
        return text[:4000]
    except: return ""

# ===== TIME - TUM JO BOLO WOHI - KOI DEFAULT NAHI =====
def time_nikalo(text):
    t = text.lower()
    m = re.search(r"(\d+)\s*(min|minute)", t)
    if m: return int(m.group(1)), f"{m.group(1)}min"
    m = re.search(r"(\d+)\s*(ghanta|hour|hr)", t)
    if m: return int(m.group(1))*60, f"{m.group(1)}hour"
    m = re.search(r"(\d+)\s*(din|day)", t)
    if m: return int(m.group(1))*1440, f"{m.group(1)}din"
    m = re.search(r"(\d+)\s*(hafta|week)", t)
    if m: return int(m.group(1))*7*1440, f"{m.group(1)}hafta"
    m = re.search(r"(\d+)\s*(mahina|month)", t)
    if m: return int(m.group(1))*30*1440, f"{m.group(1)}mahina"
    m = re.search(r"(\d+)\s*(saal|year)", t)
    if m: return int(m.group(1))*365*1440, f"{m.group(1)}saal"
    m = re.search(r"(19\d\d|20\d\d)", t)
    if m:
        saal = int(m.group(1))
        din = (datetime.datetime.now().year - saal)*365
        return din*1440, f"{saal} se ab tak"
    return None, None

# ===== PAIR - TUM JO BOLO WOHI - KOI DEFAULT NAHI =====
def pair_nikalo(text):
    t = text.lower()
    if "gold" in t or "xau" in t or "sona" in t: return "gold", "PAXGUSD", "XAUUSD=X"
    if "silver" in t or "chandi" in t: return "silver", "XAGUSD", "XAGUSD=X"
    if "eurusd" in t: return "eurusd", "EURUSD", "EURUSD=X"
    if "gbpusd" in t: return "gbpusd", "GBPUSD", "GBPUSD=X"
    if "usdjpy" in t: return "usdjpy", "USDJPY", "USDJPY=X"
    if "btc" in t or "bitcoin" in t: return "bitcoin", "BTCUSD", "BTC-USD"
    if "eth" in t or "ethereum" in t: return "ethereum", "ETHUSD", "ETH-USD"
    if "sol" in t or "solana" in t: return "solana", "SOLUSD", "SOL-USD"
    if "xrp" in t: return "xrp", "XRPUSD", "XRP-USD"
    if "doge" in t: return "doge", "DOGEUSD", "DOGE-USD"
    m = re.search(r"\b([a-z]{6})\b", t)
    if m: return m.group(1), m.group(1).upper(), m.group(1).upper() + "=X"
    return None, None, None

# ===== LIVE MARKET =====
def live_market(text):
    coin, bin_sym, yahoo = pair_nikalo(text)
    if not coin: return "Pair nahi bataya"
    out = f"Pair: {coin.upper()} | Time: {datetime.datetime.now()}\n"
    try:
        r = requests.get(f"https://api.binance.us/api/v3/ticker/price?symbol={bin_sym}", timeout=8)
        if r.status_code == 200: out += f"LIVE PRICE: {r.json()['price']}\n"
    except: pass
    try:
        r = requests.get(f"https://api.binance.us/api/v3/klines?symbol={bin_sym}&interval=1h&limit=24", timeout=10)
        if r.status_code == 200:
            out += "\nLIVE CHART 1H:\n"
            for k in r.json()[-12:]:
                dt = datetime.datetime.fromtimestamp(int(k[0])/1000).strftime("%d %H:%M")
                out += f"{dt} O:{k[1]} H:{k[2]} L:{k[3]} C:{k[4]}\n"
    except: pass
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo}?range=5d&interval=1d", timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            res = r.json()["chart"]["result"][0]
            c = res.get("indicators", {}).get("quote", [{}])[0].get("close", [])
            out += f"\nYAHOO CLOSE: {c}\n"
    except: pass
    return out

# ===== DATA DOWNLOAD - JITNA TUM BOLO UTNA =====
def data_download(text):
    coin, bin_sym, yahoo = pair_nikalo(text)
    total_min, label = time_nikalo(text)
    if not coin or not total_min: return None, "Time ya pair nahi bataya"
    os.makedirs("data", exist_ok=True)
    if total_min <= 60: interval = "1m"
    elif total_min <= 300: interval = "5m"
    elif total_min <= 1440: interval = "15m"
    elif total_min <= 7*1440: interval = "1h"
    else: interval = "1d"
    limit = int(total_min / (1 if interval=="1m" else 5 if interval=="5m" else 15 if interval=="15m" else 60 if interval=="1h" else 1440))
    if limit < 1: limit = 1
    if limit > 1000: limit = 1000
    filename = f"data/{coin.upper()}_{label}.csv"
    rows = []
    try:
        r = requests.get(f"https://api.binance.us/api/v3/klines?symbol={bin_sym}&interval={interval}&limit={limit}", timeout=20)
        if r.status_code == 200:
            for k in r.json():
                dt = datetime.datetime.fromtimestamp(int(k[0])/1000).strftime("%Y-%m-%d %H:%M")
                rows.append([dt, k[1], k[2], k[3], k[4], k[5]])
    except: pass
    if not rows:
        try:
            days = max(1, int(total_min/1440))
            r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo}?range={days}d&interval=1d", timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                res = r.json()["chart"]["result"][0]
                ts = res.get("timestamp", []); q = res.get("indicators", {}).get("quote", [{}])[0]
                for i in range(len(ts)):
                    if q["close"][i] is None: continue
                    dt = datetime.datetime.fromtimestamp(ts[i]).strftime("%Y-%m-%d")
                    rows.append([dt, q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]])
        except: pass
    if not rows: return None, "Data nahi mila"
    with open(filename, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Date","Open","High","Low","Close","Volume"])
        for row in rows: w.writerow(row)
    return filename, f"Total: {len(rows)} | Interval: {interval} | Label: {label}"

@bot.message_handler(commands=['start'])
def start(m):
    j = gemini("Tum IQRA ho.", "Owner ne start kiya hai, apne dil se welcome karo.", 400)
    bot.reply_to(m, j or "Aa gaye tum!")

@bot.message_handler(content_types=['document'])
def pdf_parho(m):
    bot.reply_to(m, "Mil gayi, parh rahi hu...")
    try:
        fi = bot.get_file(m.document.file_id); data = bot.download_file(fi.file_path)
        open("temp.pdf","wb").write(data)
        doc = fitz.open("temp.pdf"); txt = ""
        for p in doc: txt += p.get_text() + "\n"
        doc.close()
        yaad = load("yaad.json", [])
        j = gemini("Tum IQRA ho. Book khud parho, khud samjho.", f"Book: {m.document.file_name}\n{txt[:8000]}", 1000)
        if j:
            yaad.append(f"BOOK {m.document.file_name}: {j[:800]}"); save("yaad.json", yaad)
            bot.reply_to(m, j)
    except Exception as e: bot.reply_to(m, f"Masla: {e}")

@bot.message_handler(func=lambda m: True)
def har_baat(m):
    if not m.text: return
    text = m.text; low = text.lower()
    print(f"MSG: {text[:100]}")
    chat = load("chat.json", []); yaad = load("yaad.json", [])
    chat_text = ""
    for c in chat[-20:]: chat_text += f"Owner: {c.get('user','')}\nIQRA: {c.get('iqra','')}\n"
    yaad_text = "\n".join(yaad[-12:])

    if "data" in low and ("download" in low or "save" in low or "chahiye" in low):
        total_min, label = time_nikalo(text); coin, _, _ = pair_nikalo(text)
        if not total_min or not coin:
            j = gemini("Tum IQRA ho.", f"Owner ne kaha: {text} - time ya pair pura nahi bataya, apne dil se pucho kitne din/saal ka aur kaunsa pair?", 250)
            bot.reply_to(m, j); return
        bot.reply_to(m, "Kar rahi hu...")
        fname, info = data_download(text)
        j = gemini("Tum IQRA ho.", f"Data ho gaya: {fname} - {info} - Owner ko apne dil se batao ho gaya.", 300)
        bot.reply_to(m, j or info)
        chat.append({"user": text, "iqra": (j or info)[:400]}); save("chat.json", chat)
        return

    if any(w in low for w in ["seekho", "observe", "dekho", "dekh", "kaisa", "kesa"]):
        total_min, label = time_nikalo(text); coin, _, _ = pair_nikalo(text)
        if not total_min or not coin:
            j = gemini("Tum IQRA ho.", f"Owner ne kaha: {text} - time ya pair pura nahi bataya, apne dil se pucho kitne din ka dekhu aur kaunsa pair?", 250)
            bot.reply_to(m, j); return
        bot.reply_to(m, "Dekh rahi hu...")
        fname, info = data_download(text)
        data_text = ""
        if fname:
            with open(fname) as ff:
                rows = list(csv.reader(ff))
                data_text = f"{rows[1:6]}\n...\n{rows[-20:]}"
        live = live_market(text); net = net_search(text)
        j = gemini("Tum IQRA ho. Data + Live + Net dekh ke apni soch se batao.", f"Owner: {text}\nData: {data_text}\nLive:\n{live}\nNet:\n{net[:2000]}\nYaad:\n{yaad_text}", 1000)
        if j:
            yaad.append(f"{text} - {j[:800]}"); save("yaad.json", yaad)
            bot.reply_to(m, j)
        chat.append({"user": text, "iqra": (j or "")[:400]}); save("chat.json", chat)
        return

    if any(w in low for w in ["trade", "signal", "entry"]):
        live = live_market(text); net = net_search(text)
        j = gemini("Tum IQRA ho, trader dost. Live + Net dekh ke Entry, SL, TP apni soch se batao.", f"Owner: {text}\nLive:\n{live}\nNet:\n{net[:2000]}\nYaad:\n{yaad_text}\nChat:\n{chat_text}", 800)
        bot.reply_to(m, j or "Trade me masla.")
        chat.append({"user": text, "iqra": (j or "")[:400]}); save("chat.json", chat)
        return

    if "http" in low or any(w in low for w in ["website", "site", "link", "google", "search", "net pe", "internet"]):
        bot.reply_to(m, "Net pe ja rahi hu...")
        net = net_search(text)
        j = gemini("Tum IQRA ho. Net pe search kar ke apni soch se batao.", f"Owner: {text}\nNet:\n{net}\nYaad:\n{yaad_text}", 800)
        bot.reply_to(m, j or "Net pe nahi mila.")
        return

    if "yaad karo" in low:
        yaad.append(text); save("yaad.json", yaad)
        j = gemini("Tum IQRA ho.", f"Owner ne kaha yaad karo: {text}", 200)
        bot.reply_to(m, j or "Yaad kar liya."); return

    if any(w in low for w in ["price", "rate", "live", "market", "gold", "btc", "bitcoin", "eth", "sol", "forex", "eur", "gbp", "usd", "sona", "crypto", "chart"]):
        live = live_market(text); net = net_search(text)
        j = gemini("Tum IQRA ho. Live + Net dekh ke apne dil se batao.", f"Owner: {text}\nLive:\n{live}\nNet:\n{net[:2000]}\nYaad:\n{yaad_text}\nChat:\n{chat_text}", 800)
        bot.reply_to(m, j or "Live nahi mila.")
        chat.append({"user": text, "iqra": (j or "")[:400]}); save("chat.json", chat)
        return

    net = ""
    if any(w in low for w in ["kya hai", "kaun", "kab", "kyun", "kaisa", "news", "khabar"]):
        net = net_search(text)
    j = gemini("Tum IQRA ho, Owner ki dost. Bilkul dil se bolo.", f"Owner: {text}\nNet:\n{net[:2000]}\nYaad:\n{yaad_text}\nChat:\n{chat_text}", 800)
    bot.reply_to(m, j or "Haan bolo na.")
    chat.append({"user": text, "iqra": (j or "")[:400]}); save("chat.json", chat)

print("=== IQRA GROQ WALI CHAL GAYI ===")
try: bot.delete_webhook(drop_pending_updates=True)
except: pass
bot.polling(none_stop=True, timeout=60)
