#!/usr/bin/env bash
# Script to start Rudebot with environment validation and error handling
set -e  # Exit on any error

cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Rudebot is already running
if pgrep -f "python.*main.py" > /dev/null; then
    print_error "Rudebot is already running."
    exit 1
fi

# Validate environment file exists
if [ ! -f ".env" ]; then
    print_error "Environment file (.env) not found!"
    print_warning "Please copy env.template to .env and add your Discord token."
    exit 1
fi

# Check if Discord token is set
if ! grep -q "DISCORD_TOKEN=" .env || grep -q "DISCORD_TOKEN=your_discord_bot_token_here" .env; then
    print_error "Discord token not configured in .env file!"
    print_warning "Please add your Discord bot token to the .env file."
    exit 1
fi

print_status "Starting Rudebot..."

# Run setup script to ensure environment is ready
./setup.sh

# Activate virtual environment
source .venv/bin/activate

# Create logs directory if it doesn't exist
mkdir -p logs

# Update the database from JSON if needed
if [ -f data/scripts/import_bot_data.py ]; then
    print_status "Updating database from bot_data.json..."
    python data/scripts/import_bot_data.py
fi

print_status "Starting Rudebot bot..."
exec python main.py 