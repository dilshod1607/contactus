import uuid

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import quote_plus
from data.config import CHANNELS
from loader import dp, db, bot

reply_sessions = {}


def showChannels(ref_link=None):
    keyboard = InlineKeyboardMarkup(row_width=1)

    for channel in CHANNELS:
        btn = InlineKeyboardButton(text=channel[0], url=channel[2])
        keyboard.insert(btn)

    if ref_link:
        # Matn va linkni kodlash (xavfsiz formatda)
        safe_url = quote_plus(ref_link)
        share_text = quote_plus("Anonim chat uchun link! 👆")
        share_link = f"https://t.me/share/url?url={safe_url}&text={share_text}"

        # Tugma qo‘shiladi
        share_button = InlineKeyboardButton("🔗 Ulashish", url=share_link)
        keyboard.add(share_button)

    return keyboard


def generate_ref_link(user_id: int, db) -> str:
    bot_username = "deptestdeploybot"

    code = db.get_user_uuid(user_id)
    print("Bazadan olingan UUID:", code)

    if not code:
        code = uuid.uuid4().hex[:14]
        db.insert_uuid_for_user(user_id, code)
        print("Yangi UUID qo'shildi:", code)

    return f"https://t.me/{bot_username}?start={code}"


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user_status = db.select_user(user_id=message.from_user.id)
    sender_id = message.from_user.id
    args = message.get_args()
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

    if args:  # Referal orqali kelgan bo‘lsa
        receiver_id = db.get_user_id_by_uuid(args)
        if receiver_id and receiver_id != sender_id:
            db.insert_referral(args, sender_id)
            keyboard = InlineKeyboardMarkup().add(
                InlineKeyboardButton("Xabar yuborish", callback_data=f"send_once:{receiver_id}")
            )
            await message.answer("Habaringizni shu yerda qoldiring.", reply_markup=keyboard)
            return

        # Foydalanuvchiga har doim shaxsiy havolasini yuborish
    ref_link = generate_ref_link(sender_id, db)
    await message.answer(f"Sizning shaxsiy havolangiz:\n\n{ref_link}", reply_markup=showChannels(ref_link))


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("send_once:"))
async def handle_send_once(callback: types.CallbackQuery):
    receiver_id = int(callback.data.split(":")[1])
    sender_id = callback.from_user.id

    reply_sessions[sender_id] = receiver_id
    await callback.message.answer("Habaringingizni shu yerda qoldiring.")
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("reply_to:"))
async def handle_reply_to(callback: types.CallbackQuery):
    receiver_id = int(callback.data.split(":")[1])
    sender_id = callback.from_user.id
    reply_sessions[sender_id] = receiver_id

    await callback.message.answer("Habaringingizni shu yerda qoldiring.")
    await callback.answer()


@dp.message_handler(
    lambda message: not (message.text and message.text.startswith('/')),
    content_types=types.ContentTypes.ANY
)
async def handle_reply(message: types.Message):
    sender_id = message.from_user.id

    if sender_id in reply_sessions:
        receiver_id = reply_sessions.pop(sender_id)
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Javob yozish", callback_data=f"reply_to:{sender_id}")
        )

        try:
            await bot.copy_message(
                chat_id=receiver_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=keyboard
            )
            await message.answer("Xabaringiz yuborildi ✅")
        except Exception as e:
            await message.answer("Xatolik yuz berdi. Xabar yuborilmadi.")
    else:
        await message.answer("Bu xabar hech kimga yuborilmadi.")
