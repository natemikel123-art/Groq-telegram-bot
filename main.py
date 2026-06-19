import requests
import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import google.generativeai as genai
# ================== KEYS ==================
BOT_TOKEN = "8818776406:AAGcgdVE1aL6My5pLNfNFf7bQnjeg6WmdWg"
TAVILY_API_KEY = "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"
GEMINI_API_KEY = "AQ.Ab8RN6LeCc4n7QccemEM1pkVEf0EAkkYOxIlARViU7UmHaXm7Q"
genai.configure(api_key=GEMINI_API_KEY)
# ================== MEMORY ==================
MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

memory = load_memory()

def get_user(user_id):
    if str(user_id) not in memory:
        memory[str(user_id)] = {
            "messages": [],
            "facts": {}
        }
    return memory[str(user_id)]

def update_memory(user_id, user_text, bot_reply):
    user = get_user(user_id)

    user["messages"].append({
        "user": user_text,
        "bot": bot_reply
    })

    user["messages"] = user["messages"][-10:]
    save_memory(memory)

# ================== FACT EXTRACTION ==================
def extract_facts(user_id, text):
    user = get_user(user_id)
    t = text.lower()

    if "my name is" in t:
        user["facts"]["name"] = text.split("my name is")[-1].strip()

    if "i like" in t:
        user["facts"]["likes"] = text.split("i like")[-1].strip()

    if "i live in" in t:
        user["facts"]["location"] = text.split("i live in")[-1].strip()

    save_memory(memory)

# ================== WEATHER ==================
def get_weather(city="Lusaka"):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": -15.3875,
        "longitude": 28.3228,
        "current_weather": True
    }

    res = requests.get(url, params=params).json()
    w = res["current_weather"]

    return f"""🌤 Weather in {city}

🌡 Temp: {w['temperature']}°C
💨 Wind: {w['windspeed']} km/h
🧭 Direction: {w['winddirection']}°
"""

# ================== TAVILY SEARCH ==================
def web_search(query):
    url = "https://api.tavily.com/search"

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": 3
    }

    data = requests.post(url, json=payload).json()
    results = data.get("results", [])

    if not results:
        return "No results found 😔"

    text = "🔍 Search Results:\n\n"

    for r in results:
        text += f"{r['title']}\n{r['url']}\n\n"

    return text

# ================== MUSIC (FREE DUCKDUCKGO) ==================
def music_search(query):
    url = "https://duckduckgo.com/"

    params = {
        "q": query + " music youtube"
    }

    # simple search link generator (no API key)
    return f"""🎵 Music Search

Search here:
https://duckduckgo.com/?q={query.replace(' ', '+')}+music+youtube
"""

# ================== GROQ AI ==================
def ask_ai(user_id, prompt):
    try:
        user = get_user(user_id)

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "You are a helpful Telegram assistant."},
                {"role": "user", "content": prompt}
            ]
        }

        res = requests.post(url, headers=headers, json=data)

        print("GROQ STATUS:", res.status_code)
        print("GROQ RESPONSE:", res.text)

        data = res.json()

        # 🔥 SAFE CHECK (IMPORTANT)
        if "choices" not in data:
            return f"Groq error: {data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("GROQ EXCEPTION:", e)
        return "AI error 😔 check logs"
# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 AI Bot Online\n\nTalk normally:\n- weather\n- search anything\n- music name\n- chat with AI"
    )

# ================== CHAT ==================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        text = update.message.text

        extract_facts(user_id, text)

        t = text.lower()

        if "weather" in t:
            reply = get_weather()

        elif t.startswith("search "):
            reply = web_search(text[7:])

        elif "music" in t:
            song = text.replace("music", "").strip()
            reply = music_search(song)

        else:
            reply = ask_ai(user_id, text)

        update_memory(user_id, text, reply)

        await update.message.reply_text(reply)

    except Exception as e:
        print("ERROR:", e)
        await update.message.reply_text("Bot error happened 😔 check logs")
# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🔥 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
