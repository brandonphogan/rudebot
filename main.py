import logging
import os

from dotenv import load_dotenv

from bot.rude_bot import RudeBot

# Get dcord info from .env
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
text_channel_id = os.getenv('TEXT_CHANNEL_ID')
discord_params = {"token": token, "text_channel_id": text_channel_id}

# Init log handler
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Init and run bot
bot = RudeBot(**discord_params, handler=handler, log_level=logging.DEBUG)
bot.run()