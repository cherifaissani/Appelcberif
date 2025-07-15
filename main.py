import logging
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

logging.basicConfig(level=logging.INFO)

strategies = {
    "safe": [0, 0, 1],
    "risky": [1, 1, 0],
    "medium": [0, 1, 0],
}

user_stats = {}

def generate_move(strategy="medium"):
    return random.choice(strategies.get(strategy, strategies["medium"]))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_stats[uid] = {"wins": 0, "losses": 0, "strategy": "medium"}
    buttons = [
        [InlineKeyboardButton("🎯 ابدأ اللعب", callback_data="play")],
        [
            InlineKeyboardButton("🟢 آمنة", callback_data="set_safe"),
            InlineKeyboardButton("🟡 متوسطة", callback_data="set_medium"),
            InlineKeyboardButton("🔴 مخاطرة", callback_data="set_risky"),
        ],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")]
    ]
    await update.message.reply_text(
        "👋 مرحباً! استخدم الأزرار للعب:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    if uid not in user_stats:
        user_stats[uid] = {"wins":0,"losses":0,"strategy":"medium"}
    data = query.data
    if data == "play":
        kb = [[InlineKeyboardButton("🍏 يسار", callback_data="left"),
               InlineKeyboardButton("🍏 يمين", callback_data="right")]]
        await query.edit_message_text("⬇️ اختر تفاحة:", reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("set_"):
        strat = data.split("_")[1]
        user_stats[uid]["strategy"] = strat
        await query.edit_message_text(f"✅ اخترت استراتيجية: {strat}")
    elif data in ["left","right"]:
        move = generate_move(user_stats[uid]["strategy"])
        chosen = 1 if data == "left" else 0
        if chosen == move:
            user_stats[uid]["wins"] += 1
            res = "✅ ربحت!"
        else:
            user_stats[uid]["losses"] += 1
            res = "❌ خسرت!"
        kb = [[InlineKeyboardButton("🔁 جولة جديدة", callback_data="play")],
              [InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")]]
        await query.edit_message_text(res, reply_markup=InlineKeyboardMarkup(kb))
    elif data == "stats":
        s = user_stats[uid]
        await query.edit_message_text(
            f"📊 انتصارات: {s['wins']}\n"
            f"❌ خسارات: {s['losses']}\n"
            f"🎯 الاستراتيجية: {s['strategy']}"
        )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("استخدم الأزرار فقط 👇")

if __name__ == "__main__":
    token = os.getenv("TOKEN")
    if not token:
        print("❌ يرجى تحديد TOKEN في متغيرات البيئة")
        exit(1)
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    print("✅ البوت يعمل الآن...")
    app.run_polling()
