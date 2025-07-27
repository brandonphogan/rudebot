"""
Simplified DJ/music cog for Rudebot.
Provides basic music queue management and playback commands.
"""
# --- Imports ---
import asyncio
import os
import discord
from discord.ext import commands
from services.music_service import add_song, remove_song, get_queue, mark_played, get_total_song_count
from utils.logging_util import get_logger

FFMPEG_OPTIONS = {
    'options': '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

class Music(commands.Cog):
    """
    Music cog for Rudebot.
    Provides music queue management and playback commands.
    """
    def __init__(self, bot):
        self.bot = bot
        self.logger = get_logger('music', 'logs/music.log')
        self.cleanup_task = None
        self.current_song = {}  # guild_id: song_id
        self.is_paused = {}     # guild_id: bool

    async def cog_load(self):
        """
        Start the background cleanup task when the cog is loaded.
        """
        self.cleanup_task = asyncio.create_task(self.cleanup_history_loop())

    async def cleanup_history_loop(self):
        """
        Periodically clean up old song history from the database.
        Currently disabled - cleanup functionality not implemented.
        """
        return  # Exit immediately since cleanup is not implemented

    @commands.group(name="dj", invoke_without_command=True, case_insensitive=True)
    async def dj(self, ctx, *, query: str = None):
        """
        Add a song to the queue if a song is provided, or show the current queue and controls.
        If called with no subcommand or song, display available DJ commands.
        """
        if query:
            song = add_song(str(ctx.guild.id), str(ctx.author.id), query, query)
            await ctx.send(f"Added **{song['title']}** to the queue.")
            self.logger.info(f"{ctx.author} added '{song['title']}' to the queue in guild {ctx.guild.id}")
            vc = ctx.voice_client
            queue = get_queue(str(ctx.guild.id))
            if (not vc or not vc.is_playing()) and ctx.author.voice and ctx.author.voice.channel:
                await self.play_next(ctx)
                return  # Let play_next handle queue display
        else:
            # Dynamically generate help message from registered subcommands, including the group help text
            help_lines = [f"**DJ Commands:**"]
            help_lines.append("!dj — Show available DJ commands and the current queue.")
            help_lines.append("!dj <song> — Add a song to the queue by title or URL. If the queue is empty, play the song immediately.")
            for cmd in self.dj.commands:
                if cmd.hidden:
                    continue
                aliases = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
                help_lines.append(f"!dj {cmd.name}{aliases} — {cmd.help or 'No description.'}")
            await ctx.send("\n".join(help_lines))
        await self.show_queue(ctx)

    @dj.command(name="add")
    async def add(self, ctx, *, query: str):
        """
        Add a song to the queue by title or URL. If the queue is empty, play the song immediately.
        """
        total_songs = get_total_song_count(str(ctx.guild.id))
        if total_songs >= 10:
            await ctx.send("The song storage limit (10) has been reached. Please remove songs before adding more.")
            return
        queue = get_queue(str(ctx.guild.id))
        if not queue:
            # Queue is empty, add and play immediately; let play_next send the now playing message
            song = add_song(str(ctx.guild.id), str(ctx.author.id), query, query)
            self.logger.info(f"{ctx.author} added and started '{song['title']}' in guild {ctx.guild.id}")
            await self.play_next(ctx)
        else:
            # Queue is not empty, just add
            song = add_song(str(ctx.guild.id), str(ctx.author.id), query, query)
            await ctx.send(f"Added **{song['title']}** to the queue.")
            self.logger.info(f"{ctx.author} added '{song['title']}' to the queue in guild {ctx.guild.id}")
            await self.show_queue(ctx)

    @dj.command(name="remove")
    async def remove(self, ctx, index: int):
        """
        Remove a song from the queue by its position (1-based).
        """
        queue = get_queue(str(ctx.guild.id))
        if 1 <= index <= len(queue):
            song = queue[index-1]
            remove_song(song.id)
            await ctx.send(f"Removed **{song.title}** from the queue.")
            self.logger.info(f"{ctx.author} removed '{song.title}' from the queue in guild {ctx.guild.id}")
        else:
            await ctx.send("Invalid song index.")
            self.logger.warning(f"{ctx.author} tried to remove invalid index {index} in guild {ctx.guild.id}")
        await self.show_queue(ctx)

    @dj.command(name="next")
    async def next(self, ctx):
        """
        Skip to the next song in the queue.
        """
        queue = get_queue(str(ctx.guild.id))
        if queue:
            mark_played(queue[0].id)
            await ctx.send(f"Skipped to next song.")
            self.logger.info(f"{ctx.author} skipped to next song in guild {ctx.guild.id}")
            await self.play_next(ctx)
        else:
            await ctx.send("No songs in the queue.")
            self.logger.info(f"{ctx.author} tried to skip with empty queue in guild {ctx.guild.id}")
        await self.show_queue(ctx)

    @dj.command(name="pause")
    async def pause(self, ctx):
        """
        Pause playback.
        """
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.pause()
            self.is_paused[ctx.guild.id] = True
            await ctx.send("Paused playback.")
            self.logger.info(f"Paused playback in guild {ctx.guild.id}")
        else:
            await ctx.send("Nothing is playing.")
            self.logger.info(f"{ctx.author} tried to pause when nothing was playing in guild {ctx.guild.id}")
        await self.show_queue(ctx)

    @dj.command(name="resume", aliases=["play"])
    async def resume(self, ctx):
        """
        Resume playback if paused.
        """
        vc = ctx.voice_client
        if vc and self.is_paused.get(ctx.guild.id):
            vc.resume()
            self.is_paused[ctx.guild.id] = False
            await ctx.send("Resumed playback.")
            self.logger.info(f"Resumed playback in guild {ctx.guild.id}")
        else:
            await ctx.send("Nothing is paused.")
            self.logger.info(f"{ctx.author} tried to resume when nothing was paused in guild {ctx.guild.id}")
        await self.show_queue(ctx)

    @dj.command(name="queue")
    async def queue_cmd(self, ctx):
        """
        Show the current queue.
        """
        await self.show_queue(ctx)

    @dj.command(name="purge", hidden=True)
    async def purge(self, ctx):
        """
        Remove all songs from the queue and delete their music files. (Admin only, not listed in help)
        """
        # Fetch all songs in the queue for this guild
        queue = get_queue(str(ctx.guild.id))
        count = 0
        errors = []
        for song in queue:
            # Attempt to delete the audio file if it exists
            if song.file_path and os.path.exists(song.file_path):
                try:
                    os.remove(song.file_path)
                except Exception as e:
                    error_msg = f"Failed to delete file {song.file_path}: {e}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
            # Remove the song from the database
            try:
                remove_song(song.id)
                count += 1
            except Exception as e:
                error_msg = f"Failed to remove song ID {song.id} from DB: {e}"
                self.logger.error(error_msg)
                errors.append(error_msg)
        # Send a summary message to the user
        if errors:
            await ctx.send(f"Removed {count} song(s) from the queue, but some errors occurred:\n" + "\n".join(errors))
        else:
            await ctx.send(f"Removed {count} song(s) from the queue.")
        self.logger.info(f"{ctx.author} purged the queue in guild {ctx.guild.id} (removed {count} songs)")

    async def play_next(self, ctx):
        """
        Play the next song in the queue, or disconnect if queue is empty.
        """
        queue = get_queue(str(ctx.guild.id))
        if not queue:
            await ctx.send("Queue is empty. Leaving voice channel.")
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
            self.current_song.pop(ctx.guild.id, None)
            self.logger.info(f"Queue empty, disconnected in guild {ctx.guild.id}")
            return
        song = queue[0]
        audio_file = song.file_path
        if not audio_file or not os.path.exists(audio_file):
            await ctx.send(f"Audio file not found for: {song.title}")
            self.logger.error(f"Audio file missing for '{song.title}' in guild {ctx.guild.id}")
            mark_played(song.id)
            await self.play_next(ctx)
            return
        vc = ctx.voice_client
        if not vc:
            if ctx.author.voice and ctx.author.voice.channel:
                vc = await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You must be in a voice channel to play music.")
                self.logger.warning(f"User {ctx.author} not in voice channel in guild {ctx.guild.id}")
                return
        self.current_song[ctx.guild.id] = song.id
        self.is_paused[ctx.guild.id] = False
        remove_song(song.id)
        source = discord.FFmpegPCMAudio(audio_file, **FFMPEG_OPTIONS)
        vc.play(source, after=lambda e: (os.remove(audio_file) if os.path.exists(audio_file) else None, asyncio.run_coroutine_threadsafe(self.after_song(ctx, song.id, e), self.bot.loop)))
        await ctx.send(f"Now playing: **{song.title}**")
        self.logger.info(f"Started playback of '{song.title}' in guild {ctx.guild.id}")
        await self.show_queue(ctx)

    async def after_song(self, ctx, song_id, error):
        """
        Callback after a song finishes playing. Remove the song from the database and auto-play next.
        """
        if error:
            self.logger.error(f"Error during playback: {error}")
        remove_song(song_id)
        await self.play_next(ctx)

    async def show_queue(self, ctx):
        """
        Send a message showing the current queue for the guild, excluding the current song.
        If a song is currently playing, show it separately as 'Now Playing'.
        """
        queue = get_queue(str(ctx.guild.id))
        current_song_id = self.current_song.get(ctx.guild.id)
        now_playing = None
        rest_queue = []
        for i, song in enumerate(queue):
            if song.id == current_song_id:
                now_playing = song
            else:
                rest_queue.append(song)
        lines = []
        if now_playing:
            lines.append(f"**Now Playing:** {now_playing.title}")
        if rest_queue:
            lines.append("**Up Next:**\n" + "\n".join(f"{i+1}. {song.title}" for i, song in enumerate(rest_queue)))
        else:
            if not now_playing:
                lines.append("The queue is empty.")
        await ctx.send("\n".join(lines))

# Required setup function for loading the cog
async def setup(bot):
    await bot.add_cog(Music(bot)) 