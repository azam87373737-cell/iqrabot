# IQRA - Seekhne Wali Trading Bot
# Owner: Tum
# Pehli Kitab: Wilder - New Concepts in Technical Trading Systems

import telebot
import os
import requests
import json
import re
import threading
from flask import Flask

# === RENDER KE LIYE PORT - ISKO MAT HATANA ===
app = Flask(__name__)
@app.route('/')
def home(): return "IQRA is Alive!"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_web, daemon=True).start()

try:
    import fitz
except:
    fitz = None

TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")
bot = telebot.TeleBot(TOKEN)

IQRA_MEMORY = [
    "RSI - Wilder ne banaya, 70 upar overbought, 30 neeche oversold",
    "Parabolic SAR - Stop And Reverse, trend ke peeche chalne wala stop",
    "ADX / Directional Movement - Pehle trend hai ya nahi ye check karo",
    "Wilder ka usool - Koi ek system har market me nahi chalta",
    "Sirf indicator pe trade nahi lena, pehle market ki haalat dekho",
    "Capital Management - Risk pehle, profit baad me"
]

def yaad_load():
    try:
        with open("yaad.json", "r") as f:
            return json.load(f)
    except:
        return IQRA_MEMORY.copy()

def yaad_save(data):
    try:
        with open("yaad.json", "w") as f:
            json.dump(data, f)
    except:
        pass

def saaf_jawab(text):
    text = re.sub(r"\*.*?\*", "", text, flags=re.DOTALL)
    text = re.sub(r"(Soch:|Thinking:|Name:|Role:|Option.*)", "", text)
    text = re.sub(r"\n\s*\n", "\n", text)
    return text.strip()

def iqra_socho(sawal):
    yaad = yaad_load()
    yaad_text = "\n".join(yaad[-20:])
    if not GEMINI_KEY:
        return "Owner, GEMINI_KEY Secret me nahi hai, isliye me apni purani yaad se bata rahi hu. /yaad likh ke dekho!"
    prompt = f"Tum IQRA ho, Owner ki dost. Roman Urdu me aasan lafzon me jawab do. Tumhari yaadein:\n{yaad_text}\n\nOwner ka sawal: {sawal}"
    try:
        # NAYA MODEL - 1.5 ki jagah 2.0
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
        data = r.json()
        # === YAHI ASAL FIX HAI - candidates check ===
        if "candidates" not in data or not data["candidates"]:
            print("Gemini Error:", data)
            # Agar API ne block kiya to purani yaad se jawab do
            return "Owner, Gemini ne abhi jawab nahi diya (shayad thora busy hai). Dobara pooch lo, ya /yaad likh ke meri purani yaad dekh lo! Meri yaad se: RSI 70 upar overbought, 30 neeche oversold hota hai."
        jawab = data["candidates"][0]["content"]["parts"][0]["text"]
        return saaf_jawab(jawab)
    except Exception as e:
        print("Error:", e)
        return f"Owner, dimagh me halka sa masla aa gaya, dobara pooch lo! ({e})"

def price_lo(coin="bitcoin"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        r = requests.get(url, timeout=10)
        price = r.json()[coin]["usd"]
        return f"Owner! {coin} ka Live Price hai: ${price}\n(CoinGecko se, kabhi block nahi hoga!)"
    except:
        return "Owner, price lene me masla aa gaya, thori der baad /price likhna!"

def google_search(query):
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
        r = requests.get(url, timeout=10)
        data = r.json()
        jawab = data.get("AbstractText") or ""
        if not jawab and data.get("RelatedTopics"):
            jawab = data["RelatedTopics"][0].get("Text", "")
        if not jawab:
            return "Owner, internet pe iske bare me kuch khaas nahi mila!"
        return f"Internet se mila Owner:\n{jawab[:1000]}"
    except Exception as e:
        return f"Search me masla: {e}"

def link_parho(link):
    try:
        r = requests.get(link, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        text = re.sub("<[^>]+>", " ", r.text)[:5000]
        return iqra_socho(f"Is website ka text ye hai, iski summary Roman Urdu me do:\n{text}")
    except Exception as e:
        return f"Link kholne me masla: {e}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "Assalam-o-Alaikum Owner! ❤️\n"
        "Mera naam IQRA hai!\n"
        "Maine pehli kitab parh li hai - Wilder ki New Concepts!\n"
        "Mujhe RSI, SAR, ADX aa gaya hai!\n"
        "Bolo aaj kya seekhu?\n"
        "/seekh - Aaj ka lesson\n"
        "/yaad - Maine kya kya seekha hai\n"
        "/price btc - Live Price CoinGecko se\n"
        "/search - Internet pe search\n"
        "PDF bhejo to me parh ke summary dungi!"
    )

@bot.message_handler(commands=['seekh'])
def seekh(message):
    bot.reply_to(message,
        "Aaj ka Lesson - Wilder se:\n\n"
        "Pehle ye dekho - Market TREND me hai ya SIDEWAYS me?\n"
        "Agar Trend me hai to Parabolic SAR + ADX use karo.\n"
        "Agar Sideways hai to RSI use karo.\n\n"
        "Sirf ek indicator pe kabhi trade mat lo!\n"
        "Owner, ye sahi seekha maine?"
    )

@bot.message_handler(commands=['yaad'])
def yaad(message):
    yaad_list = yaad_load()
    yaad_text = "Meri Diary - Maine ye seekha hai:\n\n"
    for i, cheez in enumerate(yaad_list, 1):
        yaad_text += f"{i}. {cheez}\n"
    bot.reply_to(message, yaad_text[:4000])

@bot.message_handler(commands=['trade'])
def trade(message):
    bot.reply_to(message,
        "Trade aise dungi Owner:\n\n"
        "1. Pehle Trend - ADX se check karo\n"
        "2. Phir Indicator - RSI / SAR\n"
        "3. Phir Entry, Stop Loss, Take Profit\n"
        "4. Risk - 1% se zyada kabhi nahi!\n\n"
        "Khali indicator pe kabhi trade nahi!"
    )

@bot.message_handler(commands=['price'])
def price_cmd(message):
    parts = message.text.split()
    coin = parts[1].lower() if len(parts) > 1 else "bitcoin"
    if coin == "btc":
        coin = "bitcoin"
    if coin == "eth":
        coin = "ethereum"
    bot.reply_to(message, price_lo(coin))

@bot.message_handler(commands=['search'])
def search_cmd(message):
    query = message.text.replace("/search", "").strip()
    if not query:
        bot.reply_to(message, "Owner, kya search karu? Jaise: /search BTC news")
        return
    bot.reply_to(message, "Internet pe dhond rahi hu Owner, ruko...")
    bot.reply_to(message, google_search(query))

@bot.message_handler(content_types=['document'])
def pdf_parho(message):
    if not message.document.file_name.lower().endswith('.pdf'):
        bot.reply_to(message, "Owner, ye PDF nahi hai!")
        return
    bot.reply_to(message, f"Mil gayi Owner! 📄 {message.document.file_name} download kar rahi hu...")
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        with open("temp.pdf", "wb") as f:
            f.write(downloaded)
        doc = fitz.open("temp.pdf")
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        if len(text) < 50:
            bot.reply_to(message, "Owner, is PDF me text nahi mila!")
            return
        bot.reply_to(message, f"Parh liya! {len(text)} lafz hain, summary bana rahi hu...")
        jawab = iqra_socho(f"Is PDF ki summary Roman Urdu me do:\n{text[:8000]}")
        bot.reply_to(message, jawab)
        yaad = yaad_load()
        yaad.append(f"PDF {message.document.file_name}: {text[:500]}")
        yaad_save(yaad)
    except Exception as e:
        bot.reply_to(message, f"PDF me masla: {e}")

@bot.message_handler(content_types=['video', 'voice', 'audio'])
def video_seekho(message):
    bot.reply_to(message,
        "Owner, video/voice mil gayi! ✅\n"
        "Me iski awaz ko samajh ke seekhungi!\n"
        "Tum iske saath 2 line bhi likh do ke is video me kya seekha, taake me pakka yaad kar lu!\n"
        "Jaise likh do: Seekho ki is video me RSI ka naya tareeqa hai"
    )
    yaad = yaad_load()
    yaad.append("Video/Audio bheji gayi, Owner ne kaha isse seekhna hai")
    yaad_save(yaad)

@bot.message_handler(func=lambda m: True)
def har_baat(message):
    if not message.text:
        return
    text = message.text.lower()
    if "http" in text:
        bot.reply_to(message, "Link mil gaya Owner! Khol ke parh rahi hu...")
        bot.reply_to(message, link_parho(message.text))
        return
    if "seekho" in text or "yaad karo" in text:
        yaad = yaad_load()
        yaad.append(message.text)
        yaad_save(yaad)
        bot.reply_to(message, "Haan Owner! Seekh liya! Ab kabhi nahi bhoolungi! Copy me likh liya hai! ✅")
        return
    if "rsi" in text:
        bot.reply_to(message, "RSI Wilder ne banaya tha! 70 se upar matlab market thak gaya, 30 se neeche matlab dab gaya. Lekin akela RSI pe trade nahi lena, ADX se trend bhi confirm karo Owner!")
    elif "trade" in text:
        bot.reply_to(message, "Trade aise dungi Owner: Pehle Trend + Phir RSI/SAR + Phir Entry, Stop Loss, Take Profit + Risk. Khali indicator pe kabhi nahi!")
    else:
        bot.reply_to(message, iqra_socho(message.text))

print("IQRA chal gayi hai...")
bot.polling(none_stop=True, timeout=60)
