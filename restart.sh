#!/usr/bin/env bash
# Script to restart Rudebot with clean stop/start cycle

cd "$(dirname "$0")"

# Colors for output
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

print_status "Restarting Rudebot..."

# Stop Rudebot if it's running
if [ -f "stop.sh" ]; then
    print_status "Stopping Rudebot..."
    ./stop.sh
    sleep 2
else
    print_warning "Stop script not found, attempting to kill processes..."
    pkill -f "python.*main.py" || true
    sleep 2
fi

# Start Rudebot
print_status "Starting Rudebot..."
./start.sh 