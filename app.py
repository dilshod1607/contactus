from aiogram import executor
import os



from loader import dp, db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
port = int(os.environ.get("PORT", 5000))

app.run(host='0.0.0.0', port=port)

async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)

    db.create_table_users()
    db.create_table_status()
    db.create_table_active_replies()
    db.create_replies_table()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
