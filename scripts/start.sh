#!/bin/bash
# Ouroboros System - Startup Script

set -e

echo "🐍 Starting Ouroboros System..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run verification
echo "Running system verification..."
python -m core.verification.cli --level 3 --quiet || echo "⚠️  Some verification checks failed"

# Start orchestrator
echo "Starting orchestrator..."
python -m core.orchestrator

