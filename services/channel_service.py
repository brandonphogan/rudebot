"""
Channel service for Rudebot.
Handles channel resolution and utilities.
Separates business logic from Discord-specific cog implementation.
"""


def resolve_text_channel(guild, text_channel_id):
    """
    Resolve the text channel to use for sending messages in a guild.
    Returns the channel with the given ID, or the system channel if not found.
    """
    channel = None
    if text_channel_id:
        channel = guild.get_channel(text_channel_id)
    if not channel:
        channel = guild.system_channel
    return channel