#!/usr/bin/env bash
# Script to gracefully stop Rudebot with fallback to force kill

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

# Find Rudebot processes
pids=$(pgrep -f "python.*main.py")

if [ -z "$pids" ]; then
    print_warning "Rudebot is not running."
    exit 0
fi

print_status "Found Rudebot processes: $pids"

# Try graceful shutdown first
print_status "Attempting graceful shutdown..."
for pid in $pids; do
    kill -TERM "$pid" 2>/dev/null || true
done

# Wait a bit for graceful shutdown
sleep 3

# Check if processes are still running
remaining_pids=$(pgrep -f "python.*main.py")

if [ -n "$remaining_pids" ]; then
    print_warning "Graceful shutdown failed. Force killing processes: $remaining_pids"
    for pid in $remaining_pids; do
        kill -KILL "$pid" 2>/dev/null || true
    done
    sleep 1
fi

# Final check
if pgrep -f "python.*main.py" > /dev/null; then
    print_error "Failed to stop Rudebot completely."
    exit 1
else
    print_status "Rudebot stopped successfully."
fi 