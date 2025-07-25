#!/usr/bin/env bash
# Script to activate the virtual environment and start Rudebot
cd "$(dirname "$0")"

# Check if Rudebot is already running
if pgrep -f "python.*main.py" > /dev/null; then
  echo "Rudebot is already running."
  exit 1
fi

source .venv/bin/activate

# Update the database from JSON if needed
if [ -f db/import_bot_data.py ]; then
  echo "Updating database from bot_data.json..."
  python db/import_bot_data.py
fi

exec python main.py 