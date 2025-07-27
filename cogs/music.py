"""
Simple music cog for Rudebot.
Provides basic streaming music functionality.
"""
import asyncio
import discord
import yt_dlp
from discord.ext import commands
from services.music_service import add_song, remove_song, get_queue, get_total_song_count
from utils.logging_util import get_logger

class Music(commands.Cog):
    """Simple music cog with streaming playback."""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = get_logger('music', 'logs/music.log')
        self.current_song = {}  # guild_id: song_id
        
    @commands.group(name="dj", invoke_without_command=True)
    async def dj(self, ctx, *, query: str = None):
        """DJ music commands."""
        if query:
            await self._add_song(ctx, query)
        else:
            await self._show_queue(ctx)
            
    @dj.command(name="add")
    async def add_cmd(self, ctx, *, query: str):
        """Add a song to the queue (explicit command)."""
        await self._add_song(ctx, query)
            
    async def _add_song(self, ctx, query: str):
        """Internal method to add a song."""
        if not ctx.author.voice:
            await ctx.send("You must be in a voice channel.")
            return
            
        # Check queue limit
        total_songs = get_total_song_count(str(ctx.guild.id))
        if total_songs >= 10:
            await ctx.send("Queue is full (10 songs max).")
            return
            
        try:
            # Get video info and extract streaming URL
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'default_search': 'ytsearch',
                'extract_flat': False,
                'format': 'bestaudio/best',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                    
                title = info.get('title', 'Unknown')
                # Store the actual YouTube video ID/URL for later streaming
                video_id = info.get('id')
                url = f"https://www.youtube.com/watch?v={video_id}" if video_id else info.get('webpage_url')
                
                if not url:
                    raise Exception("Could not get video URL")
                
            # Add to database queue
            add_song(str(ctx.guild.id), str(ctx.author.id), title, url)
            await ctx.send(f"Added: {title}")
            self.logger.info(f"Added '{title}' to queue in guild {ctx.guild.id}")
            
            # Start playing if not already playing
            if not ctx.voice_client or not ctx.voice_client.is_playing():
                await self._play_next(ctx)
                
        except Exception as e:
            await ctx.send("Failed to add song.")
            self.logger.error(f"Failed to add song '{query}': {e}")
            
    @dj.command(name="skip", aliases=["next"])
    async def skip(self, ctx):
        """Skip the current song."""
        if not ctx.voice_client:
            await ctx.send("Not playing music.")
            return
            
        # Check if there are more songs in queue
        queue = get_queue(str(ctx.guild.id))
        if len(queue) <= 1:  # Only current song or no songs
            await ctx.send("No more songs to skip to.")
            return
            
        ctx.voice_client.stop()
        await ctx.send("Skipped.")
        self.logger.info(f"Song skipped in guild {ctx.guild.id}")
        
    @dj.command(name="pause")
    async def pause(self, ctx):
        """Pause playback."""
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("Nothing is playing.")
            return
            
        ctx.voice_client.pause()
        await ctx.send("Paused.")
        self.logger.info(f"Playback paused in guild {ctx.guild.id}")
        
    @dj.command(name="resume")
    async def resume(self, ctx):
        """Resume playback."""
        if not ctx.voice_client or not ctx.voice_client.is_paused():
            await ctx.send("Nothing is paused.")
            return
            
        ctx.voice_client.resume()
        await ctx.send("Resumed.")
        self.logger.info(f"Playback resumed in guild {ctx.guild.id}")
        
    @dj.command(name="queue")
    async def queue_cmd(self, ctx):
        """Show the music queue."""
        await self._show_queue(ctx)
        
    async def _show_queue(self, ctx):
        """Show the music queue."""
        queue = get_queue(str(ctx.guild.id))
        if not queue:
            await ctx.send("Queue is empty.")
            return
            
        current_song_id = self.current_song.get(ctx.guild.id)
        lines = []
        
        # Show currently playing song
        if current_song_id:
            for song in queue:
                if song.id == current_song_id:
                    lines.append(f"Now Playing: {song.title}")
                    break
        
        # Show remaining queue
        remaining_songs = [song for song in queue if song.id != current_song_id]
        if remaining_songs:
            lines.append("Up Next:")
            for i, song in enumerate(remaining_songs[:10], 1):
                lines.append(f"{i}. {song.title}")
        elif not lines:  # No current song and no remaining songs
            lines.append("Queue is empty.")
            
        await ctx.send("\n".join(lines))
        
    @dj.command(name="help")
    async def help_cmd(self, ctx):
        """Show all DJ commands and their usage."""
        help_text = """
**DJ Music Commands:**

`!dj` - Show the current queue
`!dj <song>` - Add a song to the queue and play it
`!dj add <song>` - Explicitly add a song (use if song name conflicts with commands)
`!dj queue` - Show the current queue
`!dj skip` or `!dj next` - Skip to the next song (if available)
`!dj pause` - Pause the current song
`!dj resume` - Resume a paused song
`!dj remove <number>` - Remove a song from the queue by position
`!dj stop` - Stop music and clear the entire queue
`!dj help` - Show this help message

**Notes:**
- Queue limit: 10 songs maximum
- You must be in a voice channel to add songs
- Songs are streamed directly from YouTube
        """
        await ctx.send(help_text)
        
    @dj.command(name="remove")
    async def remove(self, ctx, index: int):
        """Remove a song from the queue by number."""
        queue = get_queue(str(ctx.guild.id))
        if not queue or index < 1 or index > len(queue):
            await ctx.send("Invalid song number.")
            return
            
        song = queue[index - 1]
        remove_song(song.id)
        await ctx.send(f"Removed: {song.title}")
        self.logger.info(f"Removed '{song.title}' from queue in guild {ctx.guild.id}")
        
    @dj.command(name="stop")
    async def stop(self, ctx):
        """Stop music and clear queue."""
        if ctx.voice_client:
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            
        # Clear current song tracking and queue
        self.current_song.pop(ctx.guild.id, None)
        queue = get_queue(str(ctx.guild.id))
        for song in queue:
            remove_song(song.id)
            
        await ctx.send("Music stopped and queue cleared.")
        self.logger.info(f"Music stopped in guild {ctx.guild.id}")
        
    async def _play_next(self, ctx):
        """Play the next song in queue."""
        queue = get_queue(str(ctx.guild.id))
        if not queue:
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
            return
            
        song = queue[0]
        
        # Connect to voice if needed
        if not ctx.voice_client:
            try:
                channel = ctx.author.voice.channel
                await channel.connect()
            except Exception as e:
                await ctx.send("Failed to connect to voice channel.")
                self.logger.error(f"Voice connection failed in guild {ctx.guild.id}: {e}")
                return
                
        try:
            # Get the actual streaming URL using yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'bestaudio/best',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song.url, download=False)
                stream_url = info['url']
            
            # Create audio source
            ffmpeg_opts = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
            }
            source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_opts)
            
            # Set current song and play with callback
            self.current_song[ctx.guild.id] = song.id
            ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(
                self._after_song(ctx, song.id, e), self.bot.loop
            ))
            
            await ctx.send(f"Now playing: {song.title}")
            self.logger.info(f"Playing '{song.title}' in guild {ctx.guild.id}")
            
        except Exception as e:
            await ctx.send("Failed to play song.")
            self.logger.error(f"Playback failed for '{song.title}': {e}")
            remove_song(song.id)
            await self._play_next(ctx)
            
    async def _after_song(self, ctx, song_id, error):
        """Callback after song finishes."""
        if error:
            self.logger.error(f"Playback error: {error}")
            
        # Clear current song tracking
        self.current_song.pop(ctx.guild.id, None)
        remove_song(song_id)
        await self._play_next(ctx)

async def setup(bot):
    await bot.add_cog(Music(bot))