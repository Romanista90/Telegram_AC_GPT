import os
import logging
import asyncio
import openai
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_GPT_TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("TELEGRAM_GPT_OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")

# Проверка переменных
if not all([TELEGRAM_TOKEN, OPENAI_API_KEY, WEBHOOK_URL]):
    raise ValueError("Не заданы необходимые переменные окружения.")

# Инициализация
openai.api_key = OPENAI_API_KEY
application = Application.builder().token(TELEGRAM_TOKEN).build()
flask_app = Flask(__name__)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне описание задачи, и я сгенерирую критерии приёмки.")

# Ответ на сообщение
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты помогаешь писать критерии приёмки на основе описания задачи. Формулируй их в виде маркированного списка. Критериев должно быть не меньше трёх."},
                {"role": "user", "content": description}
            ]
        )
        await update.message.reply_text(response.choices[0].message.content.strip())
    except Exception as e:
        logger.exception("Ошибка при генерации ответа")
        await update.message.reply_text("Произошла ошибка при генерации ответа от OpenAI.")

# Обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook (асинхронно!)
@flask_app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
async def telegram_webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.exception("Ошибка при обработке запроса от Telegram")
    return "OK"

# Запуск
if __name__ == "__main__":
    async def run():
        await application.initialize()
        await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook/{TELEGRAM_TOKEN}")
        await application.start()
        logger.info("Бот запущен и webhook установлен.")
        # Flask запускается в отдельном потоке
        from threading import Thread
        Thread(target=lambda: flask_app.run(host="0.0.0.0", port=10000)).start()
        await asyncio.Event().wait()  # держим процесс живым

    asyncio.run(run())
