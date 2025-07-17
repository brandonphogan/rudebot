import discord
from discord.ext import commands

import asyncio
import logging
import os

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,  # Or DEBUG for more details
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

async def main():
	# Get dcord info from .env
	load_dotenv()
	token = os.getenv('DISCORD_TOKEN')
	text_channel_id = os.getenv('TEXT_CHANNEL_ID')

	# Set intents
	intents = discord.Intents.default()
	intents.presences = True
	intents.message_content = True
	intents.voice_states = True
	intents.members = True

	# Init log handler
	handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

	# Init bot
	bot = commands.Bot(command_prefix="!", intents=intents)

	# Load cogs
	for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
			await bot.load_extension(f'cogs.{filename[:-3]}')

	# Run bot
	await bot.start(token)

asyncio.run(main())