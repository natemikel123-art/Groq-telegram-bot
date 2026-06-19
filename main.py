from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
import requests

BOT_TOKEN = "8818776406:AAGcgdVE1aL6My5pLNfNFf7bQnjeg6WmdWg"
GROQ_API_KEY = "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"
SERPAPI_KEY = "1016ce29db72568f1e28438ec78486dee178eb6b80cc56ac9cd16e1d51fd6b25"

client = Groq(api_key=GROQ_API_KEY)
conversations = {}

def web_search(query):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": "your_serpapi_key",
        "engine": "google"
    }
    response = requests.get(url, params=params)
    results = response.json().get("organic_results", [])
    if results:
        return "\n".join([f"• {r['title']}\n{r['snippet']}" for r in results[:2]])
    return "No results found"

def needs_search(message):
    keywords = ["today", "current", "latest", "news", "2024", "2025", "2026", "who won", "what happened", "price of", "weather"]
    return any(word in message.lower() for word in keywords)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm Astro BOT, developed by Nate 🤖")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_message = update.message.text
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_message = update.message.text

    # Ignore messages with links
    if user_message and ("http" in user_message or "t.me" in user_message):
        await update.message.reply_text("I don't process links, just ask me questions! 😊")
        return

    if user_id not in conversations:
        conversations[user_id] = []
    # ... rest of code
    if user_id not in conversations:
        conversations[user_id] = []

    if needs_search(user_message):
        search_results = web_search(user_message)
        content = f"{user_message}\n\nWeb results:\n{search_results}"
    else:
        content = user_message

    conversations[user_id].append({"role": "user", "content": content})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are ASTRO, a helpful AI assistant from Zambia. You're friendly, use emojis, and respond in a casual way. You love talking about Zambia, tech, and gaming."},
            *conversations[user_id]
        ],
        max_tokens=500
    )

    reply = response.choices[0].message.content
    conversations[user_id].append({"role": "assistant", "content": reply})
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
