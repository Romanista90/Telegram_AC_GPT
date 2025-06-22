import os
import logging
import openai
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Переменные окружения
BOT_TOKEN = os.getenv("TELEGRAM_GPT_TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("TELEGRAM_GPT_OPENAI_API_KEY")
WEBHOOK_DOMAIN = os.getenv("TELEGRAM_GPT_WEBHOOK_DOMAIN")  # например, https://your-app.onrender.com

# Инициализация Flask
app = Flask(__name__)

# OpenAI
openai.api_key = OPENAI_KEY

# Telegram bot
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне описание задачи, и я сгенерирую критерии приёмки.")

# Обработка текста
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
        logging.exception("Ошибка при обращении к OpenAI")
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

# Добавляем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask route
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

# Установка webhook при старте (однократно)
@app.before_request
def set_webhook():
    url = f"{WEBHOOK_DOMAIN}/webhook/{BOT_TOKEN}"
    application.bot.set_webhook(url)
    logging.info(f"Webhook установлен: {url}")

# Запуск Flask-сервера
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
