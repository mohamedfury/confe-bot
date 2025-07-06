import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '7787936953:AAF5_FjYZA-xove1KaqkyPrOpNSGLwGaxA4'
DEVELOPER_ID = 674291793
GROUP_ID = -1001201718722

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

admissions_open = False

# تخزين آخر وقت اعتراف لكل مستخدم لمنع السبام
user_last_confession = {}

# تخزين نصوص الاعترافات حسب message_id
confessions_storage = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("اهلا بك في بوت الاعترافات 🌚\nاذا الاعترافات مفتوحة اكدر استلم منك رسالتك.")

@dp.message_handler(lambda message: message.chat.type == 'supergroup')
async def group_commands(message: types.Message):
    global admissions_open
    if message.from_user.id == DEVELOPER_ID:
        if message.text == "فتح الاعترافات":
            admissions_open = True
            await message.reply("✅ تم فتح الاعترافات.")
        elif message.text == "ايقاف الاعترافات":
            admissions_open = False
            await message.reply("⛔ تم ايقاف الاعترافات.")

@dp.message_handler(lambda message: message.chat.type == 'private')
async def handle_confession(message: types.Message):
    global admissions_open

    if not admissions_open:
        await message.reply("🚫 الاعترافات مغلقة حالياً.")
        return

    user_id = message.from_user.id
    now = time.time()

    # تحقق إذا مرّت 60 دقيقة من آخر اعتراف
    if user_id in user_last_confession:
        last_time = user_last_confession[user_id]
        elapsed = now - last_time
        if elapsed < 3600:
            remaining = int((3600 - elapsed) // 60)
            await message.reply(f"⏳ انتظر {remaining} دقيقة قبل أن ترسل اعتراف آخر.")
            return

    user_last_confession[user_id] = now

    # تأكيد للمرسل
    await message.reply("✅ تم ارسال اعترافك بنجاح.")

    # إرسال رسالة للمطور عن منو دز الاعتراف
    await bot.send_message(DEVELOPER_ID, f"📥 اعتراف جديد من: {message.from_user.full_name} (ID: {user_id})")

    # خزّن نص الاعتراف مع message_id
    confessions_storage[message.message_id] = message.text

    # أزرار نشر وحذف
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("نشر", callback_data=f"publish|{message.message_id}|{user_id}"),
        InlineKeyboardButton("حذف", callback_data=f"delete|{message.message_id}")
    )

    # إرسال نص الاعتراف مع الأزرار للمطور
    await bot.send_message(DEVELOPER_ID, f"📝 نص الاعتراف:\n\n{message.text}", reply_markup=keyboard)

@dp.callback_query_handler()
async def handle_decision(call: types.CallbackQuery):
    action, msg_id, user_id = call.data.split("|")

    if action == "publish":
        confession_text = confessions_storage.get(int(msg_id), "لا يوجد نص الاعتراف.")
        await bot.send_message(GROUP_ID, f"💭 اعتراف مجهول:\n\n{confession_text}")
        await call.message.edit_text("✅ تم نشر الاعتراف.")
    elif action == "delete":
        await call.message.edit_text("❌ تم حذف الاعتراف.")

    # بعد النشر أو الحذف، نحذف الاعتراف من التخزين
    confessions_storage.pop(int(msg_id), None)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)