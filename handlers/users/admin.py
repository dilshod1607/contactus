import asyncio
import os
import xlsxwriter as xl

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import ADMINS
from loader import bot, db, dp
from keyboards.inline.AdminPanel import (SuperAdminPanel, AdminPanel, GoBack, BaseType, admins_keyboard,
                                         build_request_message)
from states.Admin_States import RefState

all_admins = db.select_all_admins()


@dp.message_handler(Command("start", prefixes="!./"))
async def admin_panel(message: types.Message):
    super_admin_id = db.select_super()
    all_admin = db.select_all_admins()
    if message.from_user.id == super_admin_id:
        await message.answer(
            text=f"<b>Assalomu alaykum xurmatli {message.from_user.get_mention()}</b>\n\n",
            reply_markup=SuperAdminPanel
        )
    elif message.from_user.id in all_admin:
        # Oddiy admin panel
        await message.answer(
            text=f"🔑 <b>Assalomu alaykum Admin {message.from_user.get_mention()}</b>\n\n",
            reply_markup=AdminPanel
        )
    print("Start bosdi:", message.from_user.id)


@dp.callback_query_handler(lambda c: c.data == "admin:murojatlar")
async def show_all_requests(callback_query: types.CallbackQuery):
    super_admin_id = db.select_super()
    is_super_admin = (callback_query.from_user.id == super_admin_id)

    # super admin = hamma yozuvlar (closed ham)
    # oddiy admin = faqat new va viewed
    requests = db.select_all_requests(include_closed=False)

    if not requests:
        return await callback_query.message.answer("📭 Hech qanday murojaat yo‘q.")

    # Callback tugmasini yopib qo'yamiz
    await callback_query.answer()

    # Har bir murojaatni alohida yuboramiz
    for r in requests:
        text = f"""
👤 F.I.O: {r['fio']}
📞 Telefon: {r['phone']}
📧 Email: {r['email']}
💬 Xabar: {r['message']}
📌 Status: {r['status']}
"""
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("Ko‘rish", callback_data=f"view_{r['id']}"),
            InlineKeyboardButton("Yopish", callback_data=f"close_{r['id']}")
        )

        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=text,
            reply_markup=markup
        )


async def new_request_handler(fio, phone, email, message, req_id):
    text = f"""
📝 <b>Yangi murojaat keldi</b>:
👤 F.I.O: {fio}
📞 Telefon: {phone}
📧 Email: {email}
💬 Xabar: {message}
📌 Status: new
"""

    # Inline tugmalar — req_id ga bog'langan
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👁 Ko‘rish", callback_data=f"view_{req_id}"),
        InlineKeyboardButton("❌ Yopish", callback_data=f"close_{req_id}")
    )

    all_admins = db.select_all_admins()
    print("Adminlar:", all_admins)

    for admin_id in all_admins:
        try:
            await bot.send_message(admin_id, text, reply_markup=markup, parse_mode="HTML")
            print(f"✅ {admin_id} ga yuborildi (req_id={req_id})")
        except Exception as e:
            print(f"❌ {admin_id} ga yuborishda xato (req_id={req_id}): {e}")


@dp.callback_query_handler(lambda c: c.data and c.data.startswith(("view_", "close_")))
async def process_request_callback(callback_query: types.CallbackQuery):
    action, req_id = callback_query.data.split("_")
    req_id = int(req_id)

    # Bitta murojaatni ID bo‘yicha olish
    request = db.select_request_by_id(req_id)
    if not request:
        return await callback_query.answer("❌ Murojaat topilmadi!", show_alert=True)

    if action == "view":
        # Statusni yangilash
        db.update_request_status(req_id, "viewed")
        text = f"""
👤 F.I.O: {request['fio']}
📞 Telefon: {request['phone']}
📧 Email: {request['email']}
💬 Xabar: {request['message']}
📌 Status: viewed
"""
        await bot.edit_message_text(
            text=text,
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=callback_query.message.reply_markup,
            parse_mode="HTML"
        )
        await callback_query.answer("Murojaat ko‘rildi ✅")

    elif action == "close":
        # Statusni yangilash
        db.update_request_status(req_id, "closed")

        # Xabarni o‘chirish
        await bot.delete_message(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id
        )
        await callback_query.answer("Murojaat yopildi va o‘chirildi ✅")


@dp.callback_query_handler(text='GoBack', state='*')
async def GoToPanel(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    super_admin_id = db.select_super()
    all_admins = db.select_all_admins()

    if call.from_user.id == super_admin_id:
        await call.answer()
        await call.message.edit_text(
            text=f"👑 <b>Assalomu alaykum {call.from_user.get_mention()}</b>\n\n",
            reply_markup=SuperAdminPanel
        )
    elif call.from_user.id in all_admins:
        await call.answer()
        await call.message.edit_text(
            text=f"🔑 <b>Assalomu alaykum Admin {call.from_user.get_mention()}</b>\n\n"
                 f"Siz uchun mavjud bo‘lgan imkoniyatlar:",
            reply_markup=AdminPanel
        )
    else:
        await call.answer("⛔ Sizga ruxsat yo‘q", show_alert=True)


# @dp.callback_query_handler(text='GoBackmu', state='*')
# async def GoToPanel(call: types.CallbackQuery, state: FSMContext):
#     await state.finish()
#     super_admin_id = db.select_super()
#     all_admins = db.select_all_admins()
#
#     if call.from_user.id == super_admin_id:
#         await call.answer()
#         await call.message.edit_text(
#             text=f"👑 <b>Assalomu alaykum {call.from_user.get_mention()}</b>\n\n",
#             reply_markup=b
#         )
#     elif call.from_user.id in all_admins:
#         await call.answer()
#         await call.message.edit_text(
#             text=f"🔑 <b>Assalomu alaykum Admin {call.from_user.get_mention()}</b>\n\n"
#                  f"Siz uchun mavjud bo‘lgan imkoniyatlar:",
#             reply_markup=AdminPanel
#         )
#     else:
#         await call.answer("⛔ Sizga ruxsat yo‘q", show_alert=True)


@dp.callback_query_handler(text="admin:qoshish", state='*')
async def addadmin(call: types.CallbackQuery):
    all_admins = db.select_all_admins()
    super_admin = db.select_super()
    admins_to_show = [a for a in all_admins if a != super_admin]

    text = "👤 Admin boshqaruvi\n\n"
    text += "🆕 Yangi admin qo‘shish uchun ID yuboring.\n\n"
    if admins_to_show:
        text += "📋 Mavjud adminlar:\n"
        for a in admins_to_show:
            text += f"   • <code>{a}</code>\n"
    else:
        text += "📋 Hozircha oddiy adminlar yo‘q."

    await call.answer()  # spinnerni yopish
    await call.message.edit_text(
        text=text,
        reply_markup=admins_keyboard(admins_to_show)
    )
    await RefState.admin_id.set()


# --- Yangi admin qo‘shish ---
@dp.message_handler(state=RefState.admin_id, content_types=types.ContentType.TEXT)
async def waitadminid(message: types.Message, state: FSMContext):
    try:
        admin_id = int(message.text.strip())
        db.add_admin(admin_id)
        await message.answer(
            f"✅ Admin qo‘shildi: <code>{admin_id}</code>",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("🔙 Ortga", callback_data="admin:qoshish")
            )
        )
    except ValueError:
        await message.answer("❌ ID faqat raqam bo‘lishi kerak")
    finally:
        await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith("admin:del:"), state='*')
async def delete_admin_handler(call: types.CallbackQuery):
    try:
        admin_id = int(call.data.split(":")[2])
    except Exception:
        return await call.answer("Noto‘g‘ri callback.", show_alert=True)

    deleted = db.delete_admin(admin_id)

    if deleted:
        await call.answer("✅ Admin o‘chirildi", show_alert=True)
    else:
        return await call.answer("❌ Super adminni ochirish mumkin emas!", show_alert=True)

    # Yangilangan ro‘yxatni qayta chiqaramiz
    super_admin = db.select_super()
    admins = db.select_all_admins()
    admins_to_show = [a for a in admins if a != super_admin]

    text = "👤 Admin boshqaruvi\n\n🆕 Yangi admin qo‘shish uchun ID yuboring.\n\n"
    if admins_to_show:
        text += "📋 Mavjud adminlar:\n" + "\n".join(f"   • <code>{a}</code>" for a in admins_to_show)
    else:
        text += "📋 Hozircha oddiy adminlar yo‘q."

    kb = admins_keyboard(admins_to_show)

    try:
        await call.message.edit_text(text, reply_markup=kb)
    except Exception:
        # Ba'zan "Message is not modified" bo‘lishi mumkin, shunda shunchaki markupni yangilaymiz
        await call.message.edit_reply_markup(reply_markup=kb)


@dp.callback_query_handler(text='admin:download_base')
async def save_base(call: types.CallbackQuery):
    await call.message.edit_text(
        text="<b>🗂 Bazani qaysi turda yuklab olishingizni tanlang</b>",
        reply_markup=BaseType
    )


@dp.callback_query_handler(text="base:dotdb")
async def dot_db(call: types.CallbackQuery):
    await call.message.delete()

    input_file = types.InputFile(path_or_bytesio='data/main.db')
    await call.message.answer_document(
        document=input_file,
        caption="<b>main.db</b>\n\n"
                "DataBase baza yuklandi",
    )


@dp.callback_query_handler(text="base:dotxlsx")
async def dot_xlsx(call: types.CallbackQuery):
    await call.message.delete()
    users = db.select_all_users()

    workbook = xl.Workbook("users.xlsx")
    bold_format = workbook.add_format({'bold': True})
    worksheet = workbook.add_worksheet("Users")
    worksheet.write('A1', 'User ID', bold_format)
    worksheet.write('B1', 'Fullname', bold_format)
    worksheet.write('C1', 'Username', bold_format)
    worksheet.write('D1', 'Uuid', bold_format)

    rowIndex = 2
    for user in users:
        user_id = user[0]
        fullname = user[1]
        username = user[2]
        uuid = user[3]

        worksheet.write('A' + str(rowIndex), user_id)
        worksheet.write('B' + str(rowIndex), fullname)
        worksheet.write('C' + str(rowIndex), f"@{username}")
        worksheet.write('D' + str(rowIndex), uuid)
        rowIndex += 1
    workbook.close()
    file = types.InputFile(path_or_bytesio="users.xlsx")
    await call.message.answer_document(
        document=file,
        caption="<b>users.xlsx</b>\n\n"
                "Excel formatida baza yuklandi", )
    os.remove(path="users.xlsx")
