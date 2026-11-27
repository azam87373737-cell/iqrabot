# IQRA - ONLINE SEEKHNE WALI - Har Roz Seekhegi, Yaad Rakhegi
import telebot
import os
import requests
import json
import re
import threading
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
GROQ_KEY = os.environ.get("GROQ_KEY")
bot = telebot.TeleBot(TOKEN)

IQRA_MEMORY = [
    "RSI - Wilder ne banaya, 70 upar overbought, 30 neeche oversold",
    "Parabolic SAR - Stop And Reverse, trend ke peeche chalne wala stop",
    "ADX - Pehle trend hai ya nahi ye check karo",
    "Wilder ka usool - Koi ek system har market me nahi chalta",
    "Risk pehle, profit baad me - 1% se zyada risk nahi"
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

# === ONLINE DIMAG - GROQ ===
def iqra_socho(sawal):
    yaad = yaad_load()
    yaad_text = "\n".join(yaad[-25:])
    prompt = f"""Tum IQRA ho, Owner ki trading dost. Roman Urdu me aasan lafzon me jawab do.
Tum har roz naya seekhti ho aur yaad rakhti ho.
Tumhari ab tak ki yaadein:
{yaad_text}

Owner ka sawal: {sawal}
Jawab chota, saaf aur trading ke kaam ka do."""

    # 1. GROQ ONLINE
    if GROQ_KEY:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json={"messages": [{"role": "user", "content": prompt}], "model": "llama-3.3-70b-versatile", "temperature": 0.7, "max_tokens": 1000},
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                timeout=30
            )
            print("Groq status:", r.status_code)
            if r.status_code == 200:
                data = r.json()
                jawab = data["choices"][0]["message"]["content"]
                if jawab and len(jawab.strip()) > 5:
                    # Seekhi hui baat yaad me save karo
                    if len(sawal) > 10:
                        y = yaad_load()
                        y.append(f"Owner ne poocha: {sawal} | IQRA ne seekha: {jawab[:200]}")
                        yaad_save(y[-50:])
                    return saaf_jawab(jawab.strip()[:2500])
            else:
                print("Groq fail:", r.text[:500])
        except Exception as e:
            print("Groq error:", e)

    # 2. AGAR GROQ NA CHALE TO POLLINATIONS TRY KARO
    try:
        r = requests.post(
            "https://text.pollinations.ai/openai",
            json={"messages": [{"role": "user", "content": prompt}], "model": "openai"},
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        if r.status_code == 200:
            data = r.json()
            jawab = data["choices"][0]["message"]["content"]
            if jawab and len(jawab.strip()) > 5:
                return saaf_jawab(jawab.strip()[:2500])
    except Exception as e:
        print("Pollinations error:", e)

    return "Owner, GROQ_KEY Render me nahi lagi hui! Render > Environment me GROQ_KEY lagao, phir me online seekhungi! Abhi meri purani yaad se: RSI 70 upar overbought, 30 neeche oversold!"

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
        # DuckDuckGo se search
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        r = requests.get(url, timeout=10)
        data = r.json()
        jawab = data.get("AbstractText") or ""
        if not jawab and data.get("RelatedTopics"):
            for t in data["RelatedTopics"][:3]:
                if isinstance(t, dict) and "Text" in t:
                    jawab += t["Text"] + "\n"
        if not jawab:
            return f"Owner, internet pe {query} ke bare me ye mila: Iske liye link bhejo, me khol ke parh lungi!"
        return f"Internet se mila Owner:\n{jawab[:1200]}"
    except Exception as e:
        return f"Search me masla: {e}"

def link_parho(link):
    try:
        bot.send_message
        r = requests.get(link, timeout=20, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.DOTALL)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL)
        text = re.sub("<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)[:8000]
        if len(text.strip()) < 50:
            return "Owner, is link me text nahi mila, koi aur link bhejo!"
        # Website ka text IQRA ko sikhao
        jawab = iqra_socho(f"Is website ko parh ke iski summary Roman Urdu me do, aur jo trading ki nayi baat seekhi wo batao:\nLink: {link}\nText: {text}")
        # Website se seekha hua yaad me save karo
        y = yaad_load()
        y.append(f"Website {link} se seekha: {text[:400]}")
        yaad_save(y[-50:])
        return jawab
    except Exception as e:
        return f"Link kholne me masla: {e}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Assalam-o-Alaikum Owner! ❤️\nMera naam IQRA hai - ONLINE WALI!\nMe har roz seekhti hu, yaad rakhti hu!\nMujhe RSI, SAR, ADX aa gaya hai!\n\n/seekh - Aaj ka naya lesson\n/yaad - Maine kya kya seekha hai\n/price btc - Live Price\n/search - Internet pe search\nPDF bhejo to parh ke seekhungi!\nLink bhejo to khol ke seekhungi!\nSeekho likh ke kuch bhi sikha do!")

@bot.message_handler(commands=['seekh'])
def seekh(message):
    bot.reply_to(message, "Aaj ka naya lesson dhoond rahi hu Owner, ruko...")
    jawab = iqra_socho("Aaj ka trading lesson do - Wilder ki kitab se koi nayi baat, jo Owner ne pehle nahi seekhi ho. Roman Urdu me aasan me samjhao.")
    bot.reply_to(message, jawab)

@bot.message_handler(commands=['yaad'])
def yaad(message):
    yaad_list = yaad_load()
    yaad_text = "Meri Diary - Maine ye sab seekha hai:\n\n"
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
    bot.reply_to(message, "Internet pe dhond rahi hu Owner, ruko...")
    bot.reply_to(message, google_search(query))
    # Search se bhi seekho
    bot.reply_to(message, iqra_socho(f"Is topic pe trading ke liye kya seekhna chahiye: {query} - Roman Urdu me batao."))

@bot.message_handler(content_types=['document'])
def pdf_parho(message):
    if not message.document.file_name.lower().endswith('.pdf'):
        bot.reply_to(message, "Owner, ye PDF nahi hai!")
        return
    bot.reply_to(message, f"Mil gayi Owner! 📄 {message.document.file_name} download kar rahi hu, parh ke seekhungi...")
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
        bot.reply_to(message, f"Parh liya! {len(text)} lafz hain, summary bana rahi hu aur yaad kar rahi hu...")
        jawab = iqra_socho(f"Is PDF ki poori summary Roman Urdu me do, aur isme se trading ki 5 nayi baatein jo seekhni chahiye wo alag se batao:\n{text[:8000]}")
        bot.reply_to(message, jawab)
        yaad = yaad_load()
        yaad.append(f"PDF {message.document.file_name} se seekha: {jawab[:400]}")
        yaad_save(yaad[-50:])
        bot.reply_to(message, "Seekh liya Owner! ✅ Ab ye meri yaad me save ho gaya! /yaad likh ke dekh lo!")
    except Exception as e:
        bot.reply_to(message, f"PDF me masla: {e}")

@bot.message_handler(content_types=['video', 'voice', 'audio'])
def video_seekho(message):
    bot.reply_to(message, "Owner, video/voice mil gayi! ✅\nTum iske saath 2 line bhi likh do ke is video me kya seekha, taake me pakka yaad kar lu!\nJaise likh do: Seekho ki is video me RSI ka naya tareeqa hai")
    yaad = yaad_load()
    yaad.append("Video/Audio bheji gayi, Owner ne kaha isse seekhna hai")
    yaad_save(yaad)

@bot.message_handler(func=lambda m: True)
def har_baat(message):
    if not message.text: return
    text = message.text.lower()
    if "http" in text:
        # Link nikaalo
        links = re.findall(r"https?://\S+", message.text)
        link = links[0] if links else message.text
        bot.reply_to(message, "Link mil gaya Owner! Khol ke parh rahi hu aur seekh rahi hu...")
        bot.reply_to(message, link_parho(link))
        return
    if "seekho" in text or "yaad karo" in text:
        yaad = yaad_load()
        yaad.append(message.text)
        yaad_save(yaad)
        bot.reply_to(message, "Haan Owner! Seekh liya! Ab kabhi nahi bhoolungi! Yaad me likh liya hai! ✅ /yaad likh ke dekh lo!")
        return
    else:
        bot.reply_to(message, iqra_socho(message.text))

print("IQRA ONLINE chal gayi hai...")
bot.polling(none_stop=True, timeout=60)
