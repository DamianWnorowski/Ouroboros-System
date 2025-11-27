#!/bin/bash
# Ouroboros System - Onboarding Script
# Complete setup for new developers

set -e

echo "🐍 Ouroboros System - Onboarding"
echo "================================"
echo ""

# Check Python
echo "1. Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi
python3 --version
echo "✅ Python OK"
echo ""

# Create venv
echo "2. Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi
source venv/bin/activate
echo ""

# Install dependencies
echo "3. Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Dependencies installed"
echo ""

# Run verification
echo "4. Running system verification..."
python -m core.verification.cli --level 3 --quiet || echo "⚠️  Some checks failed (non-critical)"
echo ""

# Run tests
echo "5. Running tests..."
pytest tests/unit/ -v --tb=short || echo "⚠️  Some tests failed"
echo ""

# Create .env if needed
echo "6. Environment setup..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "   Create .env file with required variables"
    echo "   See README_ENV_SETUP.md for guidance"
else
    echo "✅ .env file exists"
fi
echo ""

# Summary
echo "================================"
echo "✅ Onboarding complete!"
echo ""
echo "Next steps:"
echo "  1. Create .env file (see README_ENV_SETUP.md)"
echo "  2. Run: make chain-all"
echo "  3. Start: make start"
echo "  4. Read: QUICK_START_GUIDE.md"
echo ""

