#!/usr/bin/env bash
set -e

if [ -f ".env" ]; then
  echo ".env already exists. Not overwriting."
else
  cat > .env <<EOL
DISCORD_TOKEN=your_token_here
GUILD_ID=your_guild_id_here
TEXT_CHANNEL_ID=your_text_channel_id_here
EOL
  echo "Created .env with placeholder values. Please edit .env to add your secrets."
fi 