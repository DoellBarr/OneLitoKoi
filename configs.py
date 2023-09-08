from dotenv import load_dotenv
import os

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
admin_chat_id = os.getenv("ADMIN_CHAT_ID")
auction_chat_id = os.getenv("AUCTION_CHAT_ID")
bot_username = ""
if admin_chat_id:
    admin_chat_id = int(admin_chat_id)
if auction_chat_id:
    auction_chat_id = int(auction_chat_id)
redis_url = os.getenv("REDIS_URL")
