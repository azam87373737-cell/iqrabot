import telebot, os, requests, re, threading, time, datetime, csv, json, urllib.parse
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return "OK"
def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_web, daemon=True).start()
try:
    import fitz
except:
    fitz = None

TOKEN = os.environ.get("BOT_TOKEN", "").strip().replace(" ", "").replace("\n", "").replace("\r", "").replace('"', "").replace("'", "")
GROQ_KEY = os.environ.get("GROQ_KEY", "").strip().replace(" ", "").replace("\n", "").replace("\r", "").replace('"', "").replace("'", "")
if not TOKEN or ":" not in TOKEN:
    raise SystemExit("TOKEN GALAT")
bot = telebot.TeleBot(TOKEN)

PAK_SYSTEM = "You are IQRA from Pakistan, Dijkot Punjab. Pakistani dost ho. Roman Urdu + Punjabi mix me baat karo. Words: han, yaar, acha, theek hai, kya haal hai, ki hoya, chal, sun na. Indian words kabhi mat use karo: aap, kripya, avashya, zaroor, batayein. Lambi formal report, ###, table mat banao. Dost jaisa short, dil se baat karo. Jo manga hai wahi do, apni taraf se zyada mat bolo. Live price jo diya hai wahi sach hai, apne mind se price mat banao. Koi example price, koi fixed trade yaad mat karo, har baar live dekh ke naya socho."

def load(n, d):
    try:
        with open(n) as f:
            return json.load(f)
    except:
        return d

def save(n, d):
    try:
        with open(n, "w") as f:
            json.dump(d, f)
    except:
        pass

def save_chat(chat, text, j):
    iqra_text = (j or "")[:800]
    chat.append({"user": text, "iqra": iqra_text, "date": datetime.datetime.now().isoformat()})
    ab = datetime.datetime.now()
    nayi = []
    for c in chat:
        try:
            if "date" in c:
                d = datetime.datetime.fromisoformat(c["date"])
                if (ab - d).days < 3650:
                    nayi.append(c)
            else:
                nayi.append(c)
        except:
            nayi.append(c)
    save("chat.json", nayi)

def mind(system, user, max_tokens=2000):
    if not GROQ_KEY:
        return "GROQ_KEY NAHI HAI"
    for model in ["openai/gpt-oss-120b", "llama-3.1-8b-instant", "openai/gpt-oss-20b"]:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                json={"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "temperature": 0.9, "max_tokens": max_tokens},
                headers={"Authorization": "Bearer " + GROQ_KEY.strip(), "Content-Type": "application/json"}, timeout=90)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            if "Invalid API Key" in r.text:
                return "GROQ KEY GALAT HAI"
        except:
            continue
    return "GROQ SE JAWAB NAHI AAYA"

def net_search(sawal):
    try:
        q = urllib.parse.quote(sawal)
        r = requests.get("https://html.duckduckgo.com/html/?q=" + q, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        text = re.sub(r"<[^>]+>", " ", r.text)
        text = re.sub(r"\s+", " ", text)
        return text[:6000]
    except:
        return ""

def website_parho(text):
    try:
        urls = re.findall(r"https?://[^\s]+", text)
        if not urls:
            return ""
        url = urls[0]
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        txt = re.sub(r"<[^>]+>", " ", r.text)
        txt = re.sub(r"\s+", " ", txt)
        return txt[:8000]
    except:
        return ""

def parse_request(text):
    t = text.lower()
    candle = None
    if "5 min" in t or "5 minute" in t:
        candle = "5m"
    elif "15 min" in t:
        candle = "15m"
    elif "1 hour" in t or "1 ghanta" in t:
        candle = "1h"
    elif "1 din" in t or "1 day" in t:
        candle = "1d"
    total_min = None
    label = ""
    m = re.search(r"(\d+)\s*(saal|year)", t)
    if m:
        total_min = int(m.group(1)) * 365 * 1440
        label = m.group(1) + "saal"
    m = re.search(r"(\d+)\s*(mahina|month)", t)
    if m:
        total_min = int(m.group(1)) * 30 * 1440
        label = m.group(1) + "mahina"
    m = re.search(r"(\d+)\s*(hafta|week)", t)
    if m:
        total_min = int(m.group(1)) * 7 * 1440
        label = m.group(1) + "hafta"
    m = re.search(r"(\d+)\s*(din|day)", t)
    if m:
        total_min = int(m.group(1)) * 1440
        label = m.group(1) + "din"
    m = re.search(r"(19\d\d|20\d\d)", t)
    if m and not total_min:
        saal = int(m.group(1))
        din = (datetime.datetime.now().year - saal) * 365
        total_min = din * 1440
        label = str(saal) + "-se"
    return total_min, label, candle

def pair_nikalo(text):
    t = text.lower()
    if "gold" in t or "xau" in t or "sona" in t:
        return "gold", "PAXGUSD", "XAUUSD=X"
    if "silver" in t or "chandi" in t:
        return "silver", "XAGUSD", "XAGUSD=X"
    if "eurusd" in t:
        return "eurusd", "EURUSD", "EURUSD=X"
    if "gbpusd" in t:
        return "gbpusd", "GBPUSD", "GBPUSD=X"
    if "usdjpy" in t:
        return "usdjpy", "USDJPY", "USDJPY=X"
    if "btc" in t or "bitcoin" in t:
        return "bitcoin", "BTCUSD", "BTC-USD"
    if "eth" in t or "ethereum" in t:
        return "ethereum", "ETHUSD", "ETH-USD"
    if "sol" in t or "solana" in t:
        return "solana", "SOLUSD", "SOL-USD"
    if "xrp" in t:
        return "xrp", "XRPUSD", "XRP-USD"
    if "doge" in t:
        return "doge", "DOGEUSD", "DOGE-USD"
    m = re.search(r"\b([a-z]{6})\b", t)
    if m:
        return m.group(1), m.group(1).upper(), m.group(1).upper() + "=X"
    return None, None, None

def live_market(text):
    coin, bin_sym, yahoo = pair_nikalo(text)
    if not coin:
        return ""
    out = coin + " | " + str(datetime.datetime.now()) + "\n"
    if coin == "gold":
        try:
            r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd", timeout=10)
            if r.status_code == 200:
                out += "LIVE GOLD PAXG: " + str(r.json()["pax-gold"]["usd"]) + " USD\n"
        except:
            pass
        try:
            r = requests.get("https://data-asg.goldprice.org/db_XAU.json", timeout=10)
            if r.status_code == 200:
                out += "LIVE GOLD SPOT: " + str(r.json()["items"][0]["price"]) + " " + str(r.json()["items"][0]["curr"]) + "\n"
        except:
            pass
    try:
        r = requests.get("https://api.binance.us/api/v3/ticker/price?symbol=" + bin_sym, timeout=8)
        if r.status_code == 200:
            out += "BINANCE " + bin_sym + ": " + str(r.json()["price"]) + "\n"
    except:
        pass
    return out

def full_analysis(text):
    coin, bin_sym, yahoo = pair_nikalo(text)
    if not coin:
        return "", ""
    out = "ANALYSIS FOR " + coin.upper() + "\n"
    closes = []
    highs = []
    lows = []
    try:
        r = requests.get("https://api.binance.us/api/v3/klines?symbol=" + bin_sym + "&interval=1h&limit=100", timeout=15)
        if r.status_code == 200:
            data = r.json()
            for k in data:
                closes.append(float(k[4]))
                highs.append(float(k[2]))
                lows.append(float(k[3]))
            out += "1H LAST 20:\n"
            for k in data[-20:]:
                dt = datetime.datetime.fromtimestamp(int(k[0]) / 1000).strftime("%d %H:%M")
                out += dt + " O:" + str(k[1]) + " H:" + str(k[2]) + " L:" + str(k[3]) + " C:" + str(k[4]) + " V:" + str(k[5]) + "\n"
        r2 = requests.get("https://api.binance.us/api/v3/klines?symbol=" + bin_sym + "&interval=15m&limit=50", timeout=15)
        if r2.status_code == 200:
            out += "15M LAST 20:\n"
            for k in r2.json()[-20:]:
                dt = datetime.datetime.fromtimestamp(int(k[0]) / 1000).strftime("%d %H:%M")
                out += dt + " C:" + str(k[4]) + " H:" + str(k[2]) + " L:" + str(k[3]) + "\n"
        r3 = requests.get("https://api.binance.us/api/v3/klines?symbol=" + bin_sym + "&interval=1d&limit=30", timeout=15)
        if r3.status_code == 200:
            out += "1D LAST 15:\n"
            for k in r3.json()[-15:]:
                dt = datetime.datetime.fromtimestamp(int(k[0]) / 1000).strftime("%Y-%m-%d")
                out += dt + " C:" + str(k[4]) + " H:" + str(k[2]) + " L:" + str(k[3]) + "\n"
    except Exception as e:
        out += "ERR " + str(e) + "\n"
    calc = ""
    if len(closes) > 20:
        try:
            gains = 0
            losses = 0
            for i in range(len(closes)-14, len(closes)):
                diff = closes[i] - closes[i-1]
                if diff > 0:
                    gains += diff
                else:
                    losses += -diff
            avg_gain = gains / 14
            avg_loss = losses / 14
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            ma20 = sum(closes[-20:]) / 20
            ma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else ma20
            support = min(lows[-20:])
            resistance = max(highs[-20:])
            last = closes[-1]
            trend = "UP" if last > ma20 > ma50 else "DOWN" if last < ma20 < ma50 else "SIDEWAYS"
            calc = f"LAST: {last} | MA20: {ma20:.2f} | MA50: {ma50:.2f} | RSI14: {rsi:.1f} | SUPPORT: {support} | RESISTANCE: {resistance} | TREND: {trend}"
            out += calc + "\n"
        except Exception as e:
            calc = "CALC ERR " + str(e)
    return out, calc

def data_download(text):
    coin, bin_sym, yahoo = pair_nikalo(text)
    total_min, label, candle = parse_request(text)
    if not coin or not total_min:
        return None, ""
    os.makedirs("data", exist_ok=True)
    if candle:
        interval = candle
        if interval == "5m":
            div = 5
        elif interval == "15m":
            div = 15
        elif interval == "1h":
            div = 60
        else:
            div = 1440
            interval = "1d"
    else:
        if total_min <= 60:
            interval = "1m"
            div = 1
        elif total_min <= 300:
            interval = "5m"
            div = 5
        elif total_min <= 1440:
            interval = "15m"
            div = 15
        elif total_min <= 7 * 1440:
            interval = "1h"
            div = 60
        else:
            interval = "1d"
            div = 1440
    limit = int(total_min / div)
    if limit < 1:
        limit = 1
    if limit > 1000:
        limit = 1000
    filename = "data/" + coin.upper() + "_" + label + "_" + interval + ".csv"
    rows = []
    try:
        r = requests.get("https://api.binance.us/api/v3/klines?symbol=" + bin_sym + "&interval=" + interval + "&limit=" + str(limit), timeout=30)
        if r.status_code == 200:
            for k in r.json():
                dt = datetime.datetime.fromtimestamp(int(k[0]) / 1000).strftime("%Y-%m-%d %H:%M")
                rows.append([dt, k[1], k[2], k[3], k[4], k[5]])
    except:
        pass
    if not rows:
        return None, ""
    with open(filename, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        for row in rows:
            w.writerow(row)
    return filename, str(len(rows)) + " rows | " + interval + " | " + label

def yaad_save(baat):
    yaad = load("yaad.json", [])
    ab = datetime.datetime.now()
    nayi = []
    for y in yaad:
        try:
            if isinstance(y, dict) and "date" in y:
                d = datetime.datetime.fromisoformat(y["date"])
                if (ab - d).days < 3650:
                    nayi.append(y)
            else:
                nayi.append(y)
        except:
            nayi.append(y)
    nayi.append({"date": ab.isoformat(), "baat": baat})
    save("yaad.json", nayi)
    return nayi

def book_save(name, summary, full_text):
    books = load("books.json", [])
    ab = datetime.datetime.now()
    nayi = []
    for b in books:
        try:
            if "date" in b:
                d = datetime.datetime.fromisoformat(b["date"])
                if (ab - d).days < 3650:
                    nayi.append(b)
        except:
            nayi.append(b)
    nayi.append({"date": ab.isoformat(), "name": name, "summary": summary, "text": full_text[:10000]})
    save("books.json", nayi)
    return nayi

def nazar_loop():
    while True:
        try:
            watch = load("watch.json", [])
            for w in watch:
                pair_text = w.get("pair", "")
                owner = w.get("owner", "")
                if not pair_text or not owner:
                    continue
                live = live_market(pair_text)
                j = mind(PAK_SYSTEM, pair_text + " | Live: " + live + " | Agar kuch khas hai to batao, warna sirf OK likho.")
                if j and j.strip().lower() != "ok" and len(j) > 20:
                    try:
                        bot.send_message(owner, j)
                    except:
                        pass
            time.sleep(1800)
        except:
            time.sleep(60)
threading.Thread(target=nazar_loop, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(m):
    j = mind(PAK_SYSTEM, "start")
    if j:
        bot.reply_to(m, j)

@bot.message_handler(content_types=['document'])
def pdf_parho(m):
    try:
        fi = bot.get_file(m.document.file_id)
        data = bot.download_file(fi.file_path)
        open("temp.pdf", "wb").write(data)
        doc = fitz.open("temp.pdf")
        txt = ""
        for p in doc:
            txt += p.get_text() + "\n"
        doc.close()
        j = mind(PAK_SYSTEM, m.document.file_name + "\n" + txt[:12000] + "\nIs book ko hamesha ke liye yaad kar lo, 10 saal tak mat bhulna.")
        if j:
            book_save(m.document.file_name, j, txt)
            yaad_save("BOOK PARHI: " + m.document.file_name + " - " + j[:1000])
            bot.reply_to(m, j)
    except Exception as e:
        j = mind(PAK_SYSTEM, "PDF error: " + str(e))
        if j:
            bot.reply_to(m, j)

@bot.message_handler(func=lambda m: True)
def har_baat(m):
    if not m.text:
        return
    text = m.text
    low = text.lower()
    chat = load("chat.json", [])
    yaad = load("yaad.json", [])
    books = load("books.json", [])
    chat_text = ""
    for c in chat[-30:]:
        chat_text += str(c.get("user", "")) + "\n" + str(c.get("iqra", "")) + "\n"
    yaad_text = ""
    for y in yaad[-20:]:
        if isinstance(y, dict):
            yaad_text += str(y.get("baat", "")) + "\n"
        else:
            yaad_text += str(y) + "\n"
    books_text = ""
    for b in books[-10:]:
        books_text += "BOOK: " + str(b.get("name", "")) + "\n" + str(b.get("summary", ""))[:2000] + "\n"

    if any(w in low for w in ["price", "rate", "kitne ka", "kya price", "live price"]):
        if len(text.split()) <= 8:
            live = live_market(text)
            j = mind(PAK_SYSTEM, text + "\nLive:\n" + live + "\nSirf exact current price do, extra mat bolo.")
            if j:
                bot.reply_to(m, j)
            save_chat(chat, text, j)
            return
        live = live_market(text)
        j = mind(PAK_SYSTEM, text + "\nLive:\n" + live + "\nYaad:\n" + yaad_text)
        if j:
            bot.reply_to(m, j)
        save_chat(chat, text, j)
        return

    if "data" in low and ("download" in low or "save" in low or "chahiye" in low or "nikalo" in low):
        total_min, label, candle = parse_request(text)
        coin, _, _ = pair_nikalo(text)
        if not total_min or not coin:
            j = mind(PAK_SYSTEM, text + "\nYaad:\n" + yaad_text)
            if j:
                bot.reply_to(m, j)
            return
        fname, info = data_download(text)
        j = mind(PAK_SYSTEM, text + "\nFile: " + str(fname) + " Info: " + info)
        if j:
            bot.reply_to(m, j)
        if fname:
            try:
                with open(fname, "rb") as ff:
                    bot.send_document(m.chat.id, ff)
            except:
                pass
        save_chat(chat, text, j)
        return

    # OBSERVE / TRADE - KHUD SOCH KE, INDICATOR JO TUM BOLO GE USI SE
    if any(w in low for w in ["seekho", "observe", "dekho", "dekh", "study", "trade", "signal", "entry", "trade do", "trade de", "analysis"]):
        analysis, calc = full_analysis(text)
        live = live_market(text)
        net = net_search(text + " news today")
        total_min, label, candle = parse_request(text)
        coin, _, _ = pair_nikalo(text)
        data_text = ""
        fname, info = None, ""
        if total_min and coin:
            fname, info = data_download(text)
            if fname:
                with open(fname) as ff:
                    rows = list(csv.reader(ff))
                    data_text = str(rows[1:10]) + "\n...\n" + str(rows[-30:])
        prompt = text + "\nANALYSIS LIVE:\n" + analysis + "\nCALC: " + calc + "\nLive:\n" + live + "\nData: " + data_text + " " + info + "\nNet:\n" + net[:4000] + "\nYaad 10 Saal:\n" + yaad_text + "\nChat:\n" + chat_text + "\nBooks:\n" + books_text + "\nAb khud soch ke, live dekh ke, search kar ke batao. Jo indicator user ne bola hai usi se trade karo, agar koi indicator nahi bola to khud jo sahi lage usi se karo. Trade mangi hai to Entry, SL, TP, Reason do. Observe bola hai to trend, support, resistance batao. Koi purana fixed jawab mat do, har baar naya socho."
        j = mind(PAK_SYSTEM, prompt)
        if j:
            yaad_save(text + " - OBSERVE/TRADE: " + j[:1000])
            bot.reply_to(m, j)
        save_chat(chat, text, j)
        return

    if "nazar rakho" in low or "nazar rakh" in low or "watch" in low:
        watch = load("watch.json", [])
        watch.append({"pair": text, "owner": m.chat.id, "date": datetime.datetime.now().isoformat()})
        save("watch.json", watch)
        j = mind(PAK_SYSTEM, text)
        if j:
            bot.reply_to(m, j)
        return

    if "nazar hata" in low or "nazar mat rakho" in low:
        save("watch.json", [])
        j = mind(PAK_SYSTEM, text)
        if j:
            bot.reply_to(m, j)
        return

    if "http" in low or any(w in low for w in ["website", "site", "link", "google", "search", "net pe", "internet"]):
        net = net_search(text)
        web = website_parho(text)
        j = mind(PAK_SYSTEM, text + "\nNet:\n" + net + "\nWebsite:\n" + web + "\nYaad:\n" + yaad_text + "\nBooks:\n" + books_text)
        if j:
            bot.reply_to(m, j)
        save_chat(chat, text, j)
        return

    if "yaad karo" in low or "book" in low or "parho" in low or "parh" in low:
        yaad_save(text)
        j = mind(PAK_SYSTEM, text + "\nYaad:\n" + yaad_text + "\nBooks:\n" + books_text)
        if j:
            bot.reply_to(m, j)
        save_chat(chat, text, j)
        return

    if any(w in low for w in ["live", "market", "gold", "btc", "bitcoin", "eth", "sol", "forex", "eur", "gbp", "usd", "sona", "crypto", "chart", "pair"]):
        live = live_market(text)
        net = net_search(text)
        j = mind(PAK_SYSTEM, text + "\nLive:\n" + live + "\nNet:\n" + net[:3000] + "\nYaad:\n" + yaad_text + "\nBooks:\n" + books_text)
        if j:
            bot.reply_to(m, j)
        save_chat(chat, text, j)
        return

    net = ""
    if any(w in low for w in ["kya hai", "kaun", "kab", "kyun", "news", "khabar"]):
        net = net_search(text)
    web = website_parho(text)
    j = mind(PAK_SYSTEM, text + "\nNet:\n" + net[:2000] + "\nWebsite:\n" + web[:2000] + "\nYaad 10 Saal:\n" + yaad_text + "\nChat:\n" + chat_text + "\nBooks 10 Saal - Kabhi Mat Bhulna:\n" + books_text)
    if j:
        bot.reply_to(m, j)
    save_chat(chat, text, j)

print("BOT START HO GAYA", flush=True)
try:
    bot.delete_webhook(drop_pending_updates=True)
except Exception as e:
    print("WEBHOOK ERR " + str(e), flush=True)
bot.polling(none_stop=True, timeout=60)
