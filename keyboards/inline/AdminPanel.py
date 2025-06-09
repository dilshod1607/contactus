from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


AdminPanel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📤 Xabar yuborish", callback_data='admin:send_message'),
            InlineKeyboardButton(text="📊 Bot statistikasi", callback_data='admin:bot_statics'),
        ],
        [
            InlineKeyboardButton(text="🔗 ID dan referal olish", callback_data="get_ref_by_id"),
            InlineKeyboardButton(text="🗄 Bazani yuklash", callback_data='admin:download_base')
        ]
    ]
)

GoBack = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="◀️ Ortga", callback_data='GoBack')
        ],
    ],
)

BaseType = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⚙️ Databse | .db", callback_data='base:dotdb'),
            InlineKeyboardButton(text="📑 Excel | .xlsx", callback_data='base:dotxlsx')
        ],
        [
            InlineKeyboardButton(text="◀️ Ortga", callback_data='GoBack')
        ]
    ],
)