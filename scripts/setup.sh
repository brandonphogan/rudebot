#!/usr/bin/env bash
# Script to set up the virtual environment, dependencies, and directories for Rudebot
set -e  # Exit on any error

cd "$(dirname "$0")/.."

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

print_status "Setting up Rudebot environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_warning "Python $python_version detected. Python 3.8+ is recommended."
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_status "Virtual environment not found. Creating..."
    python3 -m venv .venv
    print_status "Virtual environment created."
else
    print_status "Virtual environment already exists."
fi

# Activate virtual environment and install dependencies
print_status "Installing dependencies..."
source .venv/bin/activate

# Upgrade pip first
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p data/dj_audio

# Initialize database if it doesn't exist
if [ ! -f "data/rudebot.sqlite3" ]; then
    print_status "Initializing database..."
    python data/init_db.py
    print_status "Database initialized."
else
    print_status "Database already exists."
fi

print_status "Setup complete!" 