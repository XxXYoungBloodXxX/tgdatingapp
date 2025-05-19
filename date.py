import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import redis
import random

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
REDIS_URL = os.getenv("REDIS_URL")
BLOCKED_WORDS = [w.strip().lower() for w in os.getenv("BLOCKED_WORDS", "").split(",") if w.strip()]

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

r = redis.Redis.from_url(REDIS_URL)

PHILIPPINE_LOCATIONS = [
    "metro manila", "quezon city", "manila", "caloocan", "davao city", "cebu city", "zamboanga city", "taguig",
    "pasig", "cagayan de oro", "parañaque", "dasmariñas", "valenzuela", "bacoor", "general santos",
    "bacolod", "antipolo", "muntinlupa", "iloilo city", "pasay", "malabon", "las piñas", "mandaue",
    "san jose del monte", "navotas", "marikina", "calamba", "angeles", "lipa", "san pedro", "butuan",
    "cavite", "bulacan", "pampanga", "laguna", "batangas", "rizal", "pangasinan", "negros occidental",
    "leyte", "bohol", "agusan del norte", "any"
]
AGE_GROUPS = ['18-25', '26-35', '36+']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇵🇭 *Filipino Anonymous Dating Bot*\n\n"
        "1. Set preferences:\n"
        "/gender [male|female|any]\n"
        "/age [18-25|26-35|36+]\n"
        "/location [city]\n"
        "2. /find - Start searching\n"
        "3. /stop - End chat\n"
        "4. /report - Report user",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def set_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if not args or args[0].lower() not in ['male', 'female', 'any']:
        await update.message.reply_text("Usage: /gender [male|female|any]")
        return
    gender = args[0].lower()
    r.hset(user_id, 'gender', gender)
    await update.message.reply_text(f"✅ Gender preference set to {gender.capitalize()}")

async def set_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if not args or args[0] not in AGE_GROUPS:
        await update.message.reply_text("Usage: /age [18-25|26-35|36+]")
        return
    age = args[0]
    r.hset(user_id, 'age', age)
    await update.message.reply_text(f"✅ Age preference set to {age}")

async def set_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if not args:
        locations = "\n".join([f"- {loc.title()}" for loc in PHILIPPINE_LOCATIONS])
        await update.message.reply_text(
            f"🇵🇭 Available Locations:\n{locations}\n\n"
            "Usage: /location [location] (e.g. /location cebu city)"
        )
        return
    location = " ".join(args).lower()
    if location not in PHILIPPINE_LOCATIONS:
        await update.message.reply_text(
            "Location not recognized. Type /location to see the list of available places."
        )
        return
    r.hset(user_id, 'location', location)
    await update.message.reply_text(f"📍 Location set to: {location.title()}")

async def find_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not r.hexists(user_id, 'gender') or not r.hexists(user_id, 'age') or not r.hexists(user_id, 'location'):
        await update.message.reply_text(
            "⚠️ Please set all your preferences first:\n"
            "/gender [male|female|any]\n"
            "/age [18-25|26-35|36+]\n"
            "/location [city/province]"
        )
        return
    # Check if already searching
    if r.lpos('waiting_queue', user_id) is not None:
        await update.message.reply_text(
            "⏳ Still searching for a match. Please wait!"
        )
        return
    # Remove user from queue if already present (just in case)
    r.lrem('waiting_queue', 0, user_id)
    r.rpush('waiting_queue', user_id)
    gender = r.hget(user_id, 'gender').decode().title()
    age = r.hget(user_id, 'age').decode()
    location = r.hget(user_id, 'location').decode().title()
    await update.message.reply_text(
        f"🔍 Searching for your match...\n"
        f"• Gender: {gender}\n"
        f"• Age: {age}\n"
        f"• Location: {location}\n"
        "Please wait while we find someone for you!"
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = r.hget(user_id, "current_partner")
    if partner_id:
        r.hdel(user_id, "current_partner")
        r.hdel(partner_id, "current_partner")
        await context.bot.send_message(chat_id=int(partner_id), text="❌ Your partner has left the chat.")
        await update.message.reply_text("❌ You have left the chat.")
    else:
        await update.message.reply_text("You're not in a chat.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text.lower()
    # Content filtering
    if any(word in message_text for word in BLOCKED_WORDS):
        await update.message.reply_text("🚫 Message blocked: Contains inappropriate content")
        r.hincrby(user_id, 'warnings', 1)
        if int(r.hget(user_id, 'warnings') or 0) >= 3 and ADMIN_IDS:
            await context.bot.send_message(chat_id=ADMIN_IDS[0], text=f"User {user_id} needs review")
        return
    partner_id = r.hget(user_id, "current_partner")
    if partner_id:
        alias = r.hget(user_id, "alias")
        if not alias:
            alias = f"User_{random.randint(1000,9999)}"
            r.hset(user_id, "alias", alias)
        await context.bot.send_message(
            chat_id=int(partner_id),
            text=f"{alias.decode() if isinstance(alias, bytes) else alias}: {update.message.text}"
        )
    else:
        await update.message.reply_text("Use /find to get matched with someone!")

async def report_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reporter_id = update.effective_user.id
    partner_id = r.hget(reporter_id, 'current_partner')
    if partner_id:
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"🚨 REPORT from {reporter_id}\n"
                     f"Target: {partner_id.decode()}\n"
                     f"Reason: {' '.join(context.args) if context.args else 'No reason'}"
            )
        await update.message.reply_text("Report submitted to admins")
    else:
        await update.message.reply_text("You're not in a chat")

async def match_users(context: ContextTypes.DEFAULT_TYPE):
    waiting_users = [uid.decode() for uid in r.lrange("waiting_queue", 0, -1)]
    matched = set()
    for i, user1 in enumerate(waiting_users):
        if user1 in matched:
            continue
        user1_gender = r.hget(user1, "gender") or b"any"
        user1_age = r.hget(user1, "age") or b"any"
        user1_location = r.hget(user1, "location") or b"any"
        for user2 in waiting_users[i+1:]:
            if user2 in matched:
                continue
            user2_gender = r.hget(user2, "gender") or b"any"
            user2_age = r.hget(user2, "age") or b"any"
            user2_location = r.hget(user2, "location") or b"any"
            gender_match = (
                user1_gender == b'any' or user2_gender == b'any' or user1_gender == user2_gender
            )
            age_match = (
                user1_age == b'any' or user2_age == b'any' or user1_age == user2_age
            )
            location_match = (
                user1_location == b'any' or user2_location == b'any' or user1_location == user2_location
            )
            if gender_match and age_match and location_match:
                r.hset(user1, "current_partner", user2)
                r.hset(user2, "current_partner", user1)
                alias1 = f"User_{random.randint(1000,9999)}"
                alias2 = f"User_{random.randint(1000,9999)}"
                r.hset(user1, "alias", alias1)
                r.hset(user2, "alias", alias2)
                details1 = (
                    f"Location: {user2_location.decode().title()}\n"
                    f"Age: {user2_age.decode()}"
                )
                details2 = (
                    f"Location: {user1_location.decode().title()}\n"
                    f"Age: {user1_age.decode()}"
                )
                await context.bot.send_message(
                    int(user1),
                    f"💑 Match found!\n"
                    f"Your partner's details:\n{details1}\n\n"
                    f"Say hi to {alias2}!"
                )
                await context.bot.send_message(
                    int(user2),
                    f"💑 Match found!\n"
                    f"Your partner's details:\n{details2}\n\n"
                    f"Say hi to {alias1}!"
                )
                matched.add(user1)
                matched.add(user2)
                break
    for user in matched:
        r.lrem("waiting_queue", 0, user)

if __name__ == "__main__":
    from telegram.ext import ApplicationBuilder
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("gender", set_gender))
    app.add_handler(CommandHandler("age", set_age))
    app.add_handler(CommandHandler("location", set_location))
    app.add_handler(CommandHandler("find", find_partner))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("report", report_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.job_queue.run_repeating(match_users, interval=10, first=5)
    print("Bot started!")
    app.run_polling()
