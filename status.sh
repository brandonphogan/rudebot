#!/usr/bin/env bash
# Script to check Rudebot status, process details, and system health

cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}[STATUS]${NC} $1"
}

# Check if Rudebot is running
pids=$(pgrep -f "python.*main.py")

if [ -z "$pids" ]; then
    print_error "Rudebot is not running."
    exit 1
fi

print_header "Rudebot Status"
print_status "Rudebot is running with PID(s): $pids"

# Show process details
echo
print_header "Process Details:"
for pid in $pids; do
    echo "  PID: $pid"
    echo "  Command: $(ps -p "$pid" -o cmd=)"
    echo "  Started: $(ps -p "$pid" -o lstart=)"
    echo "  Memory: $(ps -p "$pid" -o rss= | awk '{print $1/1024 " MB"}')"
    echo "  CPU: $(ps -p "$pid" -o %cpu=)%"
    echo
done

# Check log files
echo
print_header "Recent Log Activity:"
if [ -f "logs/rudebot.log" ]; then
    echo "  Main log (last 5 lines):"
    tail -5 logs/rudebot.log | sed 's/^/    /'
else
    print_warning "  No main log file found"
fi

# Check database
echo
print_header "Database Status:"
if [ -f "data/rudebot.sqlite3" ]; then
    db_size=$(du -h data/rudebot.sqlite3 | cut -f1)
    print_status "Database exists (size: $db_size)"
else
    print_error "Database not found"
fi

# Check environment
echo
print_header "Environment Status:"
if [ -f ".env" ]; then
    print_status "Environment file exists"
    if grep -q "DISCORD_TOKEN=" .env && ! grep -q "DISCORD_TOKEN=your_discord_bot_token_here" .env; then
        print_status "Discord token configured"
    else
        print_warning "Discord token not configured"
    fi
else
    print_error "Environment file missing"
fi

if [ -d ".venv" ]; then
    print_status "Virtual environment exists"
else
    print_error "Virtual environment missing"
fi 