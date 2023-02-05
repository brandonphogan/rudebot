import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", help_command=None, intents=intents)

cogs: list = ["functions.messages.messagehandler",
              "functions.channeljoin.joinhandler"]


@bot.event
async def on_ready():
    print("Loading cogs...")
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"Loaded cog {cog}")
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print("Failed to load cog {}\n{}".format(cog, exc))

    print("RudeBot is ruining your day!")


bot.run(os.getenv('TOKEN'))
