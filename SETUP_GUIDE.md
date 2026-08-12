# 🚀 Complete Setup Guide

This guide will walk you through setting up the Media Link Bot step-by-step.

---

## 📋 Pre-requisites

Before you begin, make sure you have:

- [ ] **Python 3.8 or higher** installed
- [ ] **Telegram account** 
- [ ] Access to a Linux VPS or local machine
- [ ] **Administrator access** to your VPS (for production deployment)

### Check Python Version

```bash
python3 --version
# Should output: Python 3.8.x or higher
```

---

## 🎯 Part 1: Get Your Telegram Credentials

### Step 1.1: Get Bot Token from BotFather

1. Open Telegram and search for **@BotFather**
2. Send command: `/newbot`
3. BotFather will ask:
   - "What should your bot be called?" → Enter bot name (e.g., "Media Link Bot")
   - "Give your bot a username." → Enter username (e.g., "my_media_link_bot")
4. BotFather sends you the token:
   ```
   Done! Congratulations on your new bot. 
   You will find it at https://t.me/your_bot_username
   Use this token to access the HTTP API:
   123456789:ABCDEfghijklmnopqrstuvwxyz1234567890
   ```
5. **Save this token!** You'll need it in the next step.

### Step 1.2: Get Your User ID

1. Open Telegram and search for **@userinfobot**
2. Send any message to it
3. The bot replies with your information:
   ```
   Id: 987654321
   First name: YourName
   Username: @yourusername
   ```
4. **Save your ID!** (the number after "Id:")

---

## 💾 Part 2: Download and Setup Bot Files

### Step 2.1: Download the Bot

**Option A: Using Git (Recommended)**

```bash
git clone https://github.com/yourusername/media-bot.git
cd media-bot
```

**Option B: Manual Download**

1. Download all bot files
2. Extract to a folder (e.g., `~/media-bot`)
3. Open terminal and navigate:
   ```bash
   cd ~/media-bot
   ```

### Step 2.2: Create Environment File

```bash
cp .env.example .env
```

Now edit the `.env` file with your credentials:

```bash
nano .env
```

Fill in these values:

```env
BOT_TOKEN=123456789:ABCDEfghijklmnopqrstuvwxyz1234567890
ADMIN_ID=987654321
DATABASE_PATH=./data/media_bot.db
LOG_LEVEL=INFO
LOG_FILE=./logs/bot.log
```

**Replace with YOUR values:**
- `BOT_TOKEN` - From BotFather
- `ADMIN_ID` - Your User ID from @userinfobot
- Leave other values as-is

Press `Ctrl+X`, then `Y`, then `Enter` to save.

### Step 2.3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Wait for installation to complete. You should see:
```
Successfully installed python-telegram-bot aiohttp requests python-dotenv
```

### Step 2.4: Create Required Directories

```bash
mkdir -p data logs
```

This creates folders for:
- `data/` - SQLite database
- `logs/` - Bot activity logs

---

## ✅ Part 3: Test the Bot Locally

### Step 3.1: Start the Bot

```bash
python bot.py
```

You should see:
```
==================================================
🤖 Media Link Bot
==================================================
Bot Token: 123456789:ABC***
Admin ID: 987654321
Database: ./data/media_bot.db
FSub Channel: Not configured
==================================================

INFO:bot:Starting Media Link Bot...
INFO:bot:Database initialized successfully
Bot is running. Press Ctrl+C to stop.
```

### Step 3.2: Test on Telegram

1. Go to your bot on Telegram (find it in your chats or search)
2. Send `/start`
3. You should get a welcome message
4. Try `/help` to see all commands

**If you see messages, congratulations! The bot works! ✅**

### Step 3.3: Stop the Bot

Press `Ctrl+C` in terminal to stop the bot.

---

## 🔐 Part 4: (Optional) Setup Force Subscribe

Force Subscribe requires users to join a channel before using the bot.

### Step 4.1: Create or Select a Channel

You need a Telegram channel. Options:
- Create a new channel: Open Telegram → Menu → "New Channel"
- Use an existing channel

**Important:** Make sure the bot is **admin** in the channel!

### Step 4.2: Get Channel ID

1. Forward any message from your channel to **@userinfobot**
2. It replies with the channel ID (starts with -100)
3. Note: If you can't see ID, create a bot message in the channel:
   - Send a message to the channel
   - Forward it to @BotFather
   - It shows the channel ID

### Step 4.3: Configure FSub

1. Start the bot again:
   ```bash
   python bot.py
   ```

2. On Telegram, send to your bot:
   ```
   /configure_fsub
   ```

3. Bot asks you to forward a message from the FSub channel

4. Forward ANY message from your channel to the bot

5. Bot confirms:
   ```
   ✅ FSub Channel Configured!
   Channel ID: -100123456789
   Channel Username: @yourchannel
   ```

### Step 4.4: Verify Bot is Admin

Send `/verify_bot` to your bot. Check the output says "Bot Admin Status: ✅ Yes"

---

## 🚀 Part 5: Deploy to VPS (Production)

### Step 5.1: SSH into Your VPS

```bash
ssh root@your_vps_ip_address
```

### Step 5.2: Download and Setup Bot

```bash
# Install Python
sudo apt update
sudo apt install python3 python3-pip git

# Download bot
git clone https://github.com/yourusername/media-bot.git
cd media-bot

# Install dependencies
pip3 install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env
# Add your credentials (BOT_TOKEN, ADMIN_ID)
```

### Step 5.3: Create Systemd Service (Auto-Start)

```bash
sudo nano /etc/systemd/system/media-bot.service
```

Paste this content:

```ini
[Unit]
Description=Telegram Media Link Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/media-bot
ExecStart=/usr/bin/python3 /root/media-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Press `Ctrl+X`, `Y`, `Enter` to save.

### Step 5.4: Enable and Start Bot

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start
sudo systemctl enable media-bot

# Start bot
sudo systemctl start media-bot

# Check status
sudo systemctl status media-bot
```

You should see: `Active: active (running)`

### Step 5.5: View Logs

```bash
# Real-time logs
sudo journalctl -u media-bot -f

# Stop log view: Ctrl+C
```

### Step 5.6: Useful VPS Commands

```bash
# Stop bot
sudo systemctl stop media-bot

# Restart bot
sudo systemctl restart media-bot

# View last 50 lines of bot log
sudo journalctl -u media-bot -n 50

# See bot startup status
sudo systemctl status media-bot
```

---

## 🧪 Part 6: Test All Features

### Test 1: Basic Commands

Send these to your bot:
```
/start        # Should show welcome
/help         # Should list commands
/about        # Should show info
/stats        # Should show statistics
```

### Test 2: Search (Admin Only)

As admin:
```
/search test
```

Should show "No results found" (since we haven't saved anything yet).

### Test 3: Save Media (Admin Only)

1. Create a test message:
   ```
   Test Movie Title [1.5 GB]
   https://example.com/link1
   https://example.com/link2
   ```

2. Send this to your bot

3. Bot should respond:
   ```
   ✅ Media Saved Successfully!
   File Name: Test Movie Title
   File Size: 1.5 GB
   URLs Found: 2
   ```

### Test 4: Search Works

Send:
```
/search Test Movie
```

Should now show the entry you just saved.

### Test 5: Force Subscribe (if configured)

1. Ask a friend to message your bot
2. Send `/search something`
3. Bot should ask to join channel
4. After joining and verifying, bot allows access

---

## 🆘 Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'telegram'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue 2: "ValueError: BOT_TOKEN not found"

**Solution:**
1. Check `.env` file exists: `ls .env`
2. Edit it: `nano .env`
3. Make sure BOT_TOKEN line doesn't have `#` at start
4. No spaces around `=`

### Issue 3: "ADMIN_ID must be set"

**Solution:**
1. Get your ID from @userinfobot
2. Add to `.env`: `ADMIN_ID=123456789` (your actual ID)

### Issue 4: Bot works locally but not on VPS

**Solution:**
```bash
# Check internet
ping google.com

# Check Python version
python3 --version

# Reinstall dependencies
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Check systemd service
sudo systemctl status media-bot
sudo journalctl -u media-bot -n 20
```

### Issue 5: Database errors

**Solution:**
```bash
# Delete old database
rm data/media_bot.db

# Restart bot
python bot.py
# or
sudo systemctl restart media-bot
```

---

## 📝 Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Bot token obtained from BotFather
- [ ] User ID obtained from @userinfobot
- [ ] `.env` file created with credentials
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Directories created: `mkdir -p data logs`
- [ ] Bot starts without errors: `python bot.py`
- [ ] `/start` command works on Telegram
- [ ] Admin can forward messages and save media
- [ ] Search functionality works
- [ ] (Optional) FSub configured and working
- [ ] (Optional) Bot running on VPS via systemd

---

## ✨ Next Steps

1. ✅ Complete this setup guide
2. ✅ Test all commands from Part 6
3. ✅ Configure FSub (optional, Part 4)
4. ✅ Deploy to VPS (optional, Part 5)
5. ✅ Read `COMMANDS.md` for full command reference
6. ✅ Invite users and start distributing links!

---

## 📞 Need Help?

- **Telegram Bot Issues:** Ask in Telegram bot
- **Setup Issues:** Check logs: `logs/bot.log`
- **Contact:** [@Franited](https://t.me/Franited)

---

**You're all set! Happy distributing! 🚀**
