from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


SuperAdminPanel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📤 Xabar yuborish", callback_data='admin:send_message'),
            InlineKeyboardButton(text="📊 Bot statistikasi", callback_data='admin:bot_statics'),
        ],
        [
            InlineKeyboardButton(text="ID orqali malumot olish", callback_data="get_ref_by_id"),
            InlineKeyboardButton(text="🗄 Bazani yuklash", callback_data='admin:download_base')
        ],
        [
            InlineKeyboardButton(text="Admin qo'shish", callback_data='admin:qoshish'),
        ]
    ]
)


AdminPanel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📤 Xabar yuborish", callback_data='admin:send_message'),
            InlineKeyboardButton(text="📊 Bot statistikasi", callback_data='admin:bot_statics'),
        ]
    ]
)


def admins_keyboard(admins: list[int]):
    kb = InlineKeyboardMarkup(row_width=2)
    for admin in admins:
        kb.add(
            InlineKeyboardButton(
                text=f"❌ {admin}",
                callback_data=f"admin:del:{admin}"
            )
        )
    kb.add(InlineKeyboardButton(text="🔙 Ortga", callback_data="GoBack"))
    return kb


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