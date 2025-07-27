#!/usr/bin/env bash
# Smart stop script that uses console interface when available, falls back to force kill
set -e

cd "$(dirname "$0")/.."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if bot is running
BOT_PID=""
if [ -f ".bot_pid" ]; then
    BOT_PID=$(cat .bot_pid)
    if ! kill -0 "$BOT_PID" 2>/dev/null; then
        print_warning "PID file exists but process not running, cleaning up..."
        rm -f .bot_pid
        BOT_PID=""
    fi
fi

# If no PID file, try to find the process
if [ -z "$BOT_PID" ]; then
    BOT_PID=$(pgrep -f "python.*main.py" || true)
fi

if [ -z "$BOT_PID" ]; then
    print_warning "Rudebot is not running."
    # Clean up any leftover files
    rm -f .bot_pid .restart_requested .console_running
    exit 0
fi

print_status "Stopping Rudebot (PID: $BOT_PID)..."

# Console interface should handle graceful shutdown automatically
# Just send SIGTERM and let the console service handle cleanup
print_status "Sending graceful shutdown signal..."
kill -TERM "$BOT_PID" 2>/dev/null || true

# Wait for graceful shutdown
sleep 3

# Check if still running
if kill -0 "$BOT_PID" 2>/dev/null; then
    print_warning "Graceful shutdown taking longer, waiting..."
    sleep 2
    
    if kill -0 "$BOT_PID" 2>/dev/null; then
        print_warning "Process still running, using SIGKILL..."
        kill -KILL "$BOT_PID" 2>/dev/null || true
        sleep 1
    fi
fi

# Clean up tracking files
rm -f .bot_pid .restart_requested .console_running

print_status "Rudebot stopped successfully." 