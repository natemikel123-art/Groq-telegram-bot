from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
import requests

BOT_TOKEN = "8818776406:AAGcgdVE1aL6My5pLNfNFf7bQnjeg6WmdWg"
GROQ_API_KEY = "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"
TAVILY_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)
conversations = {}

def web_search(query):
    response = requests.post(
        "https://api.tavily.com/search",
        json={"api_key": TAVILY_API_KEY, "query": query, "max_results": 2}
    )
    results = response.json().get("results", [])
    return "\n".join([r["content"][:300] for r in results])

def needs_search(message):
    keywords = ["today", "current", "latest", "news", "2024", "2025", "2026", "who won", "what happened", "price of", "weather"]
    return any(word in message.lower() for word in keywords)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! How can I help you?")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_message = update.message.text

    if user_id not in conversations:
        conversations[user_id] = []

    if needs_search(user_message):
        search_results = web_search(user_message)
        content = f"{user_message}\n\nWeb results:\n{search_results}"
    else:
        content = user_message

    conversations[user_id].append({"role": "user", "content": content})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=conversations[user_id],
        max_tokens=500
    )

    reply = response.choices[0].message.content
    conversations[user_id].append({"role": "assistant", "content": reply})
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
