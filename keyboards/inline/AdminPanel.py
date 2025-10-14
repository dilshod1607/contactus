from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


SuperAdminPanel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Murojaatlar", callback_data='admin:murojatlar'),
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
            InlineKeyboardButton(text="📋 Murojaatlar", callback_data='admin:murojatlar'),
            InlineKeyboardButton(text="🗄 Bazani yuklash", callback_data='admin:download_base')
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

GoBackmu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="◀️ Ortga", callback_data='GoBackmu')
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


def build_request_message(requests):
    text = "📬 <b>Murojaatlar:</b>\n\n"
    markup = InlineKeyboardMarkup(row_width=2)

    for r in requests:
        # short info
        text += f"{r['id']}. {r['fio']} – {r['phone']} – {r['status']}\n"

        # tugmalar
        markup.add(
            InlineKeyboardButton("Ko‘rish", callback_data=f"view_{r['id']}"),
            InlineKeyboardButton("Yopish", callback_data=f"close_{r['id']}")
        )

    return text, markup
