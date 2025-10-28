#!/bin/bash
# Quick setup script for Bandwidth Monitor

echo "========================================"
echo "Bandwidth Monitor Setup"
echo "========================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed"
    exit 1
fi

echo "✓ pip found"

# Install dependencies
echo ""
echo "Installing dependencies..."
cd led-sign-project
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "Error installing dependencies"
    exit 1
fi

# Make scripts executable
chmod +x bandwidth_monitor.py
chmod +x bandwidth_dashboard.py

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Quick Start Commands:"
echo ""
echo "1. Run a single speed test:"
echo "   python3 bandwidth_monitor.py --once"
echo ""
echo "2. Start continuous monitoring (5 min interval):"
echo "   python3 bandwidth_monitor.py"
echo ""
echo "3. Start web dashboard (in another terminal):"
echo "   python3 bandwidth_dashboard.py"
echo "   Then open: http://localhost:5001"
echo ""
echo "4. View statistics:"
echo "   python3 bandwidth_monitor.py --stats 24"
echo ""
echo "For full documentation, see: BANDWIDTH_MONITOR_README.md"
echo ""
