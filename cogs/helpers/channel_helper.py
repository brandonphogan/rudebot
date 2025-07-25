"""
Helper for resolving the correct text channel for a guild in Rudebot.
Prefers a configured channel ID, falls back to the system channel.
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