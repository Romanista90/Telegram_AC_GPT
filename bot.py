import os
import logging
import openai
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_GPT_TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("TELEGRAM_GPT_OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")

openai.api_key = OPENAI_API_KEY
flask_app = Flask(__name__)
application = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне описание задачи, и я сгенерирую критерии приёмки.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты помогаешь писать критерии приёмки на основе описания задачи. Формулируй их в виде маркированного списка. Действуй как опытный аналитик или продакт. Критериев должно быть не меньше трёх, максимум не ограничен, но пиши только полезные критерии, пиши вдумчиво."},
                {"role": "user", "content": description}
            ]
        )
        result = response.choices[0].message.content.strip()
        await update.message.reply_text(result)
    except Exception as e:
        logger.exception("Ошибка при генерации ответа")
        await update.message.reply_text(f"Произошла ошибка: {e}")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@flask_app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
async def telegram_webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.exception("Ошибка при обработке запроса от Telegram")
    return "OK"

if __name__ == "__main__":
    import asyncio
    from threading import Thread

    async def main():
        await application.initialize()
        await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook/{TELEGRAM_TOKEN}")
        await application.start()
        Thread(target=lambda: flask_app.run(host="0.0.0.0", port=10000)).start()

    asyncio.run(main())
