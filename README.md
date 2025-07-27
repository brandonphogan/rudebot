# Rudebot

Rudebot is a big meany Discord bot with sarcastic responses and music playback capabilities. Built with a clean architecture that separates business logic from Discord-specific code.

## Features

- **Sarcastic Commands**: Rude responses to `!hello`, `!joke`, and other commands
- **Music System**: Full DJ functionality with queue management and audio streaming
- **Event Responses**: Automatic greetings when users join voice channels
- **Interactive Console**: Real-time bot management with console commands
- **Hot Reloading**: Reload cogs without restarting the bot
- **Clean Architecture**: Services layer separated from Discord handlers
- **Database Management**: SQLite database with JSON import/export

## Quick Start

1. **Setup Environment**:
   ```bash
   cp env.template .env
   # Edit .env with your Discord token and server details
   ```

2. **Start the Bot**:
   ```bash
   ./scripts/start.sh
   ```

## Management Scripts

- `./scripts/start.sh` - Start Rudebot with console interface
- `./scripts/stop.sh` - Gracefully stop Rudebot (detects console mode)
- `./scripts/restart.sh` - Restart Rudebot cleanly
- `./scripts/status.sh` - Check Rudebot status and health
- `./scripts/setup.sh` - Set up environment (called automatically)

## Console Interface

When running, the bot provides an interactive console for real-time management:

```bash
# Console commands (type directly while bot is running):
help                # Show all available commands
stop                # Gracefully stop the bot
restart             # Restart the bot (creates restart flag)
status              # Show bot statistics (latency, guilds, users)
guilds              # List connected Discord servers
cogs                # List all loaded cogs
reload <cog>        # Hot-reload a specific cog

# Examples:
reload commands     # Reload the commands cog
reload music        # Reload the music cog
reload events       # Reload the events cog
```

**Benefits**: No need to restart the bot for most changes - just reload the affected cog!

## Project Structure

```
rudebot/
├── cogs/              # Discord bot cogs (clean, simple names)
│   ├── commands.py    # Text commands (!help, !hello, !joke)
│   ├── events.py      # Discord events (voice join greetings)
│   └── music.py       # Music queue and playback
├── services/          # Business logic (Discord-agnostic)
│   ├── response_service.py   # Response handling and DB queries
│   ├── action_service.py     # Bot actions (kick, scatter)
│   ├── music_service.py      # Queue management, audio download
│   ├── channel_service.py    # Channel utilities
│   └── console_service.py    # Interactive console interface
├── data/              # Database, scripts, and bot data
│   ├── scripts/       # Database management scripts
│   ├── models.py      # SQLAlchemy ORM models
│   ├── session.py     # Database session management
│   └── dj_audio/      # Downloaded music files
├── scripts/           # Management scripts (start, stop, etc.)
├── utils/             # Utility modules (logging, paths)
├── logs/              # Log files (separate for each component)
└── .venv/             # Python virtual environment
```

## Architecture Benefits

- **Clean Separation**: Business logic in `services/`, Discord handling in `cogs/`
- **Testable**: Services can be unit tested without Discord mocking
- **Reusable**: Services could work with other interfaces (web, CLI)
- **Maintainable**: Changes to business logic don't affect Discord protocols
- **Hot Reloadable**: Cogs can be reloaded individually during development

## Development Workflow

### Making Changes:
1. **Edit code** in `services/` or `cogs/`
2. **Hot reload** with console: `reload <cog_name>`
3. **Test changes** immediately without full restart
4. **Use console commands** for real-time debugging and management

### Adding New Features:
1. **Business logic** goes in `services/`
2. **Discord interface** goes in `cogs/`
3. **Import services** in cogs to use business logic
4. **Test with hot reload** during development

## Desktop Shortcut

A desktop shortcut (`rudebot.desktop`) is available for easy startup from your desktop environment.
