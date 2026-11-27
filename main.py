import telebot, os, requests, re, threading, time, datetime, csv, json, urllib.parse
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home(): return "OK"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_web, daemon=True).start()
try: import fitz
except: fitz = None
TOKEN = os.environ.get("BOT_TOKEN", "").strip().replace(" ", "").replace("\n", "").replace("\r", "").replace('"', "").replace("'", "")
GROQ_KEY = os.environ.get("GROQ_KEY", "").strip().replace(" ", "").replace("\n", "").replace("\r", "").replace('"', "").replace("'", "")
print(f"TOKEN LEN: {len(TOKEN)} GROQ LEN: {len(GROQ_KEY)}", flush=True)
if not TOKEN or ":" not in TOKEN:
    print("TOKEN GALAT", flush=True)
    raise SystemExit("TOKEN GALAT")
bot = telebot.TeleBot(TOKEN)
def load(n, d):
    try:
        with open(n) as f: return json.load(f)
    except: return d
def save(n, d):
    try:
        with open(n, "w") as f: json.dump(d, f)
    except: pass

def mind(system, user, max_tokens=1000):
    if not GROQ_KEY:
        print("GROQ_KEY NAHI HAI", flush=True)
        return "GROQ_KEY NAHI HAI"
    for model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                json={"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "temperature": 0.9, "max_tokens": max_tokens},
                headers={"Authorization": f"Bearer {GROQ_KEY.strip()}", "Content-Type": "application/json"}, timeout=60)
            print(f"GROQ {model} {r.status_code} {r.text[:300]}", flush=True)
            if r.status_code == 200: return r.json()["choices"][0]["message"]["content"]
            if "Invalid API Key" in r.text: return "GROQ KEY GALAT HAI"
        except Exception as e:
            print(f"GROQ ERR {e}", flush=True)
            continue
    return "GROQ SE JAWAB NAHI AAYA"

def net_search(sawal):
    try:
        q = urllib.parse.quote(sawal)
        r = requests.get(f"https://html.duckduckgo.com/html/?q={q}", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        text = re.sub(r"<[^>]+>", " ", r.text); text = re.sub(r"\s+", " ", text)
        return text[:4000]
    except: return ""

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
        return din*1440, f"{saal}"
    return None, None

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

def live_market(text):
    coin, bin_sym, yahoo = pair_nikalo(text)
    if not coin: return ""
    out = f"{coin} | {datetime.datetime.now()}\n"
    try:
        r = requests.get(f"https://api.binance.us/api/v3/ticker/price?symbol={bin_sym}", timeout=8)
        if r.status_code == 200: out += f"{r.json()['price']}\n"
    except: pass
    try:
        r = requests.get(f"https://api.binance.us/api/v3/klines?symbol={bin_sym}&interval=1h&limit=24", timeout=10)
        if r.status_code == 200:
            for k in r.json()[-12:]:
                dt = datetime.datetime.fromtimestamp(int(k[0])/1000).strftime("%d %H:%M")
                out += f"{dt} O:{k[1]} H:{k[2]} L:{k[3]} C:{k[4]}\n"
    except: pass
    return out

def data_download(text):
    coin, bin_sym, yahoo = pair_nikalo(text)
    total_min, label = time_nikalo(text)
    if not coin or not total_min: return None, ""
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
    if not rows: return None, ""
    with open(filename, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Date","Open","High","Low","Close","Volume"])
        for row in rows: w.writerow(row)
    return filename, f"{len(rows)} | {interval} | {label}"

def yaad_save(baat):
    yaad = load("yaad.json", [])
    ab = datetime.datetime.now()
    nayi = []
    for y in yaad:
        try:
            if isinstance(y, dict) and "date" in y:
                d = datetime.datetime.fromisoformat(y["date"])
                if (ab - d).days < 1825: nayi.append(y)
            else: nayi.append(y)
        except: nayi.append(y)
    nayi.append({"date": ab.isoformat(), "baat": baat})
    save("yaad.json", nayi)
    return nayi

def nazar_loop():
    while True:
        try:
            watch = load("watch.json", [])
            for w in watch:
                pair_text = w.get("pair", ""); owner = w.get("owner", "")
                if not pair_text or not owner: continue
                live = live_market(pair_text)
                j = mind("You are IQRA.", f"{pair_text} | Live: {live} | Agar kuch khas hai to batao, warna sirf OK likho.")
                if j and j.strip().lower() != "ok" and len(j) > 20:
                    try: bot.send_message(owner, j)
                    except: pass
            time.sleep(1800)
        except: time.sleep(60)
threading.Thread(target=nazar_loop, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(m):
    print(f"START AAYA {m.chat.id} {m.text}", flush=True)
    bot.reply_to(m, "HAAN OWNER BOL - ME ZINDA HU")
    j = mind("You are IQRA.", "start")
    if j and "HAAN OWNER" not in j: bot.send_message(m.chat.id, j)

@bot.message_handler(content_types=['document'])
def pdf_parho(m):
    print(f"PDF AAYA {m.document.file_name}", flush=True)
    bot.reply_to(m, "PDF MIL GAYI - PARH RAHI HU")
    try:
        fi = bot.get_file(m.document.file_id); data = bot.download_file(fi.file_path)
        open("temp.pdf","wb").write(data)
        doc = fitz.open("temp.pdf"); txt = ""
        for p in doc: txt += p.get_text() + "\n"
        doc.close()
        j = mind("You are IQRA.", f"{m.document.file_name}\n{txt[:8000]}")
        if j:
            yaad_save(f"{m.document.file_name}: {j[:800]}")
            bot.reply_to(m, j)
    except Exception as e: print(f"PDF ERR {e}", flush=True)

@bot.message_handler(func=lambda m: True)
def har_baat(m):
    if not m.text: return
    text = m.text; low = text.lower()
    print(f"MSG AAYA: {text} FROM {m.chat.id}", flush=True)
    # TEST - SAB SE PEHLE - GROQ KE BINA
    if low.strip() in ["hi", "hello", "hii", "hey", "salam", "test", "ping", "123", "12345"]:
        bot.reply_to(m, "HAAN OWNER BOL - ME ZINDA HU - TEST PASS HO GAYA")
        return
    chat = load("chat.json", []); yaad = load("yaad.json", [])
    chat_text = ""
    for c in chat[-20:]: chat_text += f"{c.get('user','')}\n{c.get('iqra','')}\n"
    yaad_text = ""
    for y in yaad[-12:]:
        if isinstance(y, dict): yaad_text += f"{y.get('baat','')}\n"
        else: yaad_text += f"{y}\n"
    if "data" in low and ("download" in low or "save" in low or "chahiye" in low):
        total_min, label = time_nikalo(text); coin, _, _ = pair_nikalo(text)
        if not total_min or not coin:
            j = mind("You are IQRA.", f"{text}")
            if j: bot.reply_to(m, j)
            return
        fname, info = data_download(text)
        j = mind("You are IQRA.", f"{text}\n{fname} - {info}")
        if j: bot.reply_to(m, j)
        chat.append({"user": text, "iqra": (j or "")[:400]}); save("chat.json", chat)
        return
    if any(w in low for w in ["seekho", "observe", "dekho", "dekh", "kaisa", "kesa"]):
        total_min, label = time_nikalo(text); coin, _, _ = pair_nikalo(text)
        if not total_min or not coin:
            j = mind("You are IQRA.", f"{text}")
            if j: bot.reply_to(m, j)
            return
        fname, info = data_download(text)
        data_text = ""
        if fname:
            with open(fname) as ff:
                rows = list(csv.reader(ff))
                data_text = f"{rows[1:6]}\n{rows[-20:]}"
        live = live_market(text); net = net_search(text)
        j = mind("You are IQRA.", f"{text}\nData: {data_text}\nLive:\n{live}\nNet:\n{net[:2000]}\nYaad:\n{yaad_text}")
        if j:
            yaad_save(f"{text} - {j[:800]}")
            bot.reply_to(m, j)
        chat.append({"user": text, "iqra": (j or "")[:400]}); save("chat.json", chat)
        return
    if any(w in low for w in ["trade", "signal", "entry"]):
        live = live_market(text); net = net_search(text)
        j = mind("You are IQRA.", f"{text}\nLive:\n{live}\nNet:\n{net[:2000]}\nYaad:\n{yaad_text}\nChat:\n{chat_text}")
        if j: bot.reply_to(m, j)
        chat.append({"user": text, "iqra": (j or "")[:400]}); save("chat.json", chat)
        return
    if "nazar rakho" in low or "nazar rakh" in low or "watch" in low:
        watch = load("watch.json", [])
        watch.append({"pair": text, "owner": m.chat.id, "date": datetime.datetime.now().isoformat()})
        save("watch.json", watch)
        j = mind("You are IQRA.", f"{text}")
        if j: bot.reply_to(m, j)
        return
    if "nazar hata" in low or "nazar mat rakho" in low:
        save("watch.json", [])
        j = mind("You are IQRA.", f"{text}")
        if j: bot.reply_to(m, j)
        return
    if "http" in low or any(w in low for w in ["website", "site", "link", "google", "search", "net pe", "internet"]):
        net = net_search(text)
        j = mind("You are IQRA.", f"{text}\nNet:\n{net}\nYaad:\n{yaad_text}")
        if j: bot.reply_to(m, j)
        return
    if "yaad karo" in low:
        yaad_save(text)
        j = mind("You are IQRA.", f"{text}")
        if j: bot.reply_to(m, j)
        return
    if any(w in low for w in ["price", "rate", "live", "market", "gold", "btc", "bitcoin", "eth", "sol", "forex", "eur", "gbp", "usd", "sona", "crypto", "chart"]):
        live = live_market(text); net = net_search(text)
        j = mind("You are IQRA.", f"{text}\nLive:\n{live}\nNet:\n{net[:2000]}\nYaad:\n{yaad_text}\nChat:\n{chat_text}")
        if j: bot.reply_to(m, j)
        chat.append({"user": text, "iqra": (j or "")[:400]}); save("chat.json", chat)
        return
    net = ""
    if any(w in low for w in ["kya hai", "kaun", "kab", "kyun", "kaisa", "news", "khabar"]):
        net = net_search(text)
    j = mind("You are IQRA.", f"{text}\nNet:\n{net[:2000]}\nYaad:\n{yaad_text}\nChat:\n{chat_text}")
    if j: bot.reply_to(m, j)
    else: bot.reply_to(m, "GROQ SE JAWAB NAHI AAYA - DOBARA BOLO")
    chat.append({"user": text, "iqra": (j or "")[:400]}); save("chat.json", chat)

print("BOT START HO GAYA", flush=True)
try: bot.delete_webhook(drop_pending_updates=True)
except Exception as e: print(f"WEBHOOK ERR {e}", flush=True)
bot.polling(none_stop=True, timeout=60)s
