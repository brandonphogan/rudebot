"""
Main entry point for Rudebot Discord bot.
Handles bot setup, cog loading, and startup/shutdown lifecycle.
"""
import discord
from discord.ext import commands

import asyncio
import logging
import os

from dotenv import load_dotenv
from utils.logging_util import setup_logging
from services.console_service import ConsoleService

# Set up centralized logging for the project
setup_logging()
logger = logging.getLogger("main")

def discover_cogs(base_dir='cogs'):
    """
    Discover all valid cog modules in the cogs directory (no subdirectories).
    Only loads files that contain an async setup function.
    """
    cogs = []
    for file in os.listdir(base_dir):
        if file.endswith('.py') and file != '__init__.py' and not file.startswith('_'):
            module = file[:-3]
            abs_path = os.path.join(base_dir, file)
            with open(abs_path, 'r', encoding='utf-8') as f:
                if 'async def setup(' not in f.read():
                    continue
            cogs.append(f'cogs.{module}')
    return cogs

async def main():
    """
    Main async entry point for the bot.
    Loads environment, sets up bot, loads cogs, and starts the bot.
    """
    # Load environment variables (including DISCORD_TOKEN)
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')

    # Set Discord bot intents
    intents = discord.Intents.default()
    intents.presences = True
    intents.message_content = True
    intents.voice_states = True
    intents.members = True

    # Initialize the bot
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Initialize console service
    console = ConsoleService(bot)

    # Load all cogs from the cogs directory
    loaded_cogs = {}
    for cog_name in discover_cogs():
        try:
            await bot.load_extension(cog_name)
            logger.info(f"Loaded cog: {cog_name}")
            loaded_cogs[cog_name] = 'Loaded'
        except Exception as e:
            logger.error(f"Failed to load cog: {cog_name} - {e}", exc_info=True)
            loaded_cogs[cog_name] = f'Failed: {e}'

    # Log a summary of all loaded cogs
    logger.info("Cog load summary:")
    for cog, status in loaded_cogs.items():
        logger.info(f"  {cog}: {status}")

    logger.info("Rudebot is starting up.")
    
    # Start console interface
    console.start()
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Bot encountered an exception: {e}", exc_info=True)
        raise
    finally:
        console.stop()
        logger.info("Rudebot is shutting down.")

if __name__ == "__main__":
    # Run the main async entry point
    asyncio.run(main())