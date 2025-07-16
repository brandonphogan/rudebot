import logging
import os

from dotenv import load_dotenv

from bot.rude_bot import RudeBot

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

bot = RudeBot(token=token, handler=handler, level=logging.DEBUG)
bot.run()