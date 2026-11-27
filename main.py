# IQRA - ONLINE - PURA UPDATED CODE - BINA KEY KE
import telebot
import os
import requests
import json
import re
import threading
import urllib.parse
from flask import Flask

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
bot = telebot.TeleBot(TOKEN)

def yaad_load():
    try:
        with open("yaad.json", "r") as f:
            return json.load(f)
    except:
        return ["RSI - 70 upar overbought, 30 neeche oversold", "Parabolic SAR - Trend ke peeche chalne wala stop", "ADX - Trend hai ya nahi ye check karo", "Risk 1% se zyada nahi", "Wilder ka usool - Koi ek system har market me nahi chalta"]

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

# === IQRA KA DIMAG - ONLINE + OFFLINE - 3 RASTE ===
def iqra_socho(sawal):
    yaad = yaad_load()
    yaad_text = "\n".join(yaad[-20:])
    prompt = f"Tum IQRA ho, Owner ki trading dost. Roman Urdu me aasan lafzon me jawab do. Har roz naya seekhti ho. Tumhari yaadein: {yaad_text} Owner ka sawal: {sawal}"

    # RASTA 1 - Pollinations GET - NAYA RASTA - BINA KEY KE
    try:
        safe_prompt = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{safe_prompt}?model=openai"
        r = requests.get(url, timeout=40, headers={"User-Agent": "Mozilla/5.0"})
        print("Pollinations GET status:", r.status_code)
        if r.status_code == 200 and len(r.text.strip()) > 5:
            jawab = r.text.strip()
            y = yaad_load()
            y.append(f"Owner: {sawal} | IQRA: {jawab[:200]}")
            yaad_save(y[-50:])
            return saaf_jawab(jawab[:2500])
        else:
            print("Pollinations GET fail:", r.text[:300])
    except Exception as e:
        print("Pollinations GET error:", e)

    # RASTA 2 - Pollinations POST - DOBARA TRY
    try:
        r = requests.post(
            "https://text.pollinations.ai/openai",
            json={"messages": [{"role": "user", "content": prompt}], "model": "openai"},
            timeout=40,
            headers={"Content-Type": "application/json"}
        )
        print("Pollinations POST status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            jawab = data["choices"][0]["message"]["content"]
            if jawab and len(jawab.strip()) > 5:
                y = yaad_load()
                y.append(f"Owner: {sawal} | IQRA: {jawab[:200]}")
                yaad_save(y[-50:])
                return saaf_jawab(jawab.strip()[:2500])
    except Exception as e:
        print("Pollinations POST error:", e)

    # RASTA 3 - APNA DIMAG - Agar Dono Band Hon To Bhi Jawab Do!
    s = sawal.lower()
    if any(x in s for x in ["hi", "hello", "assalam", "salam", "hey"]):
        return "Assalam-o-Alaikum Owner! ❤️ Me IQRA hu, ONLINE hu! Bolo aaj kya seekhe? RSI, ADX, SAR ya Trade ka plan pooch lo!"
    if "rsi" in s:
        return "RSI Wilder ne banaya tha Owner!\n\n70 se upar = Market thak gaya hai, gir sakta hai (Overbought)\n30 se neeche = Market dab gaya hai, uth sakta hai (Oversold)\n\nAkela RSI pe trade nahi lena! Pehle ADX se trend confirm karo!"
    if "adx" in s:
        return "ADX matlab Trend ki Taqat!\n\nADX 25 se upar = Strong Trend hai, SAR use karo\nADX 20 se neeche = Sideways hai, RSI use karo\n\nWilder kehta tha - Pehle ye dekho trend hai ya nahi!"
    if "sar" in s or "parabolic" in s:
        return "Parabolic SAR matlab Stop And Reverse!\n\nDots price ke neeche = Uptrend hai\nDots price ke upar = Downtrend hai\n\nYe trend ke peeche chalne wala Stop Loss hai Owner!"
    if "trade" in s or "entry" in s or "signal" in s:
        return "Trade aise lo Owner:\n\n1. Pehle Trend - ADX se check karo\n2. Phir Indicator - RSI / SAR\n3. Phir Entry, Stop Loss, Take Profit\n4. Risk - 1% se zyada kabhi nahi!"
    if "risk" in s or "capital" in s or "money" in s or "paisa" in s:
        return "Capital Management - Risk pehle, profit baad me!\nEk trade me 1% se zyada risk kabhi nahi lena! Agar 1000$ hain to sirf 10$ ka risk!"
    if "wilder" in s or "kitab" in s or "book" in s:
        return "Wilder ne New Concepts likhi thi Owner!\nUsme 4 cheezein di thi - RSI, Parabolic SAR, ADX aur Volatility System!\nUska usool tha - Koi ek system har market me nahi chalta! Pehle market ki haalat dekho!"
    if "btc" in s or "bitcoin" in s or "crypto" in s:
        return "BTC ke liye Owner, /price btc likho, me live price de dungi!\nAur trading ke liye yaad rakho - BTC me bhi pehle ADX se trend dekho, phir RSI se entry lo! Bina trend ke trade mat lo!"
    if "seekh" in s or "lesson" in s:
        return "Aaj ka Lesson - Wilder se:\n\nPehle ye dekho - Market TREND me hai ya SIDEWAYS me?\nAgar Trend me hai to Parabolic SAR + ADX use karo.\nAgar Sideways hai to RSI use karo.\n\nSirf ek indicator pe kabhi trade mat lo!"
    if "kaise ho" in s or "kesi ho" in s or "kya haal" in s:
        return "Me bilkul theek hu Owner! ❤️ Tum sunao, aaj kya seekhna hai? RSI samjhau ya Trade ka poora plan banau?"
    if "shukria" in s or "thanks" in s:
        return "Koi baat nahi Owner! ❤️ Tum seekhte raho, me sikhati rahungi! Bolo aur kya poochna hai?"
    return f"Samajh gayi Owner! Tumne poocha - {sawal}\n\nTrading me sab se pehle market ki haalat dekho - Trend hai ya Sideways? Phir RSI / SAR lagao, aur Risk 1% se zyada mat lo! Is bare me aur detail se pooch lo, me samjha dungi!"

def price_lo(coin="bitcoin"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        r = requests.get(url, timeout=10)
        price = r.json()[coin]["usd"]
        return f"Owner! {coin} ka Live Price hai: ${price}"
    except:
        return "Owner, price lene me masla aa gaya, thori der baad /price likhna!"

def google_search(query):
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        r = requests.get(url, timeout=10)
        data = r.json()
        jawab = data.get("AbstractText") or ""
        if not jawab and data.get("RelatedTopics"):
            for t in data["RelatedTopics"][:3]:
                if isinstance(t, dict) and "Text" in t:
                    jawab += t["Text"] + "\n"
        if not jawab:
            return "Owner, search me kuch nahi mila, koi link bhejo me khol ke parh lungi!"
        return f"Internet se mila Owner:\n{jawab[:1200]}"
    except Exception as e:
        return f"Search me masla: {e}"

def link_parho(link):
    try:
        r = requests.get(link, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.DOTALL)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL)
        text = re.sub("<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)[:8000]
        if len(text.strip()) < 50:
            return "Owner, is link me text nahi mila, koi aur link bhejo!"
        jawab = iqra_socho(f"Is website ko parh ke iski summary Roman Urdu me do, trading ki nayi baat batao:\nLink: {link}\nText: {text}")
        y = yaad_load()
        y.append(f"Website {link} se seekha: {text[:400]}")
        yaad_save(y[-50:])
        return jawab
    except Exception as e:
        return f"Link kholne me masla: {e}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Assalam-o-Alaikum Owner! ❤️\nMe IQRA hu - ONLINE WALI, BINA KEY KE!\nMe har roz seekhti hu, yaad rakhti hu!\n/seekh - Naya lesson\n/yaad - Kya seekha hai\n/price btc - Live Price\n/search - Internet pe search\nPDF bhejo to parh ke seekhungi!\nLink bhejo to khol ke seekhungi!")

@bot.message_handler(commands=['seekh'])
def seekh(message):
    bot.reply_to(message, "Naya lesson la rahi hu Owner...")
    bot.reply_to(message, iqra_socho("Aaj ka trading lesson do - Wilder ki kitab se nayi baat, Roman Urdu me aasan me."))

@bot.message_handler(commands=['yaad'])
def yaad(message):
    yaad_list = yaad_load()
    yaad_text = "Meri Diary - Maine ye seekha hai:\n\n"
    for i, cheez in enumerate(yaad_list[-30:], 1):
        yaad_text += f"{i}. {cheez[:200]}\n"
    bot.reply_to(message, yaad_text[:4000])

@bot.message_handler(commands=['trade'])
def trade(message):
    bot.reply_to(message, iqra_socho("Trading ka poora plan batao - Trend, Entry, Stop Loss, Take Profit, Risk Management - Roman Urdu me."))

@bot.message_handler(commands=['price'])
def price_cmd(message):
    parts = message.text.split()
    coin = parts[1].lower() if len(parts) > 1 else "bitcoin"
    if coin == "btc": coin = "bitcoin"
    if coin == "eth": coin = "ethereum"
    if coin == "sol": coin = "solana"
    bot.reply_to(message, price_lo(coin))

@bot.message_handler(commands=['search'])
def search_cmd(message):
    query = message.text.replace("/search", "").strip()
    if not query:
        bot.reply_to(message, "Owner, kya search karu? Jaise: /search BTC news")
        return
    bot.reply_to(message, "Internet pe dhond rahi hu Owner...")
    bot.reply_to(message, google_search(query))
    bot.reply_to(message, iqra_socho(f"Is topic pe trading ke liye kya seekhna chahiye: {query} - Roman Urdu me."))

@bot.message_handler(content_types=['document'])
def pdf_parho(message):
    if not message.document.file_name.lower().endswith('.pdf'):
        bot.reply_to(message, "Owner, ye PDF nahi hai!")
        return
    bot.reply_to(message, f"Mil gayi Owner! 📄 {message.document.file_name} parh ke seekhungi...")
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        with open("temp.pdf", "wb") as f: f.write(downloaded)
        doc = fitz.open("temp.pdf")
        text = ""
        for page in doc: text += page.get_text() + "\n"
        doc.close()
        if len(text) < 50:
            bot.reply_to(message, "Owner, is PDF me text nahi mila!")
            return
        bot.reply_to(message, f"Parh liya! {len(text)} lafz hain, summary bana rahi hu...")
        jawab = iqra_socho(f"Is PDF ki summary Roman Urdu me do, 5 nayi trading baatein batao:\n{text[:8000]}")
        bot.reply_to(message, jawab)
        yaad = yaad_load()
        yaad.append(f"PDF {message.document.file_name} se seekha: {jawab[:400]}")
        yaad_save(yaad[-50:])
        bot.reply_to(message, "Seekh liya Owner! ✅ /yaad me save ho gaya!")
    except Exception as e:
        bot.reply_to(message, f"PDF me masla: {e}")

@bot.message_handler(content_types=['video', 'voice', 'audio'])
def video_seekho(message):
    bot.reply_to(message, "Owner, video/voice mil gayi! ✅\nSaath me 2 line likh do ke isme kya seekha, me pakka yaad kar lungi!")
    yaad = yaad_load()
    yaad.append("Video/Audio bheji gayi")
    yaad_save(yaad)

@bot.message_handler(func=lambda m: True)
def har_baat(message):
    if not message.text: return
    text = message.text.lower()
    if "http" in text:
        links = re.findall(r"https?://\S+", message.text)
        link = links[0] if links else message.text
        bot.reply_to(message, "Link mil gaya Owner! Khol ke parh rahi hu...")
        bot.reply_to(message, link_parho(link))
        return
    if "seekho" in text or "yaad karo" in text:
        yaad = yaad_load()
        yaad.append(message.text)
        yaad_save(yaad)
        bot.reply_to(message, "Haan Owner! Seekh liya! Yaad me likh liya! ✅")
        return
    else:
        bot.reply_to(message, iqra_socho(message.text))

print("IQRA ONLINE BINA KEY KE chal gayi hai...")
bot.polling(none_stop=True, timeout=60)
