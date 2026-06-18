from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

BOT_TOKEN = "8818776406:AAFPC8Hxc6DlzSq7gcd9s3eAzUcqU8w7184"
client = Groq(api_key="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") 
conversations = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! How can I help you?")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_message = update.message.text

    if user_id not in conversations:
        conversations[user_id] = []

    conversations[user_id].append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
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
