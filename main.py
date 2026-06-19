from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
import requests
import base64

BOT_TOKEN = "8818776406:AAFPC8Hxc6DlzSq7gcd9s3eAzUcqU8w7184"
GROQ_API_KEY = "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"
TAVILY_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)
conversations = {}
current_model = "llama-3.3-70b-versatile"

MODELS = ["llama-3.3-70b-versatile", "gemma2-9b-it", "llama-3.1-8b-instant"]

def web_search(query):
    if any(word in query.lower() for word in ["exchange", "kwacha", "rate"]):
        query = "USD ZMW exchange rate today site:xe.com"
    else:
        query = query + " 2026 current today"
    response = requests.post("https://api.tavily.com/search", json={"api_key": TAVILY_API_KEY, "query": query, "max_results": 3, "search_depth": "advanced", "topic": "news"})
    results = response.json().get("results", [])
    return "\n".join([r["content"][:300] for r in results])

def needs_search(message):
    keywords = ["today", "current", "latest", "news", "2024", "2025", "2026", "who won", "what happened", "price of", "weather", "exchange", "kwacha", "rate"]
    return any(word in message.lower() for word in keywords)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! How can I help you?")

async def model_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🤖 Currently using: {current_model}")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_model
    user_id = update.message.chat_id
    user_message = update.message.text or ""
    
    if user_id not in conversations:
        conversations[user_id] = []
    
    if needs_search(user_message):
        search_results = web_search(user_message)
        content = f"{user_message}\n\nWeb results:\n{search_results}"
    else:
        content = user_message
    
    conversations[user_id].append({"role": "user", "content": content})
    
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
        reply = "I'm overloaded, try again later! 😔"
    
    conversations[user_id].append({"role": "assistant", "content": reply})
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("model", model_info))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
