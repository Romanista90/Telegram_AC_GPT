import os
import logging
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Токены
TELEGRAM_TOKEN = os.getenv("TELEGRAM_GPT_TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("TELEGRAM_GPT_OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text

    # Генерация ответа через OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # или другой доступный тебе
            messages=[
                {
                    "role": "system",
                    "content": "Ты помощник, который помогает формулировать критерии приёмки по описанию задачи."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )
        reply_text = response["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        reply_text = "Произошла ошибка при обращении к OpenAI."

    await update.message.reply_text(reply_text)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()
