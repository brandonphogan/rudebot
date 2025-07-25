"""
Helpers for formatting, sending, and fetching responses for Rudebot commands and events.
Includes BotResponse dataclass, response formatting, DB fetchers, and send logic.
"""
import discord
import logging
from typing import Optional, Union, List
from dataclasses import dataclass
from db.models import Response
from db.session import get_session
import random

@dataclass
class BotResponse:
    """
    Data structure for holding all parts of a bot response.
    """
    text: Optional[str] = None
    gif_url: Optional[str] = None
    action: Optional[str] = None

def format_response_text(user: Union[discord.Member, discord.User], text: str, emote: str) -> str:
    """
    Format a response message by combining a user mention, text, and emote.
    """
    parts = [user.mention]
    if text:
        parts.append(text)
    if emote:
        parts.append(emote)
    return " ".join(parts).strip()

async def send_response(
    target: Union[discord.abc.Messageable, discord.ext.commands.Context],
    response: BotResponse,
    logger: Optional[logging.Logger] = None
):
    """
    Send a text and/or gif response to a Discord context or channel, and log the action.
    """
    user = getattr(target, 'author', None) or getattr(target, 'user', None)
    channel_id = getattr(target, 'channel', getattr(target, 'id', None))
    if hasattr(channel_id, 'id'):
        channel_id = channel_id.id
    guild_id = getattr(getattr(target, 'guild', None), 'id', None)
    if not guild_id and hasattr(target, 'guild'):
        guild_id = target.guild.id

    if response.text:
        await target.send(response.text)
        if logger:
            logger.info(f"Sent response to {user} in channel {channel_id} (guild {guild_id}): {response.text}")
    if response.gif_url:
        embed = discord.Embed()
        embed.set_image(url=response.gif_url)
        await target.send(embed=embed)
        if logger:
            logger.info(f"Sent gif to {user} in channel {channel_id} (guild {guild_id}): {response.gif_url}")
    if response.action and logger:
        logger.info(f"Performed action '{response.action}' for {user} in channel {channel_id} (guild {guild_id})")

def get_responses(category: str, trigger: str) -> List[Response]:
    """
    Fetch all Response entries from the database for a given category and trigger.
    Returns a list of Response ORM objects.
    """
    with get_session() as session:
        responses = session.query(Response).filter_by(category=category, trigger=trigger).all()
        return responses

def get_random_response(category: str, trigger: str) -> Optional[Response]:
    """
    Fetch a random Response entry from the database for a given category and trigger.
    Returns a single Response ORM object or None.
    """
    responses = get_responses(category, trigger)
    if not responses:
        return None
    return random.choice(responses) 