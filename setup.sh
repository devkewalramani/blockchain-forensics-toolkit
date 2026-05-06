#!/bin/bash

# Blockchain Forensics Toolkit - Quick Setup Script

echo "=================================="
echo "Blockchain Forensics Toolkit Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✓ Python $PYTHON_VERSION found"
else
    echo "✗ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt --break-system-packages

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "⚠ Some dependencies may have failed to install"
    echo "  Try: pip3 install requests pandas"
fi

# Create output directories
echo ""
echo "Creating output directories..."
mkdir -p reports balance_reports cache
echo "✓ Directories created"

# Check for API key
echo ""
echo "API Key Setup:"
echo "You will need an Etherscan API key to use this toolkit."
echo "Get a free key at: https://etherscan.io/apis"
echo ""
echo "You can either:"
echo "  1. Set environment variable: export ETHERSCAN_API_KEY='your_key'"
echo "  2. Enter it when prompted by the scripts"
echo ""

read -p "Do you have an Etherscan API key? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your API key (it will not be saved): " API_KEY
    echo ""
    echo "Testing API key..."
    
    # Simple test
    RESPONSE=$(curl -s "https://api.etherscan.io/v2/api?chainid=1&module=account&action=balance&address=0x742d35cc6634c0532925a3b844bc9e7595f0beb1&tag=latest&apikey=$API_KEY")
    
    if [[ $RESPONSE == *"\"status\":\"1\""* ]]; then
        echo "✓ API key is valid!"
        echo ""
        echo "To save it for future use, add to your ~/.bashrc or ~/.zshrc:"
        echo "  export ETHERSCAN_API_KEY='$API_KEY'"
    else
        echo "✗ API key appears invalid. Please check it."
    fi
else
    echo "Please obtain an API key before using the toolkit."
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Quick start options:"
echo "  1. Simple launcher:  python3 tools/run_forensics.py"
echo "  2. Basic analysis:   python3 core/goliath_forensics.py"
echo "  3. Balance check:    python3 tools/check_all_balances_improved.py"
echo ""
echo "See USAGE_GUIDE.md for detailed examples and workflows."
echo ""
