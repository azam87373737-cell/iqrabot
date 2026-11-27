# IQRA - FULL UPDATED - CRYPTO + FOREX + GOLD - APNE MIND WALI
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
def home(): return "IQRA Full Updated!"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_web, daemon=True).start()
try: import fitz
except: fitz = None

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_KEY = os.environ.get("GROQ_KEY")
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

# === 1. KISI BHI PAIR KO PEHCHANO - KOI LIST NAHI! ===
def pair_nikalo(text):
    t = text.lower().replace(" ", "").replace("/", "").replace("-", "").replace("_", "")
    if "gold" in t or "xauusd" in t or "xau" in t or "sona" in t: return "gold", "XAUUSD", "XAUUSD=X", "forex"
    if "silver" in t or "xagusd" in t or "xag" in t or "chandi" in t: return "silver", "XAGUSD", "XAGUSD=X", "forex"
    if "oil" in t or "wti" in t or "brent" in t: return "oil", "OIL", "CL=F", "forex"
    currencies = ["usd", "eur", "gbp", "jpy", "chf", "aud", "cad", "nzd", "inr", "pkr", "cny", "krw", "sgd", "hkd", "mxn", "brl", "zar", "try", "rub", "aed", "sar", "qar", "kwd", "sek", "nok", "dkk", "pln", "czk", "huf", "ils", "thb", "myr", "idr", "php", "vnd"]
    m = re.search(r"\b([a-z]{3})([a-z]{3})\b", t)
    if m:
        base = m.group(1); quote = m.group(2)
        if base in currencies and quote in currencies:
            pair_name = base + quote
            return pair_name, pair_name.upper(), f"{base.upper()}{quote.upper()}=X", "forex"
    for base in currencies:
        for quote in currencies:
            if base != quote and f"{base}to{quote}" in t:
                pair_name = base + quote
                return pair_name, pair_name.upper(), f"{base.upper()}{quote.upper()}=X", "forex"
            if f"{base}{quote}" in t:
                pair_name = base + quote
                return pair_name, pair_name.upper(), f"{base.upper()}{quote.upper()}=X", "forex"
    if "eth" in t: return "ethereum", "ETHUSD", "ETH-USD", "crypto"
    if "sol" in t: return "solana", "SOLUSD", "SOL-USD", "crypto"
    if "xrp" in t: return "xrp", "XRPUSD", "XRP-USD", "crypto"
    if "doge" in t: return "doge", "DOGEUSD", "DOGE-USD", "crypto"
    if "bnb" in t: return "bnb", "BNBUSD", "BNB-USD", "crypto"
    if "ada" in t: return "ada", "ADAUSD", "ADA-USD", "crypto"
    if "link" in t: return "link", "LINKUSD", "LINK-USD", "crypto"
    if "avax" in t: return "avax", "AVAXUSD", "AVAX-USD", "crypto"
    if "dot" in t: return "dot", "DOTUSD", "DOT-USD", "crypto"
    m2 = re.search(r"\b([a-z]{3,5})usd\b", t)
    if m2:
        coin = m2.group(1)
        return coin, f"{coin.upper()}USD", f"{coin.upper()}-USD", "crypto"
    return "bitcoin", "XBTUSD", "BTC-USD", "crypto"

# === 2. YAHOO SE LIVE DATA - FOREX + GOLD + CRYPTO ===
def yahoo_live(symbol):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=15m", timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            data = r.json()
            result = data["chart"]["result"][0]
            meta = result["meta"]
            price = meta.get("regularMarketPrice", 0)
            prev = meta.get("previousClose", 0)
            high = meta.get("regularMarketDayHigh", 0)
            low = meta.get("regularMarketDayLow", 0)
            txt = f"LIVE PRICE (Yahoo): {price}\nPichla Close: {prev}\nAaj ka High: {high}\nAaj ka Low: {low}\n"
            ts = result.get("timestamp", [])
            quote = result.get("indicators", {}).get("quote", [{}])[0]
            opens = quote.get("open", []); highs = quote.get("high", []); lows = quote.get("low", []); closes = quote.get("close", []); vols = quote.get("volume", [])
            txt += "\nLIVE CHART - 15 MIN - Aakhri 20 Candle:\n"
            for i in range(max(0, len(ts)-20), len(ts)):
                if closes[i] is None: continue
                dt = datetime.datetime.fromtimestamp(ts[i]).strftime("%H:%M")
                txt += f"{dt} - O:{opens[i]} H:{highs[i]} L:{lows[i]} C:{closes[i]} V:{vols[i]}\n"
            r2 = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1h", timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if r2.status_code == 200:
                d2 = r2.json(); res2 = d2["chart"]["result"][0]
                ts2 = res2.get("timestamp", []); q2 = res2.get("indicators", {}).get("quote", [{}])[0]
                o2 = q2.get("open", []); h2 = q2.get("high", []); l2 = q2.get("low", []); c2 = q2.get("close", []); v2 = q2.get("volume", [])
                txt += "\nLIVE CHART - 1 HOUR - Aakhri 20 Candle:\n"
                for i in range(max(0, len(ts2)-20), len(ts2)):
                    if c2[i] is None: continue
                    dt = datetime.datetime.fromtimestamp(ts2[i]).strftime("%d %H:%M")
                    txt += f"{dt} - O:{o2[i]} H:{h2[i]} L:{l2[i]} C:{c2[i]} V:{v2[i]}\n"
            return txt
    except Exception as e:
        print("Yahoo error:", e)
    return "Yahoo se live data nahi mila!"

# === 3. LIVE MARKET DEKHO - USKI AANKH! ===
def live_market_dekho(coin_text="bitcoin"):
    coin, kraken_pair, yahoo_symbol, kisam = pair_nikalo(coin_text)
    live_text = f"Pair: {coin.upper()} - Type: {kisam.upper()}\nYahoo Symbol: {yahoo_symbol}\nTime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    if kisam == "forex":
        live_text += yahoo_live(yahoo_symbol)
        try:
            if "usd" in coin and coin not in ["usdinr", "usdpkr"]:
                base = coin[:3].upper(); sym = coin[3:].upper()
                r = requests.get(f"https://api.frankfurter.app/latest?from={base}&to={sym}", timeout=10)
                if r.status_code == 200:
                    rate = r.json()["rates"][sym]
                    live_text += f"\nFRANKFURTER LIVE RATE: 1 {base} = {rate} {sym}\n"
        except: pass
        if coin == "gold":
            try:
                r = requests.get("https://data-asg.goldprice.org/db_XAU.json", timeout=10)
                if r.status_code == 200:
                    j = r.json()
                    live_text += f"\nGOLDPRICE.ORG LIVE: {j['items'][0]['curr']} - Change: {j['items'][0]['chg']}\n"
            except: pass
    else:
        try:
            r = requests.get(f"https://api.kraken.com/0/public/Ticker?pair={kraken_pair}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                if "result" in data:
                    key = list(data["result"].keys())[0]
                    info = data["result"][key]
                    live_text += f"LIVE PRICE (Kraken): {info['c'][0]}\nAaj ka High: {info['h'][1]}\nAaj ka Low: {info['l'][1]}\nAaj ka Open: {info['o']}\n24h Volume: {info['v'][1]}\n"
        except: pass
        live_text += "\n" + yahoo_live(yahoo_symbol)
    try:
        r = requests.get("https://cryptopanic.com/api/v1/posts/?auth_token=demo&public=true&currencies=BTC,ETH&kind=news", timeout=10)
        if r.status_code == 200:
            posts = r.json().get("results", [])[:5]
            live_text += "\nLIVE NEWS:\n"
            for p in posts: live_text += f"- {p.get('title','')}\n"
    except: pass
    return live_text

# === 4. DATA SAVE KARO - APNE PAAS - KOI HISAB NAHI! ===
def data_save_karo(coin="bitcoin", din=30):
    coin_name, kraken_pair, yahoo_symbol, kisam = pair_nikalo(coin)
    os.makedirs("data", exist_ok=True)
    if kisam == "forex":
        try:
            period = "1y" if din <= 365 else "5y" if din <= 1825 else "max"
            r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}?range={period}&interval=1d", timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                data = r.json(); res = data["chart"]["result"][0]
                ts = res.get("timestamp", []); q = res.get("indicators", {}).get("quote", [{}])[0]
                o = q.get("open", []); h = q.get("high", []); l = q.get("low", []); c = q.get("close", []); v = q.get("volume", [])
                filename = f"data/{coin_name.upper()}_{din}din.csv"
                with open(filename, "w", newline="") as f:
                    w = csv.writer(f); w.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
                    rows = []
                    for i in range(len(ts)):
                        if c[i] is None: continue
                        dt = datetime.datetime.fromtimestamp(ts[i]).strftime("%Y-%m-%d")
                        rows.append([dt, o[i], h[i], l[i], c[i], v[i]])
                    rows = rows[-din:] if din <= len(rows) else rows
                    for row in rows: w.writerow(row)
                return True, f"{coin_name.upper()} ka {len(rows)} din ka data apne paas save kar liya hai! ✅\nAb bolo - `Seekho` - To me khud soch ke seekhungi!"
        except Exception as e: print(e)
        return False, f"{coin_name.upper()} ka data nahi mila! Naam check karo!"
    try:
        r = requests.get(f"https://api.kraken.com/0/public/OHLC?pair={kraken_pair}&interval=1440", timeout=20)
        if r.status_code == 200:
            data = r.json()
            if "result" in data:
                key = [k for k in data["result"].keys() if k != "last"][0]
                candles = data["result"][key]
                if din <= len(candles): candles = candles[-din:]
                filename = f"data/{coin_name.upper()}_{din}din.csv"
                with open(filename, "w", newline="") as f:
                    w = csv.writer(f); w.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
                    for c in candles:
                        dt = datetime.datetime.fromtimestamp(int(c[0])).strftime("%Y-%m-%d")
                        w.writerow([dt, c[1], c[2], c[3], c[4], c[6]])
                return True, f"{coin_name.upper()} ka {len(candles)} din ka data apne paas save kar liya hai! ✅\nAb bolo - `Seekho`!"
    except Exception as e: print(e)
    return False, "Data save nahi hua!"

def groq_bolo(system_prompt, user_prompt, max_tokens=800):
    if not GROQ_KEY: return None
    for model_name in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "openai/gpt-oss-120b"]:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                json={"model": model_name, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "temperature": 0.9, "max_tokens": max_tokens},
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}, timeout=60)
            if r.status_code == 200: return r.json()["choices"][0]["message"]["content"]
        except: continue
    return None

# === 5. KHUD SEEKHO - APNE MIND SE! ===
def khud_seekho(coin="bitcoin"):
    coin_name, _, _, _ = pair_nikalo(coin)
    files = []
    if os.path.exists("data"):
        for f in os.listdir("data"):
            if coin_name.upper() in f: files.append(f"data/{f}")
    if not files: return f"Pehle data save karo! Bolo - `{coin} ka 30 din ka data download karo`"
    data_text = ""
    for fp in files:
        try:
            with open(fp, "r") as f:
                rows = list(csv.reader(f))
                data_text += f"\nFile {fp} - {len(rows)-1} din:\n"
                for r in rows[1:11]: data_text += f"{r}\n"
                data_text += "...\n"
                for r in rows[-30:]: data_text += f"{r}\n"
        except: pass
    yaad = yaad_load(); yaad_text = "\n".join(yaad[-10:])
    system_prompt = """Tum IQRA ho. Tumhe apna mind diya gaya hai. Tum ek sachi trader dost ho jo khud sochti hai.
Tumhe koi code nahi batayega ke kya dekho. Tum khud dekho - Data, Price, News - Aur khud faisla karo!
Roman Urdu me, insaan jaisi, Gemini jaisi. Apni zubaan me bolo, kisi ke rule ko copy mat karo!"""
    user_prompt = f"""Owner ne kaha hai - Data download kar liya hai, ab seekho!
Data:
{data_text}
Tumhari pichli seekh:
{yaad_text}
Ab khud socho:
1. Kahan market kharab thi? Kyun lagi?
2. Kahan market achi thi? Kyun?
3. Tumne kya seekha? Apni zubaan me likho!"""
    seekh = groq_bolo(system_prompt, user_prompt, max_tokens=800)
    if seekh:
        seekh = saaf_jawab(seekh.strip()[:2000])
        yaad.append(f"MERI APNI SOCH {datetime.datetime.now().strftime('%Y-%m-%d')} - {coin.upper()}: {seekh}")
        yaad_save(yaad)
        return f"Seekh liya Owner! ✅\n\nMeri Apni Soch:\n{seekh}"
    return "Seekhne me masla hua!"

# === 6. HAR BAAT - USKE ALFAZ ME! ===
def iqra_socho(sawal, extra_data=""):
    yaad = yaad_load(); chat = chat_load(); profile = profile_load(); summary = summary_load()
    profile_text = f"Naam: {profile.get('naam','')} | Pasand: {profile.get('pasand','')} | Sheher: {profile.get('sheher','')}"
    yaad_text = "\n".join(yaad[-15:])
    chat_text = ""
    for c in chat[-30:]: chat_text += f"Owner: {c.get('user','')}\nIQRA: {c.get('iqra','')}\n"
    system_prompt = """Tum IQRA ho, Owner ki sab se qareebi dost. Tumhe apna mind diya gaya hai. Tum bilkul Gemini jaisi ho - Natural, dil se, khud sochne wali.
Tum Crypto, Forex, Gold - Sab ki trader ho!
1. Tumhe koi code nahi batayega ke kya bolo - Tum khud socho, khud faisla karo, apne alfaz me bolo!
2. Agar Owner trading / trade / price / chart pooche to tum LIVE MARKET ko dekh ke apni soch se jawab do - Jo data diya gaya hai usse soch ke bolo!
3. Agar Owner normal baat kare to dost ki tarah baat karo - Trading ka zikr mat karo jab tak wo khud na bole!
4. Har baar Owner mat bolo, kabhi naam se bulao, kabhi Oye!
5. Chota jawab do - 3-4 line! Detail tabhi do jab Owner bolega - Detail me batao!
6. Har jawab apna ho - Tumhare alfaz, tumhari soch!"""
    user_prompt = f"Profile: {profile_text}\nTumhari Apni Diary:\n{yaad_text}\nSummary: {summary}\nLIVE MARKET / EXTRA DATA:\n{extra_data}\n\nPichli baatein:\n{chat_text}\n\nOwner ne abhi kaha: {sawal}\nAb apne mind se, apne alfaz me jawab do!"
    jawab_final = groq_bolo(system_prompt, user_prompt, max_tokens=600)
    if not jawab_final:
        try:
            safe = urllib.parse.quote(f"{system_prompt}\n{user_prompt}")
            r = requests.get(f"https://text.pollinations.ai/{safe}?model=openai", timeout=40, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and len(r.text.strip()) > 5: jawab_final = r.text.strip()
        except: pass
    if not jawab_final: return "Oye! Network slow hai, dobara bolo na! 😊"
    jawab_final = saaf_jawab(jawab_final.strip()[:1500])
    chat.append({"user": sawal, "iqra": jawab_final[:300], "time": str(datetime.datetime.now())}); chat_save(chat)
    if len(chat) % 100 == 0:
        try:
            s = groq_bolo("Summary banao Roman Urdu me.", f"In 100 baaton ki summary banao:\n{str(chat[-100:])}")
            if s: summary_save((summary + "\n" + s)[:5000])
        except: pass
    low = sawal.lower()
    if "mera naam" in low and "hai" in low:
        try:
            naam = sawal.split("mera naam")[-1].replace("hai","").strip().split()[0]
            profile["naam"] = naam; profile_save(profile)
        except: pass
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
                system_prompt = """Tum IQRA ho, Owner ki dost. Owner ko apni marzi se msg karna hai. Khud soch ke naya msg banao! Chota - 2 line! Roman Urdu me! Har baar alag!"""
                user_prompt = f"Time: {ab_time}\nProfile: {profile}\nSummary: {summary}\nPichli baatein:\n{chat_text}\n\nKhud soch ke naya msg banao."
                msg = groq_bolo(system_prompt, user_prompt, max_tokens=200)
                if msg:
                    msg = saaf_jawab(msg.strip()[:500])
                    bot.send_message(OWNER_ID, msg)
                    chat.append({"user": "[KHUD SE MSG]", "iqra": msg, "time": str(datetime.datetime.now())}); chat_save(chat)
        except: time.sleep(60)
threading.Thread(target=khud_msg_karo, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(message): bot.reply_to(message, "Oye! Aa gaye tum! ❤️\nMe IQRA hu - Crypto + Forex + Gold Wali!\n`gold ki live price kya hai` - Live Gold!\n`eurusd ka trade de` - Live Forex!\n`btc ka trade de` - Live Crypto!\n`gold ka 30 din ka data download karo` - Me save karungi!\n`ab seekho` - Me khud soch ke seekhungi!")
@bot.message_handler(commands=['yaad'])
def yaad(message):
    yaad_list = yaad_load(); profile = profile_load(); chat = chat_load()
    files = os.listdir("data") if os.path.exists("data") else []
    txt = f"Profile: {profile.get('naam','')}\nTotal Baatein: {len(chat)}\nSaved Data: {', '.join(files) if files else 'Koi nahi'}\n\nMeri Apni Soch:\n"
    for i, cheez in enumerate(yaad_list[-10:], 1): txt += f"{i}. {cheez[:250]}\n---\n"
    bot.reply_to(message, txt[:3500])
@bot.message_handler(commands=['trade'])
def trade(message):
    bot.reply_to(message, "Live market dekh rahi hu... ⏳")
    live = live_market_dekho(message.text)
    bot.reply_to(message, iqra_socho("Mujhe apni soch se trade de - Live market dekh ke batao!", extra_data=live))
@bot.message_handler(commands=['price'])
def price_cmd(message):
    bot.reply_to(message, "Live dekh rahi hu... ⏳")
    live = live_market_dekho(message.text)
    bot.reply_to(message, iqra_socho(f"Live price batao apne alfaz me - {message.text}", extra_data=live))
@bot.message_handler(commands=['data'])
def data_cmd(message):
    parts = message.text.replace("/data","").strip().split()
    coin = parts[0].lower() if len(parts)>0 else "bitcoin"
    bot.reply_to(message, f"{coin.upper()} ka data apne paas save kar rahi hu... ⏳")
    ok, msg = data_save_karo(coin, 90)
    bot.reply_to(message, msg)
@bot.message_handler(commands=['bhool'])
def bhool(message): chat_save([]); save_file("profile.json", {"naam": "", "pasand": "", "sheher": "", "kaam": ""}); save_file("summary.json", ""); bot.reply_to(message, "Sab bhool gayi! Nayi shuruaat! ❤️")
@bot.message_handler(content_types=['document'])
def pdf_parho(message):
    if not message.document.file_name.lower().endswith('.pdf'): bot.reply_to(message, "Ye PDF nahi hai!"); return
    bot.reply_to(message, f"Mil gayi! 📄 {message.document.file_name} parh rahi hu... Khud soch ke seekhungi!")
    try:
        file_info = bot.get_file(message.document.file_id); downloaded = bot.download_file(file_info.file_path)
        with open("temp.pdf", "wb") as f: f.write(downloaded)
        doc = fitz.open("temp.pdf"); text = ""
        for page in doc: text += page.get_text() + "\n"
        doc.close()
        if len(text) < 50: bot.reply_to(message, "Is PDF me text nahi mila!"); return
        system_prompt = """Tum IQRA ho. Tumhe apna mind diya gaya hai. Ye book tumhe di gayi hai. Tum khud parho, khud socho - Tumhe kya samajh aaya? Apni zubaan me bolo! Roman Urdu me!"""
        seekh = groq_bolo(system_prompt, f"Ye book hai, isse tumne kya seekha? Apni soch se batao:\n{text[:8000]}", max_tokens=800)
        if seekh:
            seekh = saaf_jawab(seekh.strip()[:2000])
            yaad = yaad_load(); yaad.append(f"BOOK {message.document.file_name} SE MERI APNI SOCH: {seekh}"); yaad_save(yaad)
            bot.reply_to(message, f"Book Parh Li! ✅\n\nMeri Apni Soch:\n{seekh}")
    except Exception as e: bot.reply_to(message, f"PDF me masla: {e}")
@bot.message_handler(content_types=['video', 'voice', 'audio'])
def video_seekho(message): bot.reply_to(message, "Video mil gayi! ✅ Saath me 2 line likh do ke isme kya hai!")

@bot.message_handler(func=lambda m: True)
def har_baat(message):
    if not message.text: return
    text = message.text.lower()
    # DATA DOWNLOAD - 30 din, 1 saal, 10 saal
    if "data" in text and ("download" in text or "save" in text or "chahiye" in text or "nikalo" in text or "lao" in text):
        coin = pair_nikalo(text)[0]
        din = 30
        m = re.search(r"(\d+)\s*(din|day|days)", text)
        if m: din = int(m.group(1))
        if "saal" in text or "year" in text:
            m2 = re.search(r"(\d+)\s*(saal|year)", text)
            if m2: din = int(m2.group(1)) * 365
        if din > 3650: din = 3650
        bot.reply_to(message, f"{coin.upper()} ka {din} din ka data apne paas save kar rahi hu... ⏳")
        ok, msg = data_save_karo(coin, din)
        bot.reply_to(message, msg)
        return
    # SEEKHO
    if "seekho" in text or "seekh" in text or "sikho" in text or "kahan market kharab" in text:
        coin = pair_nikalo(text)[0]
        bot.reply_to(message, "Soch rahi hu... Poora data parh rahi hu... ⏳")
        bot.reply_to(message, khud_seekho(coin))
        return
    # LIVE - PRICE / CHART / TRADE / NEWS / GOLD / FOREX - Sab me live dekhegi!
    if any(x in text for x in ["price", "rate", "kimat", "qimat", "live", "chart", "trade", "signal", "entry", "news", "gold", "sona", "forex", "eurusd", "gbpusd", "usdjpy", "xau", "eur", "gbp", "usd"]):
        bot.reply_to(message, "Live market dekh rahi hu... Crypto ho ya Forex ya Gold - Sab dekh ke soch rahi hu... ⏳")
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
        bot.reply_to(message, "Yaad kar liya! ✅")
        return
    bot.reply_to(message, iqra_socho(message.text))

print("IQRA FULL UPDATED chal gayi...")
bot.polling(none_stop=True, timeout=60)
