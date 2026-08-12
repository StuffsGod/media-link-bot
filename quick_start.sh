#!/bin/bash

# ==========================================
# Media Link Bot - Quick Start Script
# ==========================================
# This script helps you setup the bot quickly

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==========================================
# Functions
# ==========================================

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ==========================================
# Checks
# ==========================================

print_header "Media Link Bot - Quick Start Setup"

print_info "Checking prerequisites..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed!"
    echo "Install Python3 first: sudo apt install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_success "Python $PYTHON_VERSION found"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found!"
    echo "Make sure you're in the media-bot directory"
    exit 1
fi

# ==========================================
# Setup Steps
# ==========================================

print_header "Step 1: Install Dependencies"

if python3 -m pip install -r requirements.txt; then
    print_success "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# ==========================================

print_header "Step 2: Setup Environment Variables"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env file created from template"
        print_warning "⚠️  Important: Edit .env and add your credentials"
    else
        print_error ".env.example not found!"
        exit 1
    fi
else
    print_info ".env file already exists"
fi

# Check if .env has required values
if grep -q "BOT_TOKEN=your_bot_token_here" .env; then
    print_warning "BOT_TOKEN not configured in .env"
    echo "Please edit .env and set BOT_TOKEN"
    read -p "Open .env now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v nano &> /dev/null; then
            nano .env
        elif command -v vi &> /dev/null; then
            vi .env
        else
            print_error "No text editor found. Edit .env manually"
        fi
    fi
fi

if grep -q "ADMIN_ID=your_user_id_here" .env; then
    print_warning "ADMIN_ID not configured in .env"
    echo "Please edit .env and set ADMIN_ID (your Telegram user ID)"
fi

# ==========================================

print_header "Step 3: Create Required Directories"

mkdir -p data logs
chmod 755 data logs
print_success "Directories created (data/, logs/)"

# ==========================================

print_header "Step 4: Verify Configuration"

if [ -f ".env" ]; then
    BOT_TOKEN=$(grep "^BOT_TOKEN=" .env | cut -d '=' -f2)
    ADMIN_ID=$(grep "^ADMIN_ID=" .env | cut -d '=' -f2)
    
    if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_bot_token_here" ]; then
        print_error "BOT_TOKEN is not set properly"
    else
        TOKEN_MASKED="${BOT_TOKEN:0:10}***"
        print_success "BOT_TOKEN configured: $TOKEN_MASKED"
    fi
    
    if [ -z "$ADMIN_ID" ] || [ "$ADMIN_ID" = "your_user_id_here" ]; then
        print_error "ADMIN_ID is not set properly"
    else
        print_success "ADMIN_ID configured: $ADMIN_ID"
    fi
else
    print_error ".env file not found"
fi

# ==========================================

print_header "Step 5: Test Bot"

print_info "Ready to start the bot!"
echo
echo "Choose an option:"
echo "  1) Start bot now"
echo "  2) Show setup instructions"
echo "  3) Exit"
echo

read -p "Enter choice (1-3): " choice

case $choice in
    1)
        print_info "Starting bot... (Press Ctrl+C to stop)"
        echo
        python3 bot.py
        ;;
    2)
        echo
        print_header "Setup Instructions"
        echo "1. Get Bot Token:"
        echo "   - Open Telegram and search for @BotFather"
        echo "   - Send /newbot"
        echo "   - Follow the instructions"
        echo "   - Copy the token"
        echo
        echo "2. Get Your User ID:"
        echo "   - Open Telegram and search for @userinfobot"
        echo "   - Send any message"
        echo "   - Copy your ID from the response"
        echo
        echo "3. Edit .env file:"
        echo "   - Edit .env and add BOT_TOKEN and ADMIN_ID"
        echo "   - Save the file"
        echo
        echo "4. Start the bot:"
        echo "   - Run: python3 bot.py"
        echo
        echo "5. Test on Telegram:"
        echo "   - Send /start to your bot"
        echo "   - Try /help command"
        echo
        echo "For more help, see SETUP_GUIDE.md"
        ;;
    3)
        print_info "Exiting..."
        exit 0
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# ==========================================

print_header "Setup Complete!"

print_success "Bot is ready to use"
echo
echo "Next steps:"
echo "  1. Edit .env with your credentials"
echo "  2. Run: python3 bot.py"
echo "  3. Send /start to your bot on Telegram"
echo "  4. Read SETUP_GUIDE.md for detailed instructions"
echo
print_info "For support, contact @Franited on Telegram"
echo
