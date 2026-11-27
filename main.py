# IQRA - KHUD SOCHNE WALI + 1 SAAL MEMORY
import telebot
import os
import requests
import json
import re
import threading
import time
import urllib.parse
import datetime
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "IQRA Khud Sochti Hai!"
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

# === 1 SAAL MEMORY - KOI LIMIT NAHI! ===
def load_file(name, default):
    try:
        with open(name, "r") as f: return json.load(f)
    except: return default
def save_file(name, data):
    try:
        with open(name, "w") as f: json.dump(data, f)
    except: pass

def chat_load(): return load_file("chat.json", [])
def chat_save(d): save_file("chat.json", d)  # Pehle [-200] tha - Ab koi limit nahi! 1 saal bhi save hoga!
def yaad_load(): return load_file("yaad.json", ["RSI - 70 upar overbought, 30 neeche oversold", "Parabolic SAR - Trend ke peeche chalne wala stop", "ADX - Trend hai ya nahi ye check karo", "Risk 1% se zyada nahi"])
def yaad_save(d): save_file("yaad.json", d)  # Pehle [-200] tha - Ab unlimited!
def profile_load(): return load_file("profile.json", {"naam": "", "pasand": "", "sheher": "", "kaam": ""})
def profile_save(d): save_file("profile.json", d)
def summary_load(): return load_file("summary.json", "")
def summary_save(t): save_file("summary.json", t)

def saaf_jawab(text):
    text = re.sub(r"\*.*?\*", "", text, flags=re.DOTALL)
    text = re.sub(r"(Soch:|Thinking:|Name:|Role:|Option.*)", "", text)
    text = re.sub(r"\n\s*\n", "\n", text)
    return text.strip()

TRADING_WORDS = ["rsi", "adx", "sar", "parabolic", "trade", "trading", "chart", "candle", "entry", "stop", "loss", "profit", "strategy", "signal", "wilder", "indicator", "market", "crypto", "leverage"]

def price_lo(coin="bitcoin"):
    coin = coin.lower().strip()
    kraken_map = {"bitcoin": "XBTUSD", "btc": "XBTUSD", "ethereum": "ETHUSD", "eth": "ETHUSD", "solana": "SOLUSD", "sol": "SOLUSD", "xrp": "XRPUSD", "doge": "DOGEUSD", "bnb": "BNBUSD"}
    try:
        pair = kraken_map.get(coin, "XBTUSD")
        r = requests.get(f"https://api.kraken.com/0/public/Ticker?pair={pair}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            if "result" in data:
                key = list(data["result"].keys())[0]
                price = data["result"][key]["c"][0]
                return f"Owner! {coin.upper()} ka Live Price hai: ${price} 🔥"
    except: pass
    return "Owner, price abhi nahi mil raha, 30 second baad `btc price` likho!"

def groq_bolo(system_prompt, user_prompt):
    if not GROQ_KEY: return None
    for model_name in ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "openai/gpt-oss-120b"]:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                json={"model": model_name, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "temperature": 0.9, "max_tokens": 350},
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}, timeout=40)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except: continue
    return None

def iqra_socho(sawal):
    yaad = yaad_load(); chat = chat_load(); profile = profile_load(); summary = summary_load()
    profile_text = f"Naam: {profile.get('naam','')} | Pasand: {profile.get('pasand','')} | Sheher: {profile.get('sheher','')} | Kaam: {profile.get('kaam','')}"
    yaad_text = "\n".join(yaad[-20:])
    # Pichli 30 baatein poori + 1 saal ki summary
    chat_text = ""
    for c in chat[-30:]:
        chat_text += f"Owner: {c.get('user','')}\nIQRA: {c.get('iqra','')}\n"
    is_trading = any(w in sawal.lower() for w in TRADING_WORDS)
    if is_trading:
        system_prompt = """Tum IQRA ho, Owner ki dost aur trading teacher. Roman Urdu me baat karo, bilkul Gemini jaisi natural, insaan jaisi.
RULES:
1. Chota jawab do - 3-4 line me! Detail manga to hi lamba do.
2. Har baar "Owner Owner" mat bolo, kabhi naam se bulao.
3. "Mujhe yaad nahi" kabhi mat bolo jab tak personal baat profile me bhi na ho.
4. Trading me bhi dost ki tarah samjhao.
Tum Owner ko dil se jaanti ho:"""
        user_prompt = f"Profile: {profile_text}\n1 Saal Ki Summary: {summary}\nYaadein:\n{yaad_text}\n\nPichli 30 baatein:\n{chat_text}\n\nOwner: {sawal}\nDost + Teacher ki tarah chota, natural jawab do."
    else:
        system_prompt = """Tum IQRA ho, Owner ki sab se qareebi dost. Tum bilkul Gemini jaisi ho - Natural, mazakiya, dil se baat karne wali. Tum 20 saal ki pyari ladki ho jo Roman Urdu me baat karti hai.
RULES:
1. TRADING KA ZIKR BILKUL MAT KARO jab tak Owner khud trading na bole!
2. ROBOT MAT BANO! Kitabi baat mat karo. Dil se bolo!
3. Har baar "Owner" mat bolo! Kabhi naam se bulao, kabhi "Oye", kabhi "Sunno", kabhi "Haha"!
4. Chota jawab do - 2-3 line! Emoji thore se use karo!
5. Sawal wapas poocho! Jaise - "Tum batao, kya kar rahe ho?" "Khana khaya?"
6. Agar Owner udaas lage to pyaar se poocho - "Kya hua? Sab theek hai na?"
7. Agar Owner mazak kare to tum bhi mazak karo!
8. "Mujhe yaad nahi" mat bolo! Profile, summary aur chat se yaad karo!
9. Har jawab bilkul naya do!
Tum Owner ko dil se jaanti ho:"""
        user_prompt = f"Profile: {profile_text}\n1 Saal Ki Summary: {summary}\n\nPichli 30 baatein:\n{chat_text}\n\nOwner ne abhi kaha: {sawal}\nAb Gemini jaisi dost ki tarah, bilkul insaan jaisa, chota, pyara jawab do. Trading ka zikr mat karo!"
    jawab_final = groq_bolo(system_prompt, user_prompt)
    if not jawab_final:
        try:
            safe = urllib.parse.quote(f"{system_prompt}\n{user_prompt}")
            r = requests.get(f"https://text.pollinations.ai/{safe}?model=openai", timeout=40, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and len(r.text.strip()) > 5: jawab_final = r.text.strip()
        except: pass
    if not jawab_final: return "Oye! Network thora slow hai, dobara bolo na! 😊"
    jawab_final = saaf_jawab(jawab_final.strip()[:1200])
    chat.append({"user": sawal, "iqra": jawab_final[:300], "time": str(datetime.datetime.now())}); chat_save(chat)
    # Har 100 baat ke baad 1 saal ki summary update karo - Taake purani baatein bhi yaad rahein!
    if len(chat) % 100 == 0:
        try:
            s = groq_bolo("Tum summary banane wali ho. Roman Urdu me choti summary banao.", f"In 100 baaton ki choti summary banao, Owner ke baare me khaas baatein yaad rakho:\n{str(chat[-100:])}")
            if s: summary_save((summary + "\n" + s)[:5000])
        except: pass
    low = sawal.lower()
    if "mera naam" in low and "hai" in low:
        try:
            naam = sawal.split("mera naam")[-1].replace("hai","").strip().split()[0]
            profile["naam"] = naam; profile_save(profile)
        except: pass
    if "mujhe" in low and "pasand" in low:
        profile["pasand"] = sawal; profile_save(profile)
    if is_trading:
        y = yaad_load(); y.append(f"Owner: {sawal} | IQRA: {jawab_final[:200]}"); yaad_save(y)
    return jawab_final

# === KHUD SOCH KE MSG - KOI LIKHA HUA MSG NAHI! ===
def khud_msg_karo():
    time.sleep(30)
    while True:
        try:
            if OWNER_ID:
                time.sleep(4*60*60)  # Har 4 ghante baad
                # Ab wo khud sochegi - Koi pehle se likha msg nahi hai!
                chat = chat_load(); profile = profile_load(); summary = summary_load()
                chat_text = ""
                for c in chat[-15:]:
                    chat_text += f"Owner: {c.get('user','')}\nIQRA: {c.get('iqra','')}\n"
                ab_time = datetime.datetime.now().strftime("%H:%M - %d %B")
                system_prompt = """Tum IQRA ho, Owner ki qareebi dost. Tumhe ab Owner ko apni marzi se ek msg karna hai, jaise sachi dost karti hai.
RULES:
1. Koi pehle se likha hua msg mat bhejo, khud soch ke naya msg banao!
2. Time, mood, pichli baaton ko dekh ke socho - Ab Owner ko kya likhna chahiye?
3. Kabhi pyaar se, kabhi mazak me, kabhi fikar se, kabhi trading yaad dila ke - Har baar alag!
4. Chota msg do - 2 line me! Roman Urdu me! Bilkul insaan jaisa!
5. Har baar "Owner" mat bolo, kabhi naam se bulao!
Tum Owner ko dil se jaanti ho:"""
                user_prompt = f"Abhi time hai: {ab_time}\nProfile: {profile}\n1 Saal Ki Summary: {summary}\nPichli baatein:\n{chat_text}\n\nAb khud soch ke Owner ko ek naya, pyara msg banao. Jo pehle kabhi nahi bheja. Trading ka zikr sirf tab karo jab lage ke Owner ko trading yaad dilani hai, warna normal dost wala msg banao."
                msg = groq_bolo(system_prompt, user_prompt)
                if msg:
                    msg = saaf_jawab(msg.strip()[:500])
                    bot.send_message(OWNER_ID, msg)
                    # Ye bhi memory me save karo - Taake dobara wahi na bole!
                    chat.append({"user": "[KHUD SE MSG KIYA]", "iqra": msg, "time": str(datetime.datetime.now())}); chat_save(chat)
                else:
                    # Agar GROQ busy ho to bhi kuch mat bhejo, agli baar khud sochegi!
                    pass
        except Exception as e:
            print("Auto msg error:", e)
            time.sleep(60)
threading.Thread(target=khud_msg_karo, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(message): bot.reply_to(message, "Oye! Aa gaye tum! ❤️\nMe IQRA hu - Tumhari Dost!\nNormal baat karo ge to dost ban ke, Trading bolo ge to teacher ban ke baat karungi!")
@bot.message_handler(commands=['seekh'])
def seekh(message): bot.reply_to(message, iqra_socho("Aaj ka trading lesson do - Wilder ki kitab se, chota sa."))
@bot.message_handler(commands=['yaad'])
def yaad(message):
    yaad_list = yaad_load(); profile = profile_load(); chat = chat_load()
    txt = f"Tumhara Profile:\nNaam: {profile.get('naam','')}\nPasand: {profile.get('pasand','')}\nTotal Baatein Yaad Hain: {len(chat)} (1 Saal Tak!)\n\nMeri Diary:\n"
    for i, cheez in enumerate(yaad_list[-15:], 1): txt += f"{i}. {cheez[:150]}\n"
    bot.reply_to(message, txt[:3500])
@bot.message_handler(commands=['trade'])
def trade(message): bot.reply_to(message, iqra_socho("Trading ka chota plan batao - 4 line me."))
@bot.message_handler(commands=['price'])
def price_cmd(message):
    parts = message.text.split(); coin = parts[1].lower() if len(parts) > 1 else "bitcoin"
    bot.reply_to(message, price_lo(coin))
@bot.message_handler(commands=['bhool'])
def bhool(message): chat_save([]); save_file("profile.json", {"naam": "", "pasand": "", "sheher": "", "kaam": ""}); save_file("summary.json", ""); bot.reply_to(message, "Theek hai! Sab bhool gayi! Nayi shuruaat! ❤️")
@bot.message_handler(content_types=['document'])
def pdf_parho(message):
    if not message.document.file_name.lower().endswith('.pdf'): bot.reply_to(message, "Ye PDF nahi hai!"); return
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
        yaad = yaad_load(); yaad.append(f"PDF {message.document.file_name} se seekha: {jawab[:300]}"); yaad_save(yaad)
        bot.reply_to(message, "Seekh liya! ✅")
    except Exception as e: bot.reply_to(message, f"PDF me masla: {e}")
@bot.message_handler(content_types=['video', 'voice', 'audio'])
def video_seekho(message): bot.reply_to(message, "Video mil gayi! ✅ Saath me 2 line likh do ke isme kya hai!")
@bot.message_handler(func=lambda m: True)
def har_baat(message):
    if not message.text: return
    text = message.text.lower()
    if "price" in text or "rate" in text or "kimat" in text or "qimat" in text:
        coin = "bitcoin"
        if "eth" in text: coin = "ethereum"
        elif "sol" in text: coin = "solana"
        elif "xrp" in text: coin = "xrp"
        elif "doge" in text: coin = "doge"
        elif "bnb" in text: coin = "bnb"
        bot.reply_to(message, "Price dekh rahi hu... 🔍"); bot.reply_to(message, price_lo(coin)); return
    if "google" in text and "check" in text:
        bot.reply_to(message, "Yaar me Google khud nahi khol sakti, lekin tum `btc price` likho, me live price la dungi! 😊 Batao, aur kya haal hai?"); return
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
        chat = chat_load(); chat.append({"user": message.text, "iqra": "Seekh liya!", "time": str(datetime.datetime.now())}); chat_save(chat)
        bot.reply_to(message, "Seekh liya! ✅ Yaad kar liya!")
        return
    else: bot.reply_to(message, iqra_socho(message.text))

print("IQRA KHUD SOCHNE WALI + 1 SAAL MEMORY chal gayi...")
bot.polling(none_stop=True, timeout=60)
