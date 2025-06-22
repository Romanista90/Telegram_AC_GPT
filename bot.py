import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)
from openai import OpenAI

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ключи
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_GPT_TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("TELEGRAM_GPT_OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"  # Можно gpt-3.5-turbo, если хочешь дешевле

openai = OpenAI(api_key=OPENAI_API_KEY)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне описание задачи, и я сгенерирую критерии приёмки.")

# Обработка обычного текста
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text("Генерирую критерии приёмки...")

    response = openai.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "Ты опытный аналитик. На основе описания задачи генерируй критерии приёмки (acceptance criteria) в формате списка."},
            {"role": "user", "content": prompt}
        ]
    )

    criteria = response.choices[0].message.content
    await update.message.reply_text(criteria)

# Запуск приложения с Webhook
async def main():
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .read_timeout(10)
        .write_timeout(10)
        .get_updates_http_version("1.1")
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))  # alias
    app.add_handler(CommandHandler("criteria", handle_message))  # опционально
    app.add_handler(CommandHandler("acceptance", handle_message))  # опционально

    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Webhook
    webhook_url = os.environ.get("WEBHOOK_URL")  # Добавим на Render
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
