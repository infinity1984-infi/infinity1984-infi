class Config:
    # Telegram API Credentials (Get from https://my.telegram.org/apps)
    API_ID = 1234567
    API_HASH = "your_api_hash_here"
    BOT_TOKEN = "your_bot_token_here"

    # Channel Configuration
    CHANNEL_ID = -1002610839118  # Replace with your channel ID (include -100)
    BASE_MESSAGE_ID = 4  # Message ID for number "1"

    # Force Subscription (Use your channel invite link)
    FORCE_SUB_LINK = "https://t.me/Sardorkinoo"  # e.g., https://t.me/joinchat/ABC123

    # Admins (Your Telegram User ID)
    ADMINS = [6285668838]  # Get from @userinfobot

    # Button URLs (Customize these)
    BUTTON_URLS = {
        "channel": {"text": "📢 Channel", "url": "https://t.me/Hanime_System"},
        "support": {"text": "💬 Support", "url": "https://t.me/+pf-4srRnotc0YWQ1"}
    }
