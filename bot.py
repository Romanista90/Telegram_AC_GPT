import os
import openai
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# Получаем токены из переменных окружения
OPENAI_API_KEY = os.environ["TELEGRAM_GPT_OPENAI_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_GPT_TELEGRAM_TOKEN"]

openai.api_key = OPENAI_API_KEY

# Основной обработчик сообщений
def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text
    prompt = f"""На основе описания задачи предложи не меньше трёх критериев приёмки. Используй формат чеклиста или Given-When-Then. 

Описание задачи: {user_input}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )
        result = response.choices[0].message.content.strip()
        update.message.reply_text(result)
    except Exception as e:
        update.message.reply_text(f"Ошибка: {e}")

# Запуск бота
updater = Updater(token=TELEGRAM_TOKEN)
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

updater.start_polling()
updater.idle()

# Заглушка-порт, чтобы Render думал, что это веб-приложение
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_dummy_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, DummyServer)
    httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
