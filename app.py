import asyncio
from loader import dp, db, bot
db.create_admins_table()
db.create_requests_table()
from keep_alive import keep_alive
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from aiogram import executor

# Flask parallel ishlashi uchun ishga tushiramiz
keep_alive()

async def on_startup(dispatcher):
    # Bot komandalarini va admin notification ishga tushadi
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)
    # Sync DB operatsiyalar
    db.create_admins_table()


if __name__ == "__main__":
    # Aiogram bot polling
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
