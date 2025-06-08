from aiogram import executor
from data.config import BOT_TOKEN
from flask import Flask
import os

app = Flask(__name__)

@app.route('/', methods=['POST'])  # <-- MUHIM: POST method ruxsat berilgan
def webhook():
    data = request.get_json()
    print("Telegramdan kelgan:", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        reply = f"You said: {text}"

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": reply
        }

        requests.post(url, json=payload)

    return 'ok', 200

from loader import dp, db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands

async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)

    db.create_table_users()
    db.create_table_status()
    db.create_table_active_replies()
    db.create_replies_table()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
