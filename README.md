# 📱 Telegram Media Link Bot

A production-ready Telegram bot for managing and distributing media/file links with Force Subscribe (FSub) support.

**Bot Made by:** @Franited  
**Powered by:** @Dokjaxvibe

---

## ✨ Features

### 📥 Core Features
- **Forward Message Handling** - Accept and process forwarded messages from source channels
- **Media Link Management** - Save file names, sizes, captions, and URLs
- **Smart URL Parsing** - Automatically extract URLs and metadata from messages
- **Link Distribution** - Provide links via text messages and clickable buttons
- **Full Search** - Search saved media by file name and caption
- **Activity Tracking** - Track user interactions and bot usage
- **Statistics** - View detailed analytics about saved media and users

### 🔐 Security Features
- **Force Subscribe (FSub)** - Require users to join a channel before accessing links
- **Admin-Only Commands** - Restrict sensitive operations to authorized users
- **Secure Configuration** - All sensitive data stored in `.env` file (not in code)
- **Activity Logging** - Comprehensive logs for auditing and debugging
- **Input Validation** - Sanitize and validate all user inputs

### ⚙️ Admin Features
- **FSub Configuration** - Setup Force Subscribe with a single command
- **Channel Verification** - Verify bot has admin permissions in channels
- **Statistics Dashboard** - View real-time statistics
- **Configuration Management** - Change settings through bot commands
- **Activity Monitoring** - Track user behavior and bot performance

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** installed
- **Telegram Account** and a bot token from [@BotFather](https://t.me/BotFather)
- **Linux VPS** or local machine to run the bot

### Step 1: Clone/Download the Bot

```bash
git clone https://github.com/yourusername/media-bot.git
cd media-bot
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Get Your Credentials

#### 1. **Telegram Bot Token**
- Open [@BotFather](https://t.me/BotFather) on Telegram
- Send `/newbot`
- Follow the instructions to create a new bot
- Copy the bot token

#### 2. **Your User ID**
- Open [@userinfobot](https://t.me/userinfobot) on Telegram
- Send any message
- Copy your User ID

### Step 4: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file:

```bash
nano .env
```

Fill in your credentials:

```
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_ID=your_user_id_from_userinfobot
DATABASE_PATH=./data/media_bot.db
LOG_LEVEL=INFO
LOG_FILE=./logs/bot.log
```

**Optional - For Force Subscribe:**
```
FSUB_CHANNEL_ID=-100your_channel_id_here
```

### Step 5: Create Required Directories

```bash
mkdir -p data logs
```

### Step 6: Run the Bot

```bash
python bot.py
```

You should see:
```
==================================================
🤖 Media Link Bot
==================================================
Bot Token: ****...
Admin ID: 123456789
Database: ./data/media_bot.db
FSub Channel: Not configured
==================================================
```

**Success!** The bot is now running. Send `/start` to the bot on Telegram to test it.

---

## 📋 Commands

### General Commands (Everyone)

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and quick start guide |
| `/help` | Show all available commands |
| `/about` | Bot information and credits |
| `/stats` | View basic statistics |
| `/search <query>` | Search saved media by name |
| `/latest` | View 10 most recent media entries |

### Admin Commands (Admin Only)

| Command | Description |
|---------|-------------|
| `/admin` | Open admin control panel |
| `/configure_fsub` | Setup Force Subscribe channel |
| `/verify_bot` | Check bot status and permissions |
| `/stats_detailed` | View detailed analytics |
| `/clear_fsub` | Remove FSub configuration |

---

## 🔧 Setup Guide

### How to Use (Users)

1. **Search for Media**
   ```
   /search movie_name
   ```
   
2. **View Latest Entries**
   ```
   /latest
   ```

3. **Force Subscribe (if enabled)**
   - Bot will ask you to join the channel
   - Click "Join Channel" button
   - Click "Check Subscription" button
   - Then access the links

### How to Use (Admin)

#### Step 1: Setup Force Subscribe (Optional)

```
/configure_fsub
```

Then forward any message from the channel you want to set as FSub. The bot will detect it automatically.

#### Step 2: Save Media Entries

Forward messages containing file links to the bot. Format:

```
Example Movie 2024 [1.5 GB]
https://example.com/file1
https://example.com/file2
```

The bot will automatically extract:
- File name: "Example Movie 2024"
- File size: "1.5 GB"
- URLs: Both links

#### Step 3: Users Can Search

Users can now search for saved media:
```
/search Example Movie
```

---

## 📁 Project Structure

```
media-bot/
├── bot.py                 # Main bot application
├── database.py            # SQLite database handler
├── url_parser.py          # URL and metadata extraction
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .env                   # Your actual credentials (DO NOT SHARE)
├── README.md              # This file
├── data/
│   └── media_bot.db       # SQLite database (auto-created)
└── logs/
    └── bot.log            # Bot activity logs (auto-created)
```

---

## 🗄️ Database Schema

### media_entries
Stores all saved media entries

```sql
- id (PRIMARY KEY)
- message_id (UNIQUE)
- channel_id
- file_name
- file_size
- caption
- urls (JSON)
- created_at
- updated_at
```

### fsub_config
Force Subscribe channel configuration

```sql
- channel_id
- channel_username
- added_at
```

### user_subscriptions
Track verified subscribers

```sql
- user_id
- channel_id
- verified_at
```

### activity_logs
Track all user interactions

```sql
- user_id
- action
- details
- timestamp
```

### bot_stats
Store statistics snapshots

```sql
- total_media_entries
- total_users
- total_requests
- last_updated
```

---

## 🔐 Security Best Practices

### ✅ DO:
- ✅ Keep `.env` file **private** and **never** commit it to git
- ✅ Use strong, unique bot tokens
- ✅ Regularly update dependencies: `pip install -r requirements.txt --upgrade`
- ✅ Review logs regularly for suspicious activity
- ✅ Use HTTPS for all external URLs
- ✅ Validate all user inputs
- ✅ Run the bot on a dedicated VPS

### ❌ DON'T:
- ❌ Share your `.env` file with anyone
- ❌ Hardcode credentials in source code
- ❌ Commit `.env` to version control
- ❌ Expose log files publicly
- ❌ Use weak or shared bot tokens
- ❌ Run the bot with unnecessary permissions

---

## 🐛 Troubleshooting

### Bot is not responding

**Solution:**
1. Check if bot token is correct in `.env`
2. Verify internet connection
3. Check logs: `tail -f logs/bot.log`

### "Invalid bot token" error

**Solution:**
1. Get a new token from [@BotFather](https://t.me/BotFather)
2. Update `.env` file with new token
3. Restart the bot

### Database errors

**Solution:**
1. Ensure `data/` directory exists
2. Check file permissions: `chmod 755 data/`
3. Delete old database and restart: `rm data/media_bot.db`

### FSub not working

**Solution:**
1. Make sure bot is admin in the channel
2. Verify channel ID is correct (should start with `-100`)
3. Check bot has "Delete messages" permission
4. Run `/verify_bot` to check status

### Bot is slow

**Solution:**
1. Check database size: `ls -lh data/media_bot.db`
2. Clear old entries if needed
3. Check server resources: `free -h`, `df -h`
4. Consider database cleanup (see `/admin` panel)

---

## 📊 Example Usage

### Step-by-Step Example

**1. Admin forwards a message:**
```
Movie Title [2.5 GB]
https://download.example.com/movie1
https://download.example.com/movie2
```

**2. Bot saves it:**
```
✅ Media Saved Successfully!

File Name: Movie Title
File Size: 2.5 GB
URLs Found: 2
Message ID: 12345
```

**3. User searches:**
```
/search Movie Title
```

**4. User gets results:**
```
🔍 Search Results for: Movie Title

1. Movie Title
   Size: 2.5 GB
```

**5. User clicks link button and gets:**
```
📁 Movie Title
📊 Size: 2.5 GB

🔗 Available Links:
1. https://download.example.com/movie1
2. https://download.example.com/movie2

📝 Description:
[Original caption if provided]

Powered by @Dokjaxvibe
```

---

## 🚀 Deployment on VPS

### Using systemd (Recommended)

**1. Create service file:**
```bash
sudo nano /etc/systemd/system/media-bot.service
```

**2. Add content:**
```ini
[Unit]
Description=Telegram Media Link Bot
After=network.target

[Service]
Type=simple
User=debian
WorkingDirectory=/home/debian/media-bot
ExecStart=/usr/bin/python3 /home/debian/media-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**3. Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable media-bot
sudo systemctl start media-bot
```

**4. Check status:**
```bash
sudo systemctl status media-bot
```

**5. View logs:**
```bash
sudo journalctl -u media-bot -f
```

---

## 📞 Support & Credits

- **Bot Made by:** [@Franited](https://t.me/Franited)
- **Powered by:** [@Dokjaxvibe](https://t.me/Dokjaxvibe)
- **Framework:** [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- **Database:** SQLite3

---

## 📜 License

This project is provided as-is for personal and commercial use.

---

## 🔄 Updates & Maintenance

### Regular Maintenance Tasks

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Backup database
cp data/media_bot.db data/media_bot.db.backup

# Check bot logs
tail -n 100 logs/bot.log

# Restart bot (if using systemd)
sudo systemctl restart media-bot
```

---

## 🎯 Next Steps

1. ✅ Complete the setup above
2. ✅ Test the bot with `/start`
3. ✅ Configure FSub (optional)
4. ✅ Save some test media entries
5. ✅ Test search functionality
6. ✅ Deploy to VPS (optional)

---

**Thank you for using Media Link Bot!** 🚀

For issues or questions, contact [@Franited](https://t.me/Franited) on Telegram.
