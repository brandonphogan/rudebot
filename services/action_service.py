"""
Action service for Rudebot.
Handles bot actions like kick and scatter operations.
Separates business logic from Discord-specific cog implementation.
"""
import random
import discord
import logging


async def handle_action(action: str, ctx: discord.ext.commands.Context, logger: logging.Logger = None):
    """
    Perform a special action (kick, scatter, etc.) in response to a command or event.
    """
    if not action:
        return
    match action.lower():
        case "kick":
            # Disconnect the user from their current voice channel
            if ctx.author.voice and ctx.author.voice.channel:
                await ctx.author.move_to(None, reason=None)
                if logger:
                    logger.info(f"Kicked {ctx.author} from voice channel in guild {ctx.guild.id}")
        case "scatter":
            # Move all users in the current voice channel to random other channels
            current_vc = ctx.author.voice.channel if ctx.author.voice else None
            if current_vc:
                other_vcs = [vc for vc in ctx.guild.voice_channels if vc != current_vc]
                if other_vcs:
                    members = current_vc.members
                    if members:
                        bot_member = ctx.guild.me
                        bot_top_role = bot_member.top_role
                        for member in members:
                            if member == bot_member:
                                continue
                            if member.top_role.position <= bot_top_role.position:
                                target_vc = random.choice(other_vcs)
                                await member.move_to(target_vc)
                                if logger:
                                    logger.info(f"Scattered {member} to channel {target_vc.id} in guild {ctx.guild.id}")