from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
import requests

BOT_TOKEN = "8818776406:AAFPC8Hxc6DlzSq7gcd9s3eAzUcqU8w7184"
GROQ_API_KEY = "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"
TAVILY_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)
conversations = {}
current_model = "llama-3.3-70b-versatile"

MODELS = ["llama-3.3-70b-versatile", "gemma2-9b-it", "llama-3.1-8b-instant"]

def get_weather(city="Lusaka"):
    lat, lon = -15.3875, 28.3228
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current_weather": True}
    res = requests.get(url, params=params)
    data = res.json()
    weather = data["current_weather"]
    return f"🌍 Weather in {city}\n\n🌡️ Temperature: {weather['temperature']}°C\n💨 Wind Speed: {weather['windspeed']} km/h\n🧭 Wind Direction: {weather['winddirection']}°"

def get_news(topic="world"):
    url = "https://newsapi.org/v2/everything"
    params = {"q": topic, "sortBy": "publishedAt", "apiKey": "demo", "pageSize": 3}
    res = requests.get(url, params=params)
    data = res.json()
    articles = data.get("articles", [])
    news = "📰 Latest News:\n\n"
    for article in articles[:3]:
        news += f"• {article['title']}\n"
    return news

def get_crypto(symbol="bitcoin"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    res = requests.get(url)
    data = res.json()
    price = data.get(symbol, {}).get("usd", "N/A")
    return f"💰 {symbol.upper()}: ${price}"

def get_quote():
    url = "https://api.quotable.io/random"
    res = requests.get(url)
    data = res.json()
    return f"💭 \"{data['content']}\"\n— {data['author']}"

def get_definition(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    res = requests.get(url)
    data = res.json()
    if isinstance(data, list) and len(data) > 0:
        definition = data[0]["meanings"][0]["definitions"][0]["definition"]
        return f"📖 {word}: {definition}"
    return "Word not found!"

def search_duckduckgo(query):
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json"}
    res = requests.get(url, params=params)
    data = res.json()
    results = data.get("Results", [])
    if results:
        return f"🔍 DuckDuckGo Results:\n\n" + "\n".join([f"• {r['Text']}" for r in results[:3]])
    return "No results found"

def get_location(place):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place, "format": "json"}
    res = requests.get(url, params=params)
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, params=params, headers=headers)
    data = res.json()
    if data:
        lat, lon = data[0]["lat"], data[0]["lon"]
        return f"📍 {place}\nLat: {lat}, Lon: {lon}"
    return "Location not found"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/weather /news /crypto /quote /search query /define word /map place")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_weather())

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_news())

async def crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_crypto())

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_quote())

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) if context.args else "zambia"
    result = search_duckduckgo(query)
    await update.message.reply_text(result)

async def map_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    place = " ".join(context.args) if context.args else "Lusaka"
    result = get_location(place)
    await update.message.reply_text(result)

async def define(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = " ".join(context.args) if context.args else "hello"
    result = get_definition(word)
    await update.message.reply_text(result)

async def model_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🤖 Currently using: {current_model}")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_model
    user_id = update.message.chat_id
    user_message = update.message.text or ""
    
    if user_id not in conversations:
        conversations[user_id] = []
    
    conversations[user_id].append({"role": "user", "content": user_message})
    
    reply = None
    for model in MODELS:
        try:
            response = client.chat.completions.create(model=model, messages=conversations[user_id], max_tokens=300)
            reply = response.choices[0].message.content
            current_model = model
            break
        except Exception:
            continue
    
    if not reply:
        reply = "I'm overloaded! 😔"
    
    conversations[user_id].append({"role": "assistant", "content": reply})
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("weather", weather))
app.add_handler(CommandHandler("news", news))
app.add_handler(CommandHandler("crypto", crypto))
app.add_handler(CommandHandler("quote", quote))
app.add_handler(CommandHandler("search", search))
app.add_handler(CommandHandler("map", map_search))
app.add_handler(CommandHandler("define", define))
app.add_handler(CommandHandler("model", model_info))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
