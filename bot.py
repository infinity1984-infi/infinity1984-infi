from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import Config
import logging
import sqlite3
from asyncio import sleep

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== DATABASE SETUP ==================
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                (user_id INTEGER PRIMARY KEY)''')
conn.commit()

def add_user(user_id: int):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_all_users():
    cursor.execute("SELECT user_id FROM users")
    return [row[0] for row in cursor.fetchall()]

# ================== FORCE SUBSCRIPTION ==================
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not Config.FORCE_SUB_LINK:
        return True  # Feature disabled

    buttons = [[InlineKeyboardButton("Join Channel", url=Config.FORCE_SUB_LINK)]]
    await update.message.reply_text(
        "⚠️ Join our channel to use this bot!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return False

# ================== AUTO-DELETE FUNCTION ==================
async def auto_delete(message, delay: int = 300):  # 5 minutes
    await sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Auto-delete failed: {e}")

# ================== COMMAND HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)
    
    buttons = [
        [InlineKeyboardButton(btn["text"], url=btn["url"])]
        for btn in Config.BUTTON_URLS.values()
    ]
    
    await update.message.reply_html(
        f"Hi {user.mention_html()}! 👋\n"
        "Send a number to get the corresponding file from the channel!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if Config.FORCE_SUB_LINK and not await check_subscription(update, context):
        return

    user_input = update.message.text
    try:
        number = int(user_input)
        if number < 1:
            await update.message.reply_text("❌ Please enter a positive number.")
            return
        
        message_id = Config.BASE_MESSAGE_ID + (number - 1)
        
        sent_msg = await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=Config.CHANNEL_ID,
            message_id=message_id
        )
        # Auto-delete after 5 minutes
        try:
            await auto_delete(sent_msg)
        except Exception as e:
            logger.error(f"Auto-delete error: {e}")

    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ File not found for this number.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMINS:
        await update.message.reply_text("❌ Admin-only command!")
        return

    replied_msg = update.message.reply_to_message
    if not replied_msg:
        await update.message.reply_text("⚠️ Reply to a message to broadcast!")
        return

    users = get_all_users()
    success = 0
    for user in users:
        try:
            await replied_msg.copy(user)
            success += 1
        except Exception as e:
            logger.error(f"Broadcast error for {user}: {e}")
    await update.message.reply_text(f"Broadcast complete! Sent to {success}/{len(users)} users.")

# ================== MAIN FUNCTION ==================
def main():
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(MessageHandler(filters.Regex(r'^\d+$'), handle_number))
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
