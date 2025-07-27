"""
Music service for Rudebot.
Handles music queue management for streaming playback.
Separates business logic from Discord-specific cog implementation.
"""
import time
from typing import List
from data.models import SongQueue
from data.session import get_session


def get_total_song_count(guild_id: str) -> int:
    """
    Get the total number of songs stored for a guild (queue + played).
    """
    with get_session() as session:
        return session.query(SongQueue).filter_by(guild_id=guild_id).count()




def add_song(guild_id: str, user_id: str, title: str, url: str) -> dict:
    """
    Add a song to the queue for a guild.
    Returns a dict with song info.
    """
    with get_session() as session:
        song = SongQueue(
            guild_id=guild_id,
            user_id=user_id,
            title=title,
            url=url,
            file_path=None,
            added_at=int(time.time())
        )
        session.add(song)
        session.commit()
        return {"title": song.title, "id": song.id, "user_id": song.user_id, "url": song.url}


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




