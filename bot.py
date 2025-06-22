import os
import logging
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Установка ключа OpenAI
openai.api_key = os.getenv("TELEGRAM_GPT_OPENAI_API_KEY")

# Обработка команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне описание задачи, и я сгенерирую критерии приёмки."
    )

# Обработка текста пользователя
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Ты помогаешь писать критерии приёмки на основе описания задачи. Формулируй их в виде маркированного списка. Действуй как опытный аналитик или продакт. Критериев должно быть не меньше трёх, максимум не ограничен, но пиши только полезные критерии, пиши вдумчиво."
                },
                {
                    "role": "user",
                    "content": description
                }
            ]
        )

        result = response.choices[0].message.content.strip()
        await update.message.reply_text(result)

    except Exception as e:
        logging.exception("Ошибка при обращении к OpenAI")
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

# Основной запуск
if __name__ == '__main__':
    TOKEN = os.getenv("TELEGRAM_GPT_TELEGRAM_TOKEN")
    if not TOKEN:
        raise ValueError("Не установлен TELEGRAM_GPT_TELEGRAM_TOKEN")

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()
