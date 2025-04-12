from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import Config
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! 👋\n"
        "Send a number to get the corresponding file from the channel!"
    )

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        number = int(user_input)
        if number < 1:
            await update.message.reply_text("❌ Please enter a positive number.")
            return
        
        message_id = Config.BASE_MESSAGE_ID + (number - 1)
        
        await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=Config.CHANNEL_ID,
            message_id=message_id
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Invalid number! No file exists for this number.")

def main():
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex(r'^\d+$'), handle_number))
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
