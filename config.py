class Config:
    API_ID = 1234567       # Get from https://my.telegram.org/apps
    API_HASH = "your_api_hash"
    BOT_TOKEN = "your_bot_token"
    CHANNEL_ID = -1002610839118  # Replace with your channel ID (include -100)
    BASE_MESSAGE_ID = 4   # Starting message ID (e.g., 1 → 4, 2 → 5)
    ADMINS = [6285668838]  # Your Telegram user ID (get from @userinfobot)
    FORCE_SUB_CHANNEL = -1002590122361  # Your channel ID (optional: set to None to disable)
    BUTTON_URLS = {
        "button1": {"text": "📢 Channel", "url": "https://t.me/Hanime_System"},
        "button2": {"text": "🌟 Rate Us", "url": "https://t.me/+pf-4srRnotc0YWQ1"}
    }
    
class Config:
    # Telegram API Credentials (Get from https://my.telegram.org/apps)
    API_ID = 1234567
    API_HASH = "your_api_hash_here"
    BOT_TOKEN = "your_bot_token_here"

    # Channel Configuration
    CHANNEL_ID = -1002610839118  # Replace with your channel ID (include -100)
    BASE_MESSAGE_ID = 4  # Starting message ID (e.g., 1 → message 4)

    # Force Subscription (Use an invite link instead of channel ID)
    FORCE_SUB_LINK = "https://t.me/Sardorkinoo"  # e.g., https://t.me/joinchat/ABCxyz123

    # Admins (Your Telegram User ID)
    ADMINS = [6285668838]

    # Button URLs (Customize these)
    BUTTON_URLS = {
        "button1": {"text": "📢 Join Channel", "url": "https://t.me/Hanime_System"},
        "button2": {"text": "🌟 Support", "url": "https://t.me/+pf-4srRnotc0YWQ1"}
    }
