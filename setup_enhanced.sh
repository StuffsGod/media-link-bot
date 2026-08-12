#!/bin/bash

# Enhanced Media Link Bot - Setup Script
# Run: bash setup_enhanced.sh

echo "╔════════════════════════════════════════╗"
echo "║  Enhanced Media Link Bot Setup         ║"
echo "║  Version: 2.0.0                        ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create directories
echo "📁 Creating directories..."
mkdir -p data logs backups

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env file with your configuration:"
    echo "   - BOT_TOKEN: Get from @BotFather"
    echo "   - ADMIN_ID: Get from @userinfobot"
    echo "   - SCRAPE_SITE_URL: Website to scrape"
    echo "   - SCRAPE_CHANNEL_ID: Channel for exports"
    echo ""
else
    echo "✅ .env file already configured"
fi

echo ""
echo "╔════════════════════════════════════════╗"
echo "║  Setup Complete! 🎉                    ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run: python3 enhanced_bot.py"
echo "3. Test in Telegram: /start"
echo ""
echo "📚 Documentation: ENHANCED_FEATURES.md"
echo ""
