# Enhanced Media Link Bot - Features & Setup Guide

## 🚀 New Features

### 1. **Automatic Web Scraping**
When a user searches for something not found in the database, the bot automatically scrapes the configured website to find results.

**How it works:**
```
User: /search Movie_XYZ
Bot: "Not found in DB, scraping website..."
Bot: "Found 5 results from website scrape!"
Bot: Auto-saves results to database
```

### 2. **/scrapeall Command (Admin Only)**
Scrapes the entire website and saves all media links to the database and exports to Telegram channel.

**Command:**
```bash
/scrapeall
```

**What it does:**
- ✅ Scrapes entire website
- ✅ Extracts all links
- ✅ Finds media files (mp4, mkv, pdf, etc.)
- ✅ Saves to SQLite database
- ✅ Exports results as `.txt` file to Telegram channel
- ✅ Provides summary statistics

**Example output:**
```
✅ Scraping Complete!

📊 Summary:
- Total Links: 456
- Media Files: 123
- Saved to Database: ✓
- Exported to Channel: ✓

🕐 Timestamp: 2024-01-15 14:23:45
```

### 3. **/addsudo Command (Main Admin Only)**
Add new admin users to the bot.

**Command:**
```bash
/addsudo 123456789
```

**Requirements:**
- Only the main admin (ADMIN_ID in .env) can use this
- Takes user_id as parameter
- Admins can use `/scrapeall` and `/admin` commands

### 4. **Admin Control Panel** (`/admin`)
Centralized dashboard for admin operations.

**Available options:**
- 🔍 Scrape All - Start full website scrape
- ➕ Add Admin - Add new admin users
- 📊 Statistics - View detailed analytics
- 🗑️ Clear Cache - Clear old data

### 5. **Telegram Channel Export**
Automatically exports all scraped links as a text file to a designated Telegram channel.

**Features:**
- Formatted text file with all links
- Organized by link type (regular links, media files)
- Timestamp included
- File naming: `scraped_links_YYYYMMDD_HHMMSS.txt`

---

## 📋 Setup Instructions

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Copy and edit `.env` file:

```bash
cp .env.example .env
```

Edit with your values:

```env
# Required
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_user_id_here

# Scraping Configuration
SCRAPE_SITE_URL=https://your-media-site.com
SCRAPE_CHANNEL_ID=-100your_channel_id

# Optional
FSUB_CHANNEL_ID=-100your_fsub_channel_id
```

### Step 3: Get Your IDs

**Bot Token:**
- Open [@BotFather](https://t.me/BotFather)
- Send `/newbot`
- Copy the bot token

**Your User ID:**
- Open [@userinfobot](https://t.me/userinfobot)
- Send any message
- Copy your ID

**Channel ID:**
- Send any message to your channel
- Forward it to [@userinfobot](https://t.me/userinfobot)
- Copy the channel ID (should start with -100)

### Step 4: Create Required Directories

```bash
mkdir -p data logs
```

### Step 5: Run the Bot

```bash
python enhanced_bot.py
```

---

## 🔐 Admin Commands Reference

### For Main Admin (ADMIN_ID)

| Command | Description | Example |
|---------|-------------|---------|
| `/addsudo <id>` | Add new admin | `/addsudo 987654321` |
| `/scrapeall` | Scrape entire website | `/scrapeall` |
| `/admin` | Open admin panel | `/admin` |

### For All Admins

| Command | Description |
|---------|-------------|
| `/scrapeall` | Scrape website |
| `/admin` | Admin panel |
| `/stats` | Detailed statistics |

---

## 🌐 Web Scraping Configuration

### Setting Up Scrape Target

In `.env`:
```env
SCRAPE_SITE_URL=https://your-website.com/media
```

### Media File Types Recognized

By default, the bot recognizes these file types:
- Video: `.mp4`, `.mkv`, `.avi`
- Documents: `.pdf`
- Archives: `.zip`, `.rar`, `.7z`
- Torrents: `.torrent`

To add more, edit the bot code:
```python
media_extensions = ['.mp4', '.mkv', '.avi', '.pdf', '.zip', '.rar', '.7z']
```

### Auto-Scrape on Search

When enabled (default), if a search result is not found in the database:
1. Bot notifies user: "❌ Not found in database. 🔍 Scraping website..."
2. Bot scrapes website for the query
3. Returns matching results from website
4. Saves results to database for future searches

---

## 💾 Database Structure

### New Tables

**scraped_links:**
```sql
- id (INTEGER PRIMARY KEY)
- url (TEXT UNIQUE)
- title (TEXT)
- media_type (TEXT)
- description (TEXT)
- file_size (TEXT)
- scraped_at (TIMESTAMP)
- added_to_db (TIMESTAMP)
```

**admins:**
```sql
- admin_id (INTEGER PRIMARY KEY)
- username (TEXT)
- added_by (INTEGER)
- added_at (TIMESTAMP)
```

**scraping_jobs:**
```sql
- id (INTEGER PRIMARY KEY)
- job_type (TEXT)
- url (TEXT)
- status (TEXT)
- links_found (INTEGER)
- media_found (INTEGER)
- started_at (TIMESTAMP)
- completed_at (TIMESTAMP)
- error_message (TEXT)
```

---

## 📊 Admin Statistics

View detailed bot statistics:

```
📊 BOT STATISTICS

📁 Media Entries: 1,234
🔗 Scraped Links: 5,678
📝 Activities Logged: 12,456
👤 Unique Users: 234
👨‍💼 Total Admins: 5
```

---

## 🔍 Search Behavior

### Priority Order

1. **Direct Database Search** - Fast, already saved results
2. **Auto-Scrape** (if enabled) - Searches website automatically
3. **Return "Not Found"** - If both fail

### Example Search Flow

```
User: /search "Movie 2024"
↓
Bot searches database
↓
Not found in DB
↓
Bot scrapes website for "Movie 2024"
↓
Found 3 matching results
↓
Results saved to database
↓
User gets links
```

---

## 🛡️ Security Features

### Admin-Only Commands

```python
# Only these users can execute
if not bot_instance.is_admin(user_id):
    return "❌ Admin only!"
```

### Activity Logging

Every action is logged:
- Search queries
- Admin commands
- Scraping jobs
- Errors

View logs:
```bash
tail -f logs/enhanced_bot.log
```

### Input Validation

- URLs validated before processing
- User IDs verified before adding as admin
- Database queries use parameterized statements

---

## 🐛 Troubleshooting

### Scraping Not Working

**Problem:** Scrape returns no results

**Solutions:**
1. Check `SCRAPE_SITE_URL` in `.env`
2. Verify website is accessible
3. Check logs: `tail logs/enhanced_bot.log`
4. Verify site HTML structure matches parser

### Links Not Saving to Channel

**Problem:** `/scrapeall` runs but doesn't export to channel

**Solutions:**
1. Verify `SCRAPE_CHANNEL_ID` is set in `.env`
2. Make bot admin in the channel
3. Check channel permissions
4. Verify channel ID format (should start with -100)

### Database Errors

**Problem:** SQLite database locked

**Solutions:**
```bash
# Backup database
cp data/media_bot.db data/media_bot.db.backup

# Remove old database
rm data/media_bot.db

# Restart bot
python enhanced_bot.py
```

### Admin Commands Not Working

**Problem:** `/addsudo` or `/scrapeall` says "Admin only"

**Solutions:**
1. Verify your ID matches `ADMIN_ID` in `.env`
2. Check if you were added with `/addsudo`
3. Restart bot after adding admin
4. Check database: `sqlite3 data/media_bot.db "SELECT * FROM admins;"`

---

## 📈 Performance Optimization

### Scraping Large Websites

For sites with 1000+ pages:

1. Set longer timeout in `.env`:
```env
SCRAPE_TIMEOUT=60
```

2. Run scraping during off-hours
3. Monitor system resources:
```bash
watch -n 1 'ps aux | grep enhanced_bot.py'
```

### Database Optimization

Enable auto-cleanup of old scraped links:

```env
AUTO_CLEANUP_ENABLED=true
CLEANUP_INTERVAL_DAYS=30
```

---

## 📝 Common Use Cases

### Case 1: Movie Database Bot

```env
SCRAPE_SITE_URL=https://movies.example.com/downloads
SCRAPE_CHANNEL_ID=-100123456789
```

Run `/scrapeall` daily to keep database updated.

### Case 2: Software Library

```env
SCRAPE_SITE_URL=https://software.example.com/downloads
```

Users can search for software, bot auto-scrapes for new versions.

### Case 3: Document Repository

```env
SCRAPE_SITE_URL=https://docs.example.com/archive
MEDIA_EXTENSIONS=.pdf,.docx,.xlsx
```

Bot focuses on document file types.

---

## 🚀 Deployment

### Using Systemd

Create `/etc/systemd/system/media-bot.service`:

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
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable media-bot
sudo systemctl start media-bot
```

---

## 📞 Support

For issues or questions:
- Check logs: `logs/enhanced_bot.log`
- Review database: `sqlite3 data/media_bot.db`
- Contact bot admin

---

**Version:** 2.0.0 - Enhanced Edition
**Last Updated:** 2024-01-15
