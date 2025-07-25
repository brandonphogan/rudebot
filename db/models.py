"""
SQLAlchemy ORM models for Rudebot.
Includes unified Response model for all command and event responses.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class CommandType(Base):
    __tablename__ = 'command_types'
    id = Column(Integer, primary_key=True)
    command_type = Column(String(100), unique=True, nullable=False)
    # (Legacy) Used for normalization, not directly referenced by Response

class ActionType(Base):
    __tablename__ = 'action_types'
    id = Column(Integer, primary_key=True)
    action_type = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    # (Legacy) Used for normalization, not directly referenced by Response

class Response(Base):
    """
    Unified model for all bot responses (commands, events, etc.).
    category: 'command', 'event', etc.
    trigger: command name or event type (e.g., 'hello', 'join')
    text, gif_url, emote, action: response content
    """
    __tablename__ = 'responses'
    id = Column(Integer, primary_key=True)
    category = Column(String(32), nullable=False)  # e.g., 'command', 'event'
    trigger = Column(String(100), nullable=False)  # e.g., command name or event type
    text = Column(Text, nullable=True)
    gif_url = Column(Text, nullable=True)
    emote = Column(String(100), nullable=True)
    action = Column(String(100), nullable=True)

class SongQueue(Base):
    """
    Model for storing the music queue and playback for each guild.
    """
    __tablename__ = 'song_queue'
    id = Column(Integer, primary_key=True)
    guild_id = Column(String(32), nullable=False)
    user_id = Column(String(32), nullable=False)
    title = Column(String(255), nullable=False)
    url = Column(String(512), nullable=False)
    file_path = Column(String(512), nullable=True)  # Path to downloaded audio file
    added_at = Column(Integer, nullable=False)  # Unix timestamp