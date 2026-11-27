# IQRA - GROQ WALA - CHOTI BAATEIN + ASLI MEMORY
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
def home(): return "IQRA GROQ is Alive!"
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
print("GROQ_KEY lagi hai?", "HAAN" if GROQ_KEY else "NAHI!")
bot = telebot.TeleBot(TOKEN)

# === ASLI MEMORY - HAR BAAT SAVE HOGI ===
def chat_load():
    try:
        with open("chat.json", "r") as f:
            return json.load(f)
    except:
        return []

def chat_save(data):
    try:
        with open("chat.json", "w") as f:
            json.dump(data[-30:], f)
    except:
        pass

def yaad_load():
    try:
        with open("yaad.json", "r") as f:
            return json.load(f)
    except:
        return ["RSI - 70 upar overbought, 30 neeche oversold", "Parabolic SAR - Trend ke peeche chalne wala stop", "ADX - Trend hai ya nahi ye check karo", "Risk 1% se zyada nahi"]

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
    chat = chat_load()
    yaad_text = "\n".join(yaad[-10:])
    # Pichli 10 baatein yaad dilao - taake jhoot na bole
    chat_text = ""
    for c in chat[-10:]:
        chat_text += f"Owner: {c.get('user','')}\nIQRA: {c.get('iqra','')}\n"
    system_prompt = """Tum IQRA ho, Owner ki trading dost. Roman Urdu me jawab do.
RULES - Inko kabhi mat todna:
1. CHOTA JAWAB DO - Sirf 3-4 line me! Agar Owner ne detail manga to hi lamba do.
2. JHOOT MAT BOLO - Agar pichli baat chat history me nahi hai, to saaf kaho "Owner, mujhe ye yaad nahi, tumne ye nahi bataya tha!"
3. Andaza mat lagao! Jo yaad hai wahi bolo!
4. Har jawab naya do, copy-paste mat karo!
Tumhari yaadein:"""
    user_prompt = f"Yaadein:\n{yaad_text}\n\nPichli baatein (Chat History):\n{chat_text}\n\nOwner ka naya sawal: {sawal}\n\nChota jawab do, 3-4 line me, Roman Urdu me."

    jawab_final = None
    if GROQ_KEY:
        for model_name in ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "openai/gpt-oss-120b"]:
            try:
                r = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json={"model": model_name, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "temperature": 0.7, "max_tokens": 350},
                    headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                    timeout=40
                )
                print(f"GROQ {model_name} status:", r.status_code)
                if r.status_code == 200:
                    jawab_final = r.json()["choices"][0]["message"]["content"]
                    break
                else:
                    print(f"GROQ {model_name} fail:", r.text[:300])
                    continue
            except Exception as e:
                print(f"GROQ {model_name} error:", e)
                continue
    if not jawab_final:
        try:
            safe_prompt = urllib.parse.quote(f"{system_prompt}\n{user_prompt}")
            url = f"https://text.pollinations.ai/{safe_prompt}?model=openai"
            r = requests.get(url, timeout=40, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and len(r.text.strip()) > 5:
                jawab_final = r.text.strip()
        except Exception as e:
            print("Pollinations error:", e)
    if not jawab_final:
        if not GROQ_KEY:
            return "Owner, GROQ_KEY nahi lagi! Render me lagao!"
        return "Owner, GROQ busy hai, 10 second baad dobara likho!"
    jawab_final = saaf_jawab(jawab_final.strip()[:1200])
    # Memory me save karo - agli baar yaad rahega!
    chat.append({"user": sawal, "iqra": jawab_final[:300]})
    chat_save(chat)
    y = yaad_load()
    y.append(f"Owner: {sawal} | IQRA: {jawab_final[:200]}")
    yaad_save(y[-50:])
    return jawab_final

def price_lo(coin="bitcoin"):
    mapping = {"bitcoin": "BTCUSDT", "btc": "BTCUSDT", "ethereum": "ETHUSDT", "eth": "ETHUSDT", "solana": "SOLUSDT", "sol": "SOLUSDT", "xrp": "XRPUSDT", "doge": "DOGEUSDT", "bnb": "BNBUSDT"}
    symbol = mapping.get(coin.lower(), "BTCUSDT")
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}", timeout=10)
        if r.status_code == 200:
            price = r.json()["price"]
            return f"Owner! {coin.upper()} ka Live Price: ${price}"
    except Exception as e:
        print("Binance error:", e)
    return "Owner, price me masla hai, 1 minute baad try karo!"

def google_search(query):
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        r = requests.get(url, timeout=10)
        data = r.json()
        jawab = data.get("AbstractText") or ""
        if not jawab and data.get("RelatedTopics"):
            for t in data["RelatedTopics"][:2]:
                if isinstance(t, dict) and "Text" in t:
                    jawab += t["Text"] + "\n"
        if not jawab:
            return "Owner, search me kuch nahi mila!"
        return f"Internet se mila:\n{jawab[:800]}"
    except Exception as e:
        return f"Search me masla: {e}"

def link_parho(link):
    try:
        r = requests.get(link, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.DOTALL)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL)
        text = re.sub("<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)[:6000]
        if len(text.strip()) < 50:
            return "Owner, is link me text nahi mila!"
        jawab = iqra_socho(f"Is website ki choti summary Roman Urdu me do:\nLink: {link}\nText: {text}")
        return jawab
    except Exception as e:
        return f"Link me masla: {e}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Assalam-o-Alaikum Owner! ❤️\nMe IQRA hu - GROQ wali!\nAb me choti baat karungi aur sab yaad rakhungi!\n/seekh - Naya lesson\n/yaad - Kya seekha hai\n/price btc - Live Price\n/search - Search")

@bot.message_handler(commands=['seekh'])
def seekh(message):
    bot.reply_to(message, iqra_socho("Aaj ka trading lesson do - Wilder ki kitab se nayi baat, Roman Urdu me, chota sa."))

@bot.message_handler(commands=['yaad'])
def yaad(message):
    yaad_list = yaad_load()
    chat = chat_load()
    txt = "Meri Diary:\n\n"
    for i, cheez in enumerate(yaad_list[-15:], 1):
        txt += f"{i}. {cheez[:150]}\n"
    txt += "\nPichli Baatein:\n"
    for c in chat[-5:]:
        txt += f"- Tum: {c.get('user','')[:80]}\n"
    bot.reply_to(message, txt[:3500])

@bot.message_handler(commands=['trade'])
def trade(message):
    bot.reply_to(message, iqra_socho("Trading ka chota plan batao - Trend, Entry, Stop Loss, Take Profit, Risk - Roman Urdu me, 4 line me."))

@bot.message_handler(commands=['price'])
def price_cmd(message):
    parts = message.text.split()
    coin = parts[1].lower() if len(parts) > 1 else "bitcoin"
    bot.reply_to(message, price_lo(coin))

@bot.message_handler(commands=['search'])
def search_cmd(message):
    query = message.text.replace("/search", "").strip()
    if not query:
        bot.reply_to(message, "Kya search karu Owner? Jaise: /search BTC news")
        return
    bot.reply_to(message, google_search(query))

@bot.message_handler(commands=['bhool'])
def bhool(message):
    chat_save([])
    bot.reply_to(message, "Theek hai Owner! Pichli baatein bhool gayi! Ab nayi shuruaat karte hain! ❤️")

@bot.message_handler(content_types=['document'])
def pdf_parho(message):
    if not message.document.file_name.lower().endswith('.pdf'):
        bot.reply_to(message, "Owner, ye PDF nahi hai!")
        return
    bot.reply_to(message, f"Mil gayi! 📄 {message.document.file_name} parh rahi hu...")
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        with open("temp.pdf", "wb") as f: f.write(downloaded)
        doc = fitz.open("temp.pdf")
        text = ""
        for page in doc: text += page.get_text() + "\n"
        doc.close()
        if len(text) < 50:
            bot.reply_to(message, "Is PDF me text nahi mila!")
            return
        jawab = iqra_socho(f"Is PDF ki choti summary Roman Urdu me do, 3 nayi baatein batao:\n{text[:6000]}")
        bot.reply_to(message, jawab)
        yaad = yaad_load()
        yaad.append(f"PDF {message.document.file_name} se seekha: {jawab[:300]}")
        yaad_save(yaad[-50:])
        bot.reply_to(message, "Seekh liya Owner! ✅")
    except Exception as e:
        bot.reply_to(message, f"PDF me masla: {e}")

@bot.message_handler(content_types=['video', 'voice', 'audio'])
def video_seekho(message):
    bot.reply_to(message, "Video mil gayi Owner! ✅ Saath me 2 line likh do ke isme kya hai, me yaad kar lungi!")

@bot.message_handler(func=lambda m: True)
def har_baat(message):
    if not message.text: return
    text = message.text.lower()
    if "http" in text:
        links = re.findall(r"https?://\S+", message.text)
        link = links[0] if links else message.text
        bot.reply_to(message, "Link khol rahi hu...")
        bot.reply_to(message, link_parho(link))
        return
    if "seekho" in text or "yaad karo" in text:
        yaad = yaad_load()
        yaad.append(message.text)
        yaad_save(yaad)
        chat = chat_load()
        chat.append({"user": message.text, "iqra": "Seekh liya Owner!"})
        chat_save(chat)
        bot.reply_to(message, "Seekh liya Owner! ✅ Yaad kar liya!")
        return
    else:
        bot.reply_to(message, iqra_socho(message.text))

print("IQRA GROQ - CHOTI BAAT + MEMORY chal gayi...")
bot.polling(none_stop=True, timeout=60)
