"""
Cog for handling Discord events in Rudebot.
Currently greets users when they join a voice channel using a random event response.
"""
from discord.ext import commands
import os
import random
from data.models import Response
from data.session import get_session
from services.response_service import BotResponse, send_response
from utils.logging_util import get_logger
from services.channel_service import resolve_text_channel

class Events(commands.Cog):
    """
    Handles Discord events such as on_ready and on_voice_state_update.
    Sends greetings to users joining voice channels.
    """
    def __init__(self, bot):
        self.bot = bot
        # Read the text channel ID from the environment
        self.text_channel_id = os.getenv('TEXT_CHANNEL_ID')
        if self.text_channel_id:
            try:
                self.text_channel_id = int(self.text_channel_id)
            except ValueError:
                self.text_channel_id = None
        # Set up a dedicated logger for this cog
        self.logger = get_logger('events', 'logs/events.log')

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Log when the bot is ready.
        """
        self.logger.info(f"Logged in as {self.bot.user.name} with ID {self.bot.user.id}")
        print(f"Logged in as {self.bot.user.name} with ID {self.bot.user.id}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Send a random event response when a non-bot member newly joins any voice channel.
        """
        try:
            # Only act when a user joins a voice channel (not moves or leaves)
            if before.channel is None and after.channel is not None:
                if member.bot:
                    return
                # Resolve the text channel to send the greeting
                text_channel = resolve_text_channel(member.guild, self.text_channel_id)
                if not text_channel:
                    self.logger.warning(f"No valid text channel found for guild {member.guild.id}")
                    return
                # Fetch a random event response from the database
                with get_session() as session:
                    responses = session.query(Response).filter_by(category='event', trigger='join').all()
                    if not responses:
                        self.logger.warning(f"No event responses found in database.")
                        return
                    response = random.choice(responses)
                # Build the BotResponse dataclass
                bot_response = BotResponse(
                    text=response.text or "",
                    gif_url=response.gif_url or "",
                    action=response.action or None
                )
                # Send the greeting response
                await send_response(
                    text_channel,
                    bot_response,
                    logger=self.logger
                )
        except Exception as e:
            self.logger.error(f"Error in on_voice_state_update: {e}", exc_info=True)

# Required setup function for loading the cog
async def setup(bot):
    await bot.add_cog(Events(bot))