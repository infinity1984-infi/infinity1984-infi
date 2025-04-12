from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from config import Config
import logging
import sqlite3
from asyncio import sleep, create_task

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
                (user_id INTEGER PRIMARY KEY,
                 invite_link TEXT,
                 has_joined BOOLEAN DEFAULT FALSE)''')
conn.commit()

def add_user(user_id: int, invite_link: str):
    cursor.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)",
                  (user_id, invite_link, False))
    conn.commit()

def update_join_status(user_id: int):
    cursor.execute("UPDATE users SET has_joined = TRUE WHERE user_id = ?", 
                  (user_id,))
    conn.commit()

def get_user(user_id: int):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

# ================== MEMBERSHIP CHECKS ==================
async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(Config.CHANNEL_ID, user_id)
        return member.status not in ["left", "kicked"]
    except Exception as e:
        logger.error(f"Membership check error: {e}")
        return False

async def periodic_membership_check(context: ContextTypes.DEFAULT_TYPE):
    """Check pending users every 30 seconds"""
    cursor.execute("SELECT user_id FROM users WHERE has_joined = FALSE")
    for row in cursor.fetchall():
        user_id = row[0]
        if await check_membership(user_id, context):
            update_join_status(user_id)
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ Verification complete! You can now use the bot."
            )

# ================== COMMAND HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        # Generate unique 1-use invite link
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=Config.CHANNEL_ID,
            name=f"invite_{user.id}",
            member_limit=1
        )
        
        add_user(user.id, invite_link.invite_link)
        
        await update.message.reply_text(
            "🔐 Join our channel with this link to unlock the bot:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Channel", url=invite_link.invite_link)]
            ])
        )
        
        # Start periodic checks (every 30 seconds)
        if not context.job_queue.get_jobs_by_name("membership_check"):
            context.job_queue.run_repeating(
                periodic_membership_check,
                interval=30,
                first=10,
                name="membership_check"
            )
            
    except Exception as e:
        logger.error(f"Start error: {e}")
        await update.message.reply_text("❌ Bot needs admin rights in the channel!")

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Instant verification command"""
    user = update.effective_user
    user_data = get_user(user.id)
    
    if not user_data:
        await update.message.reply_text("⚠️ Use /start first!")
        return
    
    if await check_membership(user.id, context):
        update_join_status(user.id)
        await update.message.reply_text("✅ Verification successful!")
    else:
        await update.message.reply_text(
            "⚠️ Join the channel first!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Now", url=user_data[1])]
            ])
        )

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = get_user(user.id)
    
    if not user_data or not user_data[2]:
        await update.message.reply_text("🔒 Complete verification first!\nUse /verify")
        return
    
    try:
        number = int(update.message.text)
        message_id = Config.BASE_MESSAGE_ID + (number - 1)
        
        sent_msg = await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=Config.CHANNEL_ID,
            message_id=message_id
        )
        # Auto-delete after 5 minutes
        create_task(auto_delete(sent_msg))
        
    except Exception as e:
        logger.error(f"Number error: {e}")
        await update.message.reply_text("⚠️ Invalid number or missing file!")

async def auto_delete(message, delay: int = 300):
    """Delete message after delay"""
    await sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Auto-delete failed: {e}")

# ================== MAIN FUNCTION ==================
def main():
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify))
    application.add_handler(MessageHandler(filters.Regex(r'^\d+$'), handle_number))
    
    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()
