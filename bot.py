import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8687956219:AAEwtEQznYVw-oZYLMwbGDAw_N0Kj_xwboA"
ADMIN_ID = 8401360466

user_state = {}

# حفظ الطلب
def save_order(data):
    try:
        with open("orders.json", "r") as f:
            orders = json.load(f)
    except:
        orders = []

    orders.append(data)

    with open("orders.json", "w") as f:
        json.dump(orders, f, indent=4)

# start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📌 طلب خدمة", callback_data="request")],
        [InlineKeyboardButton("ℹ️ معلومات", callback_data="info")]
    ]
    await update.message.reply_text("🔥 أهلاً بك في بوت الخدمات 🔥", reply_markup=InlineKeyboardMarkup(keyboard))

# buttons
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "request":
        keyboard = [
            [InlineKeyboardButton("🔹 إزالة صفحات", callback_data="remove")],
            [InlineKeyboardButton("🔹 استرجاع حساب", callback_data="recover")],
            [InlineKeyboardButton("🔹 مساعدة ابتزاز", callback_data="blackmail")],
            [InlineKeyboardButton("🔹 خدمات سوشل", callback_data="social")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
        ]
        await query.message.reply_text("اختر الخدمة:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data in ["remove", "recover", "blackmail", "social"]:
        user_state[query.from_user.id] = {"service": query.data}
        await query.message.reply_text("✍️ اكتب تفاصيل الطلب:")

    elif query.data == "info":
        await query.message.reply_text("بوت خدمات احترافي 🚀")

    elif query.data == "cancel":
        user_state.pop(query.from_user.id, None)
        await query.message.reply_text("❌ تم إلغاء الطلب")

# نص
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_state and "details" not in user_state[user_id]:
        user_state[user_id]["details"] = update.message.text

        btn = [[KeyboardButton("📱 إرسال رقمي", request_contact=True)]]
        await update.message.reply_text(
            "📞 أرسل رقمك:",
            reply_markup=ReplyKeyboardMarkup(btn, resize_keyboard=True, one_time_keyboard=True)
        )

# رقم
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_state:
        data = user_state[user_id]
        user = update.message.from_user

        order = {
            "name": user.first_name,
            "id": user.id,
            "phone": update.message.contact.phone_number,
            "service": data['service'],
            "details": data['details']
        }

        save_order(order)

        msg = f"""
🔥 طلب جديد

👤 الاسم: {order['name']}
🆔 ID: {order['id']}
📞 الرقم: {order['phone']}

📌 الخدمة: {order['service']}
📝 التفاصيل:
{order['details']}
"""

        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

        await update.message.reply_text("✅ تم إرسال طلبك بنجاح")

        user_state.pop(user_id, None)

# عرض الطلبات (إلك فقط)
async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    try:
        with open("orders.json", "r") as f:
            orders = json.load(f)

        text = "📂 الطلبات:\n\n"
        for o in orders[-5:]:
            text += f"{o['name']} | {o['service']}\n"

        await update.message.reply_text(text)

    except:
        await update.message.reply_text("ما في طلبات بعد")

# تشغيل
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("orders", orders))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.CONTACT, handle_contact))

print("🔥 Bot running...")
app.run_polling()

