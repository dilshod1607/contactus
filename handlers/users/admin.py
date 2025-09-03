import asyncio
import os

# import uuid

from datetime import datetime
import datetime as dt
import pytz
import xlsxwriter as xl

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import ADMINS
from loader import bot, db, dp
from keyboards.inline.AdminPanel import SuperAdminPanel, AdminPanel, GoBack, BaseType, admins_keyboard
from states.Admin_States import SendMessage, RefState


@dp.message_handler(Command("admin", prefixes="!./"))
async def admin_panel(message: types.Message):
    super_admin_id = db.select_super()
    all_admins = db.select_all_admins()
    if message.from_user.id == super_admin_id:
        await message.answer(
            text=f"<b>Assalomu alaykum xurmatli {message.from_user.get_mention()}</b>\n\n"
                 f"😊 Bugun nimalarni o'zgartiramiz?",
            reply_markup=SuperAdminPanel
        )
    elif message.from_user.id in all_admins:
        # Oddiy admin panel
        await message.answer(
            text=f"🔑 <b>Assalomu alaykum Admin {message.from_user.get_mention()}</b>\n\n"
                 f"Siz uchun mavjud bo‘lgan imkoniyatlar:",
            reply_markup=AdminPanel
        )


@dp.callback_query_handler(text='GoBack', state='*')
async def GoToPanel(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    super_admin_id = db.select_super()
    all_admins = db.select_all_admins()

    if call.from_user.id == super_admin_id:
        await call.answer()
        await call.message.edit_text(
            text=f"👑 <b>Assalomu alaykum Super Admin {call.from_user.get_mention()}</b>\n\n"
                 f"😊 Bugun nimalarni o‘zgartiramiz?",
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


@dp.callback_query_handler(text="admin:send_message")
async def send_message(call: types.CallbackQuery):
    await call.message.edit_text(
        text="<b>😉 Ajoyib!, kerakli xabarni yuboring</b>",
        reply_markup=GoBack,
    )
    await SendMessage.text.set()


@dp.message_handler(state=SendMessage.text, content_types=types.ContentType.ANY)
async def Send_Message(message: types.Message, state: FSMContext):
    await state.finish()

    users = db.select_all_users()
    count = db.count_users()[0]
    x = 0
    y = 0

    start_ads = datetime.now(pytz.timezone('Asia/Tashkent'))
    text = await message.answer(f"<b>📨 Xabar qabul qilindi</b>\n\n"
                                f"<b>📄 Turi:</b> Oddiy xabar\n"
                                f"<b>📤 Yuborilishi kerak:</b> {count} ta\n"
                                f"<b>⏰ Boshlandi:</b> {start_ads.strftime('%d/%m/%Y  %H:%M:%S')}"
                                )
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0],
                                   from_chat_id=message.from_user.id,
                                   message_id=message.message_id,
                                   )
            x += 1
        except:
            y += 1
        await asyncio.sleep(0.05)

    finish_ads = datetime.now(pytz.timezone('Asia/Tashkent'))
    db.update_active(active=x)
    db.update_block(block=y)
    await text.edit_text(text=f"<b>📨 Xabar yuborilishi yakunlandi</b>\n\n"
                              f"<b>📤 Yuborildi:</b> {x}/{x + y} ta\n"
                              f"<b>⏰ Boshlandi:</b> {start_ads.strftime('%d/%m/%Y  %H:%M:%S')}\n"
                              f"<b>⏰ Yakunlandi:</b> {finish_ads.strftime('%d/%m/%Y  %H:%M:%S')}\n"
                              f"<b>🕓 Umumiy ketgan vaqt:</b> {(finish_ads - start_ads).seconds} soniya",
                         reply_markup=GoBack)


@dp.callback_query_handler(text="admin:bot_statics")
async def admin_bot_statics(call: types.CallbackQuery):
    text = await call.message.edit_text("<b>📊 Bot statistikasi yuklanmoqda...</b>")
    try:
        active = db.select_active()[0]
    except:
        active = 0
    try:
        block = db.select_block()[0]
    except:
        block = 0

    start_bot = dt.date(year=2023, month=11, day=29)
    today_bot = dt.date.today()

    await text.edit_text(text=f"<b>📊 Bot statistikasi</b>\n\n"
                              f"<b>✅ Aktiv:</b> {active} ta\n"
                              f"<b>❌ Blok:</b> {block} ta\n"
                              f"<b>🔰 Umumiy:</b> {active + block} ta\n"
                              f"➖➖➖➖➖➖➖➖\n"
                              f"<b>⏸ Bot ishga tushgan:</b> {start_bot.strftime('%d/%m/%Y')}\n"
                              f"<b>📆 Bugun:</b> {today_bot.strftime('%d/%m/%Y')}\n"
                              f"<b>📆 Bot ishga tushganiga:</b> {(today_bot - start_bot).days} kun bo'ldi",
                         reply_markup=GoBack)


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
        return await call.answer("❌ Super adminni o‘chirish mumkin emas!", show_alert=True)

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
    worksheet = workbook.add_worksheet("Users")
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
                "Excel formatida baza yuklandi",)
    os.remove(path="users.xlsx")


@dp.callback_query_handler(text="get_ref_by_id")
async def ask_for_user_id(call: types.CallbackQuery):
    await call.message.edit_text("Foydalanuvchi ID sini yuboring (raqam ko‘rinishida):", reply_markup=GoBack)
    await RefState.waiting_for_user_id.set()


@dp.message_handler(state=RefState.waiting_for_user_id)
async def show_referral_stats(message: types.Message, state: FSMContext):
    try:
        target_id = int(message.text)
        uuid = db.get_user_uuid(target_id)

        if not uuid:
            await message.answer("Bu foydalanuvchi uchun UUID topilmadi.")
            await state.finish()
            return

        referral_count = db.count_referral_senders(uuid)
        referral_users = db.get_referral_senders(uuid)

        text = (
            f"👤 Foydalanuvchi ID: {target_id}\n"
            f"🔗 Referal havola: https://t.me/deptestdeploybot?start={uuid}\n"
            f"📥 Murojaat qilganlar soni: {referral_count}\n\n"
        )

        if referral_users:
            text += "👥 Murojaat qilganlar IDlari:\n"
            text += "\n".join(str(uid) for uid in referral_users)
        else:
            text += "👥 Murojaat qilgan foydalanuvchilar yo‘q."

        await message.answer(text, reply_markup=GoBack)
    except ValueError:
        await message.answer("Iltimos, to‘g‘ri ID kiriting (faqat raqam).", reply_markup=GoBack)
    await state.finish()
