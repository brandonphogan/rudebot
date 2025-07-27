"""
Music service for Rudebot.
Handles music queue management, audio downloading, and playback logic.
Separates business logic from Discord-specific cog implementation.
"""
import time
import os
import yt_dlp
from typing import List, Optional
from data.models import SongQueue
from data.session import get_session


# Audio storage directory
AUDIO_DIR = os.path.join('data', 'dj_audio')
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)


def get_total_song_count(guild_id: str) -> int:
    """
    Get the total number of songs stored for a guild (queue + played).
    """
    with get_session() as session:
        return session.query(SongQueue).filter_by(guild_id=guild_id).count()


def download_audio(url_or_query: str) -> str:
    """
    Download audio using yt-dlp and return the file path.
    """
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'default_search': 'ytsearch',
        'extract_flat': False,
        'outtmpl': os.path.join(AUDIO_DIR, '%(id)s.%(ext)s'),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url_or_query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            return ydl.prepare_filename(info)
        except Exception as e:
            print(f"yt-dlp download failed: {e}")
            return None


def add_song(guild_id: str, user_id: str, title: str, url: str) -> dict:
    """
    Add a song to the queue for a guild. Downloads audio and stores file path.
    Returns a dict with song info.
    """
    file_path = download_audio(url)
    with get_session() as session:
        song = SongQueue(
            guild_id=guild_id,
            user_id=user_id,
            title=title,
            url=url,
            file_path=file_path,
            added_at=int(time.time())
        )
        session.add(song)
        session.commit()
        return {"title": song.title, "id": song.id, "user_id": song.user_id, "url": song.url, "file_path": song.file_path}


def remove_song(song_id: int) -> bool:
    """
    Remove a song from the queue by its ID.
    """
    with get_session() as session:
        song = session.query(SongQueue).filter_by(id=song_id).first()
        if song:
            session.delete(song)
            session.commit()
            return True
        return False


def get_queue(guild_id: str) -> List[SongQueue]:
    """
    Get the current queue for a guild (not played yet).
    """
    with get_session() as session:
        return session.query(SongQueue).filter_by(guild_id=guild_id).order_by(SongQueue.added_at).all()


def mark_played(song_id: int) -> bool:
    """
    Mark a song as played (no-op, kept for compatibility).
    """
    # No longer needed, but kept for compatibility with DJHandler
    return True


def cleanup_orphaned_files():
    """
    Clean up audio files that are no longer referenced in the database.
    """
    referenced_files = set()
    with get_session() as session:
        for song in session.query(SongQueue).all():
            if song.file_path:
                referenced_files.add(song.file_path)
    
    for fname in os.listdir(AUDIO_DIR):
        fpath = os.path.join(AUDIO_DIR, fname)
        if fpath not in referenced_files:
            try:
                os.remove(fpath)
            except Exception as e:
                print(f"Failed to delete orphaned audio file {fpath}: {e}")


# Initialize cleanup on import
cleanup_orphaned_files()