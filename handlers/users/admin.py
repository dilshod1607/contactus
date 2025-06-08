import asyncio
import os

from datetime import datetime
import datetime as dt
import pytz
import xlsxwriter as xl

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext

from data.config import ADMINS
from loader import bot, db, dp
from keyboards.inline.AdminPanel import AdminPanel, GoBack, BaseType
from states.Admin_States import SendMessage


@dp.message_handler(Command("admin", prefixes='!./'), user_id=ADMINS)
async def admin_panel(message: types.Message):
    print("ADMIN KOMANDA KELDI")
    await message.answer(
        text=f"<b>Assalomu alaykum xurmatli {message.from_user.get_mention()}</b>\n\n"
             f"😊 Bugun nimalarni o'zgartiramiz?",
        reply_markup=AdminPanel
    )


@dp.callback_query_handler(state='*', text='GoBack')
async def GoToPanel(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(
        text=f"<b>Assalomu alaykum xurmatli {call.from_user.get_mention()}</b>\n\n"
             f"😊 Bugun nimalarni o'zgartiramiz?",
        reply_markup=AdminPanel
    )


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
    rowIndex = 2
    for user in users:
        user_id = user[0]
        fullname = user[1]
        username = user[2]

        worksheet.write('A' + str(rowIndex), user_id)
        worksheet.write('B' + str(rowIndex), fullname)
        worksheet.write('C' + str(rowIndex), f"@{username}")
        rowIndex += 1
    workbook.close()
    file = types.InputFile(path_or_bytesio="users.xlsx")
    await call.message.answer_document(
        document=file,
        caption="<b>users.xlsx</b>\n\n"
                "Excel formatida baza yuklandi")
    os.remove(path="users.xlsx")
