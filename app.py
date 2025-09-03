from aiogram import executor
from data.config import BOT_TOKEN
from keep_alive import keep_alive
from loader import dp, db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
keep_alive()


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)
    db.create_admins_table()
    db.create_table_users()
    db.create_table_status()
    db.create_reply_sessions_table()
    db.create_uuid_to_user_table()
    db.create_referrals_table()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
