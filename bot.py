from telegram import Update, Message
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from config import Config
import logging
import sqlite3
import asyncio

# Enable detailed logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== DATABASE SETUP ==================
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
conn.commit()

def add_user(user_id: int):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_all_users():
    cursor.execute("SELECT user_id FROM users")
    return [row[0] for row in cursor.fetchall()]

# ================== FIXED AUTO-DELETE ==================
async def auto_delete(message: Message, delay: int):
    """Delete a Telegram Message object after delay"""
    try:
        await asyncio.sleep(delay)
        await message.delete()
        logger.info(f"Deleted message {message.message_id}")
    except Exception as e:
        logger.error(f"Delete failed: {e}")

# ================== COMMAND HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)
    
    start_msg = await update.message.reply_text(
        f"Hi {user.mention_html()}! 👋\n"
        "Send a number to get the corresponding file!\n"
        "This message will self-destruct in 30 seconds.",
        parse_mode="HTML"
    )
    
    # Delete start message and user's /start command
    asyncio.create_task(auto_delete(start_msg, 30))
    asyncio.create_task(auto_delete(update.message, 10))

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_msg = update.message
        number = int(user_msg.text)
        
        if number < 1:
            reply = await user_msg.reply_text("❌ Enter positive number")
            asyncio.create_task(auto_delete(reply, 10))
            asyncio.create_task(auto_delete(user_msg, 10))
            return
        
        message_id = Config.BASE_MESSAGE_ID + (number - 1)
        
        # Use forward_message to get full Message object for deletion
        forwarded_msg = await context.bot.forward_message(
            chat_id=user_msg.chat_id,
            from_chat_id=Config.CHANNEL_ID,
            message_id=message_id
        )
        
        # Schedule deletions
        asyncio.create_task(auto_delete(forwarded_msg, 60))  # Delete forwarded file after 60s
        asyncio.create_task(auto_delete(user_msg, 10))       # Delete user's input
        
    except ValueError:
        reply = await update.message.reply_text("⚠️ Enter valid number")
        asyncio.create_task(auto_delete(reply, 10))
        asyncio.create_task(auto_delete(update.message, 10))
    except Exception as e:
        logger.error(f"Error: {e}")
        reply = await update.message.reply_text("⚠️ File not found")
        asyncio.create_task(auto_delete(reply, 10))
        asyncio.create_task(auto_delete(update.message, 10))

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in Config.ADMINS:
        reply = await update.message.reply_text("❌ Admin only!")
        asyncio.create_task(auto_delete(reply, 10))
        return

    if not update.message.reply_to_message:
        reply = await update.message.reply_text("⚠️ Reply to a message")
        asyncio.create_task(auto_delete(reply, 10))
        return

    users = get_all_users()
    success = 0
    for user_id in users:
        try:
            await update.message.reply_to_message.copy(user_id)
            success += 1
        except Exception as e:
            logger.error(f"Broadcast fail {user_id}: {e}")
    
    report = await update.message.reply_text(f"✅ Sent to {success}/{len(users)} users")
    asyncio.create_task(auto_delete(report, 30))
    asyncio.create_task(auto_delete(update.message, 10))

# ================== MAIN FUNCTION ==================
def main():
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(MessageHandler(filters.Regex(r'^\d+$'), handle_number))
    
    application.run_polling()

if __name__ == "__main__":
    main()
