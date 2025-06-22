import os
import logging
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_GPT_TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("TELEGRAM_GPT_OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# Обработчик входящих сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    prompt = f"""
Ты — опытный продакт-менеджер. Сформулируй не менее трёх чётких и измеримых критериев приёмки на основе описания задачи ниже. Максимум не ограничен, но пиши полезные критерии, чтобы они помогали в приёмке, а не просто для количества.

Описание задачи:
{user_message}

Формат ответа:
- Критерий 1
- Критерий 2
...
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=500,
        )

        reply_text = response.choices[0].message.content.strip()
        await update.message.reply_text(reply_text)

    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        await update.message.reply_text("Произошла ошибка при генерации критериев. Попробуйте позже.")

# Основная функция запуска
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
