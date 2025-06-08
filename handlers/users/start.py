import uuid

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import CHANNELS
from loader import dp, db, bot

uuid_to_user = {}  # {uuid_str: user_id}
reply_sessions = {}  # {sender_id: receiver_id}


def showChannels():
    keyboard = InlineKeyboardMarkup(row_width=1)

    for channel in CHANNELS:
        btn = InlineKeyboardButton(text=channel[0], url=channel[2])  # Assuming channel[1] is a URL
        keyboard.insert(btn)

    return keyboard


def generate_ref_link(user_id: int) -> str:
    bot_username = "chatmessangerbot"
    # Avvaldan bor UUIDni topamiz yoki yangi yaratamiz
    for code, uid in uuid_to_user.items():
        if uid == user_id:
            return f"https://t.me/{bot_username}?start={code}"
    new_code = uuid.uuid4().hex[:14]
    uuid_to_user[new_code] = user_id
    return f"https://t.me/{bot_username}?start={new_code}"


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user_status = db.select_user(user_id=message.from_user.id)
    sender_id = message.from_user.id
    if not user_status:
        db.add_user(
            user_id=sender_id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )

        count = db.count_users()
        await bot.send_message(chat_id='-1002106389662',
                               text="<b>🆕 Yangi foydalanuvchi!</b>\n"
                                    f"<b>🧑🏻 Ism:</b> {message.from_user.get_mention()}\n"
                                    f"<b>🌐 Username:</b> @{message.from_user.username}\n"
                                    f"<b>🆔 User ID:</b> [<code>{sender_id}</code>]\n"
                                    f"➖➖➖➖➖➖➖➖\n"
                                    f"<b>⚙️ Umumiy:</b> {count[0]} ta")

        try:
            active = db.select_active()[0]
            db.update_active(active=active + 1)
        except:
            db.add_status(active=1)

    args = message.get_args()
    if args:  # Referal orqali kelgan bo‘lsa
        if args in uuid_to_user:
            receiver_id = uuid_to_user[args]
            if receiver_id != sender_id:  # O'zining ssilkasi emasligiga ishonch
                keyboard = InlineKeyboardMarkup().add(
                    InlineKeyboardButton("Xabar yuborish", callback_data=f"send_once:{receiver_id}")
                )
                await message.answer("Habaringizni shu yerda qoldiring.", reply_markup=keyboard)
                return

    # Foydalanuvchiga har doim shaxsiy havolasini yuborish
    ref_link = generate_ref_link(sender_id)
    await message.answer(f"Sizning shaxsiy havolangiz:\n\n{ref_link}", reply_markup=showChannels())


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("send_once:"))
async def handle_send_once(callback: types.CallbackQuery):
    receiver_id = int(callback.data.split(":")[1])
    sender_id = callback.from_user.id

    if receiver_id == sender_id:
        await callback.message.answer("O‘zingizga xabar yuborolmaysiz.")
        await callback.answer()
        return

    reply_sessions[sender_id] = receiver_id
    await callback.message.answer("Habaringingizni shu yerda qoldiring.")
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("reply_to:"))
async def handle_reply_to(callback: types.CallbackQuery):
    receiver_id = int(callback.data.split(":")[1])
    sender_id = callback.from_user.id

    if receiver_id == sender_id:
        await callback.message.answer("O‘zingizga yozolmaysiz.")
        return

    reply_sessions[sender_id] = receiver_id
    await callback.message.answer("Habaringingizni shu yerda qoldiring.")
    await callback.answer()  # <-- bu ham muhim!


@dp.message_handler(lambda message: not message.text.startswith(('/', '!', '.')))
async def handle_reply(message: types.Message):
    sender_id = message.from_user.id

    if sender_id in reply_sessions:
        receiver_id = reply_sessions.pop(sender_id)

        # Javob tugmasi bilan keyboard
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Javob yozish", callback_data=f"reply_to:{sender_id}")
        )

        await bot.send_message(
            receiver_id,
            f"📨 Sizga yangi xabar:\n\n{message.text}",
            reply_markup=keyboard
        )
        await message.answer("Xabaringiz yuborildi ✅")
    else:
        await message.answer("Bu xabar hech kimga yuborilmadi.")
