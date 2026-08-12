# 🚀 Quick Start Guide - Enhanced Media Link Bot v2.0

## ✨ What's New

Your bot has been upgraded with these amazing features:

✅ **Auto-Scraping** - Search not found? Bot scrapes website automatically  
✅ **`/scrapeall`** - Scrape entire website with one command (admin only)  
✅ **`/addsudo`** - Add new admin users easily  
✅ **Telegram Export** - Save scraped links to channel as .txt file  
✅ **Admin Panel** - Centralized control dashboard  
✅ **Database Storage** - All scraped links saved to database  

---

## 📦 Files Included

### Essential Files

| File | Purpose |
|------|---------|
| `enhanced_bot.py` | Main bot application (700+ lines) |
| `enhanced_database.py` | Database operations (400+ lines) |
| `requirements.txt` | Python dependencies |
| `.env.example` | Configuration template |
| `setup_enhanced.sh` | Automated setup script |

### Documentation

| File | Content |
|------|---------|
| `ENHANCED_FEATURES.md` | Complete feature guide (600+ lines) |
| `ADMIN_GUIDE.md` | Admin operations manual (500+ lines) |
| `IMPLEMENTATION_SUMMARY.md` | Technical details |
| `QUICKSTART.md` | This file |

---

## ⚡ 3-Minute Setup

### Step 1: Prepare Environment

```bash
# Clone/download all files
# Create directory
mkdir media-bot-enhanced
cd media-bot-enhanced

# Copy all files here
cp enhanced_bot.py .
cp enhanced_database.py .
cp requirements.txt .
cp .env.example .env
cp setup_enhanced.sh .
chmod +x setup_enhanced.sh
```

### Step 2: Run Setup Script

```bash
bash setup_enhanced.sh
```

This will:
- ✅ Check Python 3 installation
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create required directories

### Step 3: Configure Bot

Edit `.env` file:

```bash
nano .env
```

Must set these:
```env
BOT_TOKEN=your_token_from_botfather
ADMIN_ID=your_user_id_from_userinfobot
SCRAPE_SITE_URL=https://your-website.com
SCRAPE_CHANNEL_ID=-100your_channel_id
```

Get IDs:
- **BOT_TOKEN**: From [@BotFather](https://t.me/BotFather) → `/newbot`
- **ADMIN_ID**: From [@userinfobot](https://t.me/userinfobot) → send message
- **SCRAPE_CHANNEL_ID**: From [@userinfobot](https://t.me/userinfobot) → forward channel message

### Step 4: Start Bot

```bash
python3 enhanced_bot.py
```

You'll see:
```
╔═══════════════════════════════════╗
║  Enhanced Media Link Bot           ║
║  With Web Scraping & Admin Panel   ║
╚═══════════════════════════════════╝

Bot is running... (Press Ctrl+C to stop)
```

---

## 🎮 Admin Commands Quick Reference

### For Main Admin Only

```bash
/addsudo 987654321        # Add new admin
/scrapeall               # Scrape entire website
/admin                   # Open admin panel
```

### For All Admins

```bash
/scrapeall               # Scrape website
/admin                   # Admin panel
/stats                   # View statistics
```

### For Users

```bash
/start                   # Welcome message
/search keyword          # Search media (auto-scrapes if not found)
/stats                   # View statistics
/help                    # Show all commands
```

---

## 📊 How It Works

### Search Flow

```
User: /search "Movie"
  ↓
Bot searches database
  ↓
Found? → Return results
  ↓
Not found? → Scrape website
  ↓
Bot scrapes for "Movie"
  ↓
Found? → Return results + save to DB
  ↓
Not found? → Return "No results"
```

### Scrape All Flow

```
Admin: /scrapeall
  ↓
Bot validates admin access
  ↓
Scrapes entire SCRAPE_SITE_URL
  ↓
Extracts all links and media
  ↓
Saves to database
  ↓
Exports to Telegram channel as .txt
  ↓
Shows summary statistics
```

---

## 🔐 Admin Management

### Add New Admin

```bash
/addsudo 123456789
```

Result:
- ✅ User added to database
- ✅ User can now use /scrapeall
- ✅ User can access /admin panel

### Check Admin List

```bash
sqlite3 data/media_bot.db "SELECT admin_id FROM admins;"
```

---

## 🌐 Configuration Tips

### Change Scrape Website

Edit `.env`:
```env
SCRAPE_SITE_URL=https://new-site.com/media
```

Restart bot to apply.

### Increase Scrape Timeout

For slow websites:
```env
SCRAPE_TIMEOUT=60
```

### Change Export Channel

```env
SCRAPE_CHANNEL_ID=-100new_channel_id
```

---

## 🐛 Troubleshooting

### "Bot token invalid"
- Get new token from @BotFather
- Update `.env`
- Restart bot

### "Admin only" error
- Verify you used `/addsudo`
- Check: `sqlite3 data/media_bot.db "SELECT * FROM admins;"`
- Restart bot

### Scraping doesn't work
- Test website is online
- Check SCRAPE_SITE_URL in .env
- View logs: `tail -20 logs/enhanced_bot.log`

### No files exported to channel
- Verify SCRAPE_CHANNEL_ID
- Make bot admin in channel
- Check logs for errors

---

## 📚 Full Documentation

For detailed information:

- **Features** → Read `ENHANCED_FEATURES.md`
- **Admin Operations** → Read `ADMIN_GUIDE.md`
- **Technical Details** → Read `IMPLEMENTATION_SUMMARY.md`

---

## 🚀 Deployment Options

### Option 1: Local Development
```bash
python3 enhanced_bot.py
```
Good for testing. Bot stops when terminal closes.

### Option 2: Background (Linux/Mac)
```bash
nohup python3 enhanced_bot.py > bot.log 2>&1 &
```
Bot continues running in background.

### Option 3: Systemd Service (Recommended)
```bash
sudo nano /etc/systemd/system/media-bot.service
```

Add:
```ini
[Unit]
Description=Enhanced Media Link Bot
After=network.target

[Service]
Type=simple
User=debian
WorkingDirectory=/home/debian/media-bot
ExecStart=/usr/bin/python3 /home/debian/media-bot/enhanced_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable media-bot
sudo systemctl start media-bot
```

### Option 4: Docker (Optional)
Create Dockerfile (see ENHANCED_FEATURES.md for details)

---

## 📊 Database Tables Created

The bot automatically creates:

- `media_entries` - Main media library
- `scraped_links` - Scraped link storage
- `admins` - Admin user list
- `scraping_jobs` - Scraping history
- `activity_logs` - User activities
- `fsub_config` - Force Subscribe settings
- `user_subscriptions` - Subscription tracking
- `bot_stats` - Statistics

All tables created automatically on first run.

---

## 📈 Expected Performance

### Scraping Speed
- Small sites (100 links): 2-5 minutes
- Medium sites (500 links): 5-15 minutes
- Large sites (1000+ links): 15-60 minutes

### Search Speed
- Database search: <100ms
- With auto-scrape: 5-30 seconds

### Memory Usage
- Idle: 50-100 MB
- During scrape: 150-300 MB
- After scrape: Returns to idle

---

## ✅ Testing

### Test 1: Basic Search
```
/search test_something
```
Should show search results or auto-scrape.

### Test 2: Admin Access
```
/admin
```
Should show admin panel (if admin).

### Test 3: Full Scrape
```
/scrapeall
```
Should scrape website and export .txt to channel.

---

## 📞 Need Help?

1. **Check logs:**
   ```bash
   tail -50 logs/enhanced_bot.log
   ```

2. **Test database:**
   ```bash
   sqlite3 data/media_bot.db "SELECT COUNT(*) FROM scraped_links;"
   ```

3. **Verify config:**
   ```bash
   grep -E "BOT_TOKEN|ADMIN_ID|SCRAPE" .env
   ```

4. **Read documentation:**
   - Features: `ENHANCED_FEATURES.md`
   - Admin: `ADMIN_GUIDE.md`
   - Technical: `IMPLEMENTATION_SUMMARY.md`

---

## 🎉 You're Ready!

Your enhanced bot is ready to use. Here's what to do next:

1. ✅ Configure `.env`
2. ✅ Run bot: `python3 enhanced_bot.py`
3. ✅ Test with `/start`
4. ✅ Add admins with `/addsudo`
5. ✅ Use `/scrapeall` to scrape website
6. ✅ Watch scraped links appear in Telegram channel

---

## 📝 File Overview

```
media-bot-enhanced/
├── enhanced_bot.py              # Main application
├── enhanced_database.py         # Database operations
├── requirements.txt             # Dependencies
├── .env                        # Configuration (create from .env.example)
├── setup_enhanced.sh           # Setup script
├── data/                       # Auto-created
│   └── media_bot.db           # Database
├── logs/                       # Auto-created
│   └── enhanced_bot.log       # Bot logs
└── docs/
    ├── ENHANCED_FEATURES.md    # Features guide
    ├── ADMIN_GUIDE.md         # Admin manual
    ├── IMPLEMENTATION_SUMMARY.md # Technical
    └── QUICKSTART.md          # This file
```

---

## 🎯 Next Steps

1. **Read** → ENHANCED_FEATURES.md for all features
2. **Setup** → Configure .env with your values
3. **Test** → Run bot and test commands
4. **Deploy** → Use systemd or Docker for production
5. **Manage** → Use ADMIN_GUIDE.md for operations

---

**Version:** 2.0.0 - Enhanced Edition  
**Status:** Production Ready ✅  
**Last Updated:** January 2024

Happy botting! 🚀
