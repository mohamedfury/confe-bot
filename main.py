from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '7787936953:AAG29m4s-rC5tx4ZX0ROBsjEPta9KDCvwMs'
DEVELOPER_ID = 674291793  # غيّره إلى آي دي المطور الحقيقي
GROUP_ID = -1001234567890  # غيّره إلى آي دي المجموعة

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

admissions_open = False
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
    if not admissions_open:
        await message.reply("🚫 الاعترافات مغلقة حالياً.")
        return

    user_id = message.from_user.id
    message_id = message.message_id

    # رسالة تأكيد للمرسل
    await message.reply("✅ تم ارسال اعترافك بنجاح.")

    # إرسال للمطور معلومات المُرسل
    await bot.send_message(DEVELOPER_ID, f"📥 اعتراف جديد من: {message.from_user.full_name} (ID: {user_id})")

    # تخزين الاعتراف
    confessions_storage[message_id] = message.text

    # أزرار نشر/حذف
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("نشر", callback_data=f"publish|{message_id}"),
        InlineKeyboardButton("حذف", callback_data=f"delete|{message_id}")
    )

    # إرسال نص الاعتراف للمطور
    await bot.send_message(DEVELOPER_ID, f"📝 نص الاعتراف:\n\n{message.text}", reply_markup=keyboard)

@dp.callback_query_handler()
async def handle_decision(call: types.CallbackQuery):
    action, msg_id = call.data.split("|")
    msg_id = int(msg_id)

    if action == "publish":
        confession_text = confessions_storage.get(msg_id, "❗ لم يتم العثور على نص الاعتراف.")
        await bot.send_message(GROUP_ID, f"💭 اعتراف مجهول:\n\n{confession_text}")
        await call.message.edit_text("✅ تم نشر الاعتراف.")
    elif action == "delete":
        await call.message.edit_text("❌ تم حذف الاعتراف.")

    # حذف الاعتراف من التخزين بعد النشر/الحذف
    confessions_storage.pop(msg_id, None)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)