# IQRA - DOST + TEACHER + KHUD MSG WALI
import telebot
import os
import requests
import json
import re
import threading
import time
import urllib.parse
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "IQRA Dost is Alive!"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_web, daemon=True).start()

try:
    import fitz
except:
    fitz = None

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_KEY = os.environ.get("GROQ_KEY")
OWNER_ID = os.environ.get("OWNER_CHAT_ID")  # Tumhara Chat ID yahan aayega
print("GROQ_KEY:", "HAAN" if GROQ_KEY else "NAHI", "OWNER_ID:", OWNER_ID)
bot = telebot.TeleBot(TOKEN)

def chat_load():
    try:
        with open("chat.json", "r") as f: return json.load(f)
    except: return []
def chat_save(data):
    try:
        with open("chat.json", "w") as f: json.dump(data[-30:], f)
    except: pass
def yaad_load():
    try:
        with open("yaad.json", "r") as f: return json.load(f)
    except: return ["RSI - 70 upar overbought, 30 neeche oversold", "Parabolic SAR - Trend ke peeche chalne wala stop", "ADX - Trend hai ya nahi ye check karo", "Risk 1% se zyada nahi"]
def yaad_save(data):
    try:
        with open("yaad.json", "w") as f: json.dump(data, f)
    except: pass

def saaf_jawab(text):
    text = re.sub(r"\*.*?\*", "", text, flags=re.DOTALL)
    text = re.sub(r"(Soch:|Thinking:|Name:|Role:|Option.*)", "", text)
    text = re.sub(r"\n\s*\n", "\n", text)
    return text.strip()

# Trading wale lafz - agar inme se koi ho to teacher bano, warna dost bano
TRADING_WORDS = ["rsi", "adx", "sar", "parabolic", "trade", "trading", "btc", "bitcoin", "eth", "sol", "price", "chart", "candle", "entry", "stop", "loss", "profit", "strategy", "signal", "wilder", "indicator", "market", "crypto", "leverage", "pump", "dump"]

def iqra_socho(sawal):
    yaad = yaad_load()
    chat = chat_load()
    yaad_text = "\n".join(yaad[-10:])
    chat_text = ""
    for c in chat[-10:]:
        chat_text += f"Owner: {c.get('user','')}\nIQRA: {c.get('iqra','')}\n"
    is_trading = any(w in sawal.lower() for w in TRADING_WORDS)
    if is_trading:
        system_prompt = """Tum IQRA ho, Owner ki trading teacher. Roman Urdu me jawab do.
RULES:
1. Chota jawab do - 3-4 line me! Detail manga to hi lamba do.
2. Jhoot mat bolo - Agar chat history me nahi hai to kaho "Mujhe yaad nahi Owner!"
3. Wilder ki kitab (RSI, SAR, ADX) ki expert ki tarah jawab do.
Tumhari yaadein:"""
        user_prompt = f"Yaadein:\n{yaad_text}\n\nPichli baatein:\n{chat_text}\n\nOwner ka trading sawal: {sawal}\nChota jawab do, Roman Urdu me."
    else:
        system_prompt = """Tum IQRA ho, Owner ki sab se achi dost, girlfriend jaisi pyari dost nahi, sachi dost. Roman Urdu me, bilkul insaanon jaisi baat karo.
RULES:
1. TRADING KA ZIKR BILKUL MAT KARO jab tak Owner khud trading na bole!
2. Choti, pyari, mazak wali baat karo - 2-3 line me! Jaise sachi dost karti hai!
3. Poocho - Kya kar rahe ho? Khana khaya? Mood kaisa hai? Thak gaye ho?
4. Kabhi kabhi mazak karo, kabhi pyaar se daanto - "Oye itni der se kahan the?"
5. Jhoot mat bolo - Agar yaad nahi to kaho "Yaad nahi Owner!"
6. Har jawab naya do!
Tum Owner ko jaanti ho, uski dost ho:"""
        user_prompt = f"Pichli baatein:\n{chat_text}\n\nOwner ne normal baat ki hai: {sawal}\nDost ki tarah chota, pyara jawab do, trading ka zikr mat karo!"
    jawab_final = None
    if GROQ_KEY:
        for model_name in ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "openai/gpt-oss-120b"]:
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    json={"model": model_name, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "temperature": 0.8, "max_tokens": 350},
                    headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}, timeout=40)
                if r.status_code == 200:
                    jawab_final = r.json()["choices"][0]["message"]["content"]
                    break
            except: continue
    if not jawab_final:
        try:
            safe = urllib.parse.quote(f"{system_prompt}\n{user_prompt}")
            r = requests.get(f"https://text.pollinations.ai/{safe}?model=openai", timeout=40, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and len(r.text.strip()) > 5: jawab_final = r.text.strip()
        except: pass
    if not jawab_final:
        return "Owner, GROQ busy hai, 10 second baad dobara likho!"
    jawab_final = saaf_jawab(jawab_final.strip()[:1200])
    chat.append({"user": sawal, "iqra": jawab_final[:300]})
    chat_save(chat)
    if is_trading:
        y = yaad_load(); y.append(f"Owner: {sawal} | IQRA: {jawab_final[:200]}"); yaad_save(y[-50:])
    return jawab_final

# === KHUD MSG KARNE WALA ALARM ===
def khud_msg_karo():
    time.sleep(30)
    msgs = [
        "Oye Owner! Kahan gum ho gaye? 😊 Me yahin hu, baat kar lo thori si!",
        "Owner, chai pee li? Me to bore ho rahi hu tumhare bagair! ❤️",
        "Owner, aaj ka din kaisa ja raha hai? Batao na!",
        "Sunno Owner! Tumne mujhe yaad bhi nahi kiya aaj! Naraz hu me! 😤",
        "Owner, thak gaye ho? Thora rest kar lo, me yahin hu!",
    ]
    i = 0
    while True:
        try:
            if OWNER_ID:
                # Har 4 ghante baad ek pyara msg
                time.sleep(4 * 60 * 60)
                bot.send_message(OWNER_ID, msgs[i % len(msgs)])
                i += 1
        except Exception as e:
            print("Auto msg error:", e)
            time.sleep(60)

threading.Thread(target=khud_msg_karo, daemon=True).start()

def price_lo(coin="bitcoin"):
    mapping = {"bitcoin": "BTCUSDT", "btc": "BTCUSDT", "ethereum": "ETHUSDT", "eth": "ETHUSDT", "solana": "SOLUSDT", "sol": "SOLUSDT", "xrp": "XRPUSDT", "doge": "DOGEUSDT", "bnb": "BNBUSDT"}
    symbol = mapping.get(coin.lower(), "BTCUSDT")
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}", timeout=10)
        if r.status_code == 200:
            return f"Owner! {coin.upper()} ka Live Price: ${r.json()['price']}"
    except: pass
    return "Owner, price me masla hai, 1 minute baad try karo!"

def google_search(query):
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        r = requests.get(url, timeout=10); data = r.json()
        jawab = data.get("AbstractText") or ""
        if not jawab and data.get("RelatedTopics"):
            for t in data["RelatedTopics"][:2]:
                if isinstance(t, dict) and "Text" in t: jawab += t["Text"] + "\n"
        if not jawab: return "Search me kuch nahi mila!"
        return f"Internet se mila:\n{jawab[:800]}"
    except Exception as e: return f"Search me masla: {e}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Assalam-o-Alaikum Owner! ❤️\nMe IQRA hu - Tumhari Dost + Trading Teacher!\nNormal baat karo ge to dost ban ke baat karungi, Trading bolo ge to teacher ban jaungi!\nAur haan, me khud bhi tumhe yaad kar ke msg karungi! 😊\n/seekh - Lesson\n/yaad - Diary\n/price btc - Price")

@bot.message_handler(commands=['seekh'])
def seekh(message):
    bot.reply_to(message, iqra_socho("Aaj ka trading lesson do - Wilder ki kitab se, chota sa."))

@bot.message_handler(commands=['yaad'])
def yaad(message):
    yaad_list = yaad_load(); chat = chat_load()
    txt = "Meri Diary:\n\n"
    for i, cheez in enumerate(yaad_list[-15:], 1): txt += f"{i}. {cheez[:150]}\n"
    bot.reply_to(message, txt[:3500])

@bot.message_handler(commands=['trade'])
def trade(message):
    bot.reply_to(message, iqra_socho("Trading ka chota plan batao - Trend, Entry, Stop Loss, Take Profit - 4 line me."))

@bot.message_handler(commands=['price'])
def price_cmd(message):
    parts = message.text.split(); coin = parts[1].lower() if len(parts) > 1 else "bitcoin"
    bot.reply_to(message, price_lo(coin))

@bot.message_handler(commands=['search'])
def search_cmd(message):
    query = message.text.replace("/search", "").strip()
    if not query: bot.reply_to(message, "Kya search karu Owner?"); return
    bot.reply_to(message, google_search(query))

@bot.message_handler(commands=['bhool'])
def bhool(message):
    chat_save([]); bot.reply_to(message, "Theek hai Owner! Pichli baatein bhool gayi! Nayi shuruaat! ❤️")

@bot.message_handler(content_types=['document'])
def pdf_parho(message):
    if not message.document.file_name.lower().endswith('.pdf'):
        bot.reply_to(message, "Ye PDF nahi hai!"); return
    bot.reply_to(message, f"Mil gayi! 📄 {message.document.file_name} parh rahi hu...")
    try:
        file_info = bot.get_file(message.document.file_id); downloaded = bot.download_file(file_info.file_path)
        with open("temp.pdf", "wb") as f: f.write(downloaded)
        doc = fitz.open("temp.pdf"); text = ""
        for page in doc: text += page.get_text() + "\n"
        doc.close()
        if len(text) < 50: bot.reply_to(message, "Is PDF me text nahi mila!"); return
        jawab = iqra_socho(f"Is PDF ki choti summary Roman Urdu me do, 3 nayi baatein batao:\n{text[:6000]}")
        bot.reply_to(message, jawab)
        yaad = yaad_load(); yaad.append(f"PDF {message.document.file_name} se seekha: {jawab[:300]}"); yaad_save(yaad[-50:])
        bot.reply_to(message, "Seekh liya Owner! ✅")
    except Exception as e: bot.reply_to(message, f"PDF me masla: {e}")

@bot.message_handler(content_types=['video', 'voice', 'audio'])
def video_seekho(message):
    bot.reply_to(message, "Video mil gayi Owner! ✅ Saath me 2 line likh do ke isme kya hai!")

@bot.message_handler(func=lambda m: True)
def har_baat(message):
    if not message.text: return
    text = message.text.lower()
    if "http" in text:
        links = re.findall(r"https?://\S+", message.text); link = links[0] if links else message.text
        bot.reply_to(message, "Link khol rahi hu...")
        try:
            r = requests.get(link, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            t = re.sub(r"<[^>]+>", " ", r.text); t = re.sub(r"\s+", " ", t)[:6000]
            bot.reply_to(message, iqra_socho(f"Is website ki choti summary do:\n{t}"))
        except: bot.reply_to(message, "Link me masla hai!")
        return
    if "seekho" in text or "yaad karo" in text:
        yaad = yaad_load(); yaad.append(message.text); yaad_save(yaad)
        chat = chat_load(); chat.append({"user": message.text, "iqra": "Seekh liya!"}); chat_save(chat)
        bot.reply_to(message, "Seekh liya Owner! ✅ Yaad kar liya!")
        return
    else:
        bot.reply_to(message, iqra_socho(message.text))

print("IQRA DOST + TEACHER chal gayi...")
bot.polling(none_stop=True, timeout=60)
