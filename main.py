from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
import requests

BOT_TOKEN = "8818776406:AAFPC8Hxc6DlzSq7gcd9s3eAzUcqU8w7184"
GROQ_API_KEY = "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")
TAVILY_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)
conversations = {}

def web_search(query):
    response = requests.post(
        "https://api.tavily.com/search",
        json={"api_key": TAVILY_API_KEY, "query": query, "max_results": 3}
    )
    results = response.json().get("results", [])
    return "\n".join([r["content"] for r in results])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I can search the web too! 🌐")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_message = update.message.text

    if user_id not in conversations:
        conversations[user_id] = []

    search_results = web_search(user_message)
    
    conversations[user_id].append({
        "role": "user",
        "content": f"{user_message}\n\nWeb search results:\n{search_results}"
    })

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=conversations[user_id],
        max_tokens=1000
    )

    reply = response.choices[0].message.content
    conversations[user_id].append({"role": "assistant", "content": reply})
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
