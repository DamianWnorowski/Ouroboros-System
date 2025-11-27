#!/bin/bash
# Test runner script

set -e

echo "🧪 Running Ouroboros System Tests..."

# Run with coverage
pytest tests/ \
    -v \
    --cov=core \
    --cov=agents \
    --cov-report=term-missing \
    --cov-report=html \
    "$@"

echo "✅ Tests complete!"
echo "📊 Coverage report: htmlcov/index.html"

