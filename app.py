from flask import Flask, request
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook

from data.config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from loader import dp, db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


# Flask app for keep_alive
app = Flask(__name__)

@app.route('/')
def index():
    return "Alive"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()


# Telegram bot webhook settings
WEBHOOK_PATH = "/webhook"  # yo'l webhook uchun (bu sizning API tokeningiz bilan yoki boshqa bo'lishi mumkin)
WEBHOOK_URL = "https://chatbot-xoti.onrender.com/" + WEBHOOK_PATH  # O'zgartiring o'z domeningizga yoki render domeniga

WEBAPP_HOST = "0.0.0.0"  # server IP
WEBAPP_PORT = 8080       # server port


async def on_startup(dispatcher):
    # webhook uchun botni webhook urlga ulash
    await bot.set_webhook(WEBHOOK_URL)

    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)

    # Bazani yaratish
    db.create_table_users()
    db.create_table_status()
    db.create_table_active_replies()
    db.create_replies_table()


async def on_shutdown(dispatcher):
    # webhook o'chirilishini ta'minlash
    await bot.delete_webhook()


if __name__ == '__main__':
    keep_alive()  # Flask serverni ishga tushir

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)

    # Aiogram uchun webhookni ishga tushurish
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
