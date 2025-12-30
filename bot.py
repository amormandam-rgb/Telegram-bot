from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# ====== تنظیمات ربات ======
API_ID = 123456           # مقدار خودت
API_HASH = "API_HASH"     # مقدار خودت
BOT_TOKEN = "TOKEN"       # مقدار خودت
ADMINS = [111111111]      # آیدی عددی ادمین‌ها

app = Client("sampbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ====== منوها ======
MAIN_MENU = ReplyKeyboardMarkup([
    ["📝 فرم‌ها", "🛒 خرید محصولات"],
    ["☎️ ارتباط با سازنده"]
], resize_keyboard=True)

FORMS_MENU = ReplyKeyboardMarkup([
    ["فرم درخواست ادمینی", "فرم درخواست هلپری", "فرم درخواست لیدری"],
    ["⬅ بازگشت"]
], resize_keyboard=True)

# ====== ذخیره مراحل فرم ======
user_steps = {}

# ====== استارت ======
@app.on_message(filters.command("start"))
def start(client, message):
    user_steps.pop(message.from_user.id, None)
    message.reply("به پنل سرور خوش آمدید:", reply_markup=MAIN_MENU)

# ====== دریافت پیام‌ها ======
@app.on_message(filters.text)
def handle(client, message):
    uid = message.from_user.id
    text = message.text

    # --- منوی اصلی ---
    if text == "📝 فرم‌ها":
        message.reply("یک فرم را انتخاب کنید:", reply_markup=FORMS_MENU)
        return
    elif text == "🛒 خرید محصولات":
        message.reply("برای سفارش محصولات سرور به آیدی زیر پیام دهید:\n@Aericol")
        return
    elif text == "☎️ ارتباط با سازنده":
        message.reply(
            "کانال سازنده ربات:\nhttps://t.me/PrivateSRI\n\n"
            "آیدی سازنده ربات:\n@Aericol\n\n"
            "آیدی فاندر های سرور:\n@Aericol\n@Pv_Erfan0"
        )
        return
    elif text == "⬅ بازگشت":
        message.reply("بازگشت به منوی اصلی", reply_markup=MAIN_MENU)
        return

    # --- منوی فرم‌ها ---
    if text in ["فرم درخواست ادمینی", "فرم درخواست هلپری", "فرم درخواست لیدری"]:
        questions = [
            "اسم شما:",
            "اسم شما در گیم:",
            "آیدی شما:",
            "چند سالتون:",
            "چند ساعت میتونید در سرور فعالیت کنید:",
            "یک شماره از شما:",
            "سابقه شما:"
        ]
        user_steps[uid] = {
            "form_name": text,
            "questions": questions,
            "answers": [],
            "step": 0
        }
        message.reply(questions[0])
        return

    # --- مراحل فرم ---
    if uid in user_steps:
        data = user_steps[uid]
        data["answers"].append(text)
        data["step"] += 1

        if data["step"] < len(data["questions"]):
            message.reply(data["questions"][data["step"]])
        else:
            # ارسال فرم کامل برای ادمین‌ها با دکمه قبول/رد
            form_text = f"📋 فرم جدید: {data['form_name']}\n\n"
            for i in range(len(data["questions"])):
                form_text += f"{data['questions'][i]} {data['answers'][i]}\n"
            form_text += f"\nآیدی کاربر: {uid}"  # برای شناسایی کاربر

            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ قبول", callback_data=f"accept_{uid}"),
                    InlineKeyboardButton("❌ رد", callback_data=f"reject_{uid}")
                ]
            ])

            for admin in ADMINS:
                client.send_message(admin, form_text, reply_markup=buttons)

            message.reply("✅ همه‌ی فرم را پر کردید و صبور باشید تا پشتیبانی جواب شما را بدهد.", reply_markup=MAIN_MENU)
            user_steps.pop(uid)

# ====== مدیریت دکمه‌های ادمین ======
@app.on_callback_query()
def callback(client, query):
    data = query.data
    admin_id = query.from_user.id

    if admin_id not in ADMINS:
        query.answer("❌ شما ادمین نیستید", show_alert=True)
        return

    if data.startswith("accept_"):
        user_id = int(data.split("_")[1])
        client.send_message(user_id,
            "تبریک! درخواست شما قبول شد ✅\nبرای ادامه مراحل به آیدی زیر پیام دهید:\n@Aericol")
        query.edit_message_reply_markup(None)
        query.answer("فرم قبول شد ✅")
    elif data.startswith("reject_"):
        user_id = int(data.split("_")[1])
        client.send_message(user_id,
            "متاسفانه درخواست شما رد شد ❌")
        query.edit_message_reply_markup(None)
        query.answer("فرم رد شد ❌")

# ====== اجرای ربات ======
app.run()
