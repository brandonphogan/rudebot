# Rudebot

Rudebot is a big meany Discord bot with sarcastic responses and music playback capabilities.

## Features

- **Sarcastic Commands**: Rude responses to `!hello`, `!joke`, and other commands
- **Music System**: Full DJ functionality with queue management
- **Event Responses**: Automatic greetings when users join voice channels
- **Database Management**: SQLite database with JSON import/export

## Quick Start

1. **Setup Environment**:
   ```bash
   cp env.template .env
   # Edit .env with your Discord token and server details
   ```

2. **Start the Bot**:
   ```bash
   ./start.sh
   ```

## Management Scripts

- `./start.sh` - Start Rudebot with full validation
- `./stop.sh` - Gracefully stop Rudebot
- `./restart.sh` - Restart Rudebot cleanly
- `./status.sh` - Check Rudebot status and health
- `./setup.sh` - Set up environment (called automatically)

## Project Structure

```
rudebot/
├── cogs/              # Discord bot command handlers
├── data/              # Database, scripts, and bot data
│   ├── scripts/       # Database management scripts
│   └── dj_audio/      # Music files
├── utils/             # Utility modules
├── logs/              # Log files
└── .venv/             # Python virtual environment
```

## Desktop Shortcut

A desktop shortcut is available for easy startup from your desktop.
