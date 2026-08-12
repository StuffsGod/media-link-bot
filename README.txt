╔════════════════════════════════════════════════════════════════════╗
║                   MEDIA LINK BOT - QUICK START                    ║
╚════════════════════════════════════════════════════════════════════╝

📦 WHAT YOU HAVE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. bot.py              ← Main bot application (use this)
2. requirements.txt    ← Python dependencies
3. .env.example        ← Configuration template
4. SETUP.txt           ← Detailed setup guide
5. README.txt          ← This file

╔════════════════════════════════════════════════════════════════════╗
║                         3-MINUTE SETUP                            ║
╚════════════════════════════════════════════════════════════════════╝

STEP 1: Install Dependencies
────────────────────────────
$ pip install -r requirements.txt

STEP 2: Create .env File
────────────────────────
Copy .env.example → .env
Edit with your values:

BOT_TOKEN=your_token        (get from @BotFather)
ADMIN_ID=your_id            (get from @userinfobot)  
SCRAPE_SITE_URL=https://...  (your website)
SCRAPE_CHANNEL_ID=-100...   (your channel - optional)

STEP 3: Run Bot
────────────────
$ python3 bot.py

✅ Bot is running!

╔════════════════════════════════════════════════════════════════════╗
║                       AVAILABLE COMMANDS                          ║
╚════════════════════════════════════════════════════════════════════╝

FOR EVERYONE:
/start              Welcome message
/search <query>     Search media (auto-scrapes if not found)
/stats              View statistics
/help               Show all commands

FOR ADMINS:
/addsudo <id>       Add new admin (main admin only)
/scrapeall          Scrape entire website
/admin              Admin panel

╔════════════════════════════════════════════════════════════════════╗
║                          FEATURES                                 ║
╚════════════════════════════════════════════════════════════════════╝

✅ AUTO-SCRAPING
   Search not found in database? Bot scrapes website automatically

✅ /scrapeall COMMAND
   • Scrapes entire website
   • Extracts all links and media
   • Saves to database
   • Exports as .txt to Telegram channel

✅ ADMIN MANAGEMENT
   • Add admins with /addsudo
   • Admin-only commands
   • Activity logging

✅ DELAY SYSTEM
   • Prevents rate limiting
   • Configurable delay between requests

✅ DATABASE
   • Auto-creates SQLite database
   • Stores media, scraped links, admin data

╔════════════════════════════════════════════════════════════════════╗
║                        HOW IT WORKS                               ║
╚════════════════════════════════════════════════════════════════════╝

SEARCH FLOW:
────────────
User: /search "Movie"
  ↓
Bot searches database
  ↓
Found? → Return results
  ↓
Not found? → Scrape website
  ↓
Save results to database
  ↓
Return to user

SCRAPEALL FLOW:
───────────────
Admin: /scrapeall
  ↓
Validate admin access
  ↓
Scrape SCRAPE_SITE_URL
  ↓
Extract all links & media
  ↓
Save to database
  ↓
Export as .txt to channel
  ↓
Show summary

╔════════════════════════════════════════════════════════════════════╗
║                     GETTING YOUR IDs                              ║
╚════════════════════════════════════════════════════════════════════╝

BOT_TOKEN:
1. Open https://t.me/BotFather
2. Send /newbot
3. Follow instructions
4. Copy the token

ADMIN_ID:
1. Open https://t.me/userinfobot
2. Send any message
3. Copy your ID

SCRAPE_CHANNEL_ID:
1. Create a Telegram channel
2. Send a message in it
3. Forward to https://t.me/userinfobot
4. Copy the channel ID (starts with -100)

╔════════════════════════════════════════════════════════════════════╗
║                    TROUBLESHOOTING                                ║
╚════════════════════════════════════════════════════════════════════╝

PROBLEM: Bot doesn't start
→ Check BOT_TOKEN in .env
→ Run: pip install -r requirements.txt
→ Check Python version: python3 --version (needs 3.8+)

PROBLEM: /search gives no response
→ Check SCRAPE_SITE_URL is correct
→ Verify website is accessible
→ Check logs: tail -20 logs/bot.log

PROBLEM: /scrapeall doesn't export to channel
→ Set SCRAPE_CHANNEL_ID in .env
→ Make bot admin in the channel
→ Check channel permissions

PROBLEM: "Database is locked"
→ Stop bot
→ Remove old database: rm data/media_bot.db
→ Start bot again

╔════════════════════════════════════════════════════════════════════╗
║                   CONFIGURATION OPTIONS                           ║
╚════════════════════════════════════════════════════════════════════╝

Required:
─────────
BOT_TOKEN              Bot token from @BotFather
ADMIN_ID               Your Telegram user ID
SCRAPE_SITE_URL        Website to scrape

Optional:
─────────
SCRAPE_CHANNEL_ID      Channel to export (.txt files)
SCRAPE_DELAY           Delay between requests (default: 1s)
SCRAPE_TIMEOUT         Scrape timeout (default: 30s)
DATABASE_PATH          Database location (default: ./data/media_bot.db)

╔════════════════════════════════════════════════════════════════════╗
║                    PRODUCTION DEPLOYMENT                          ║
╚════════════════════════════════════════════════════════════════════╝

OPTION 1: Background Process (Linux/Mac)
────────────────────────────────────────
$ nohup python3 bot.py > bot.log 2>&1 &

OPTION 2: Systemd Service (Recommended)
────────────────────────────────────────
1. Create /etc/systemd/system/media-bot.service

[Unit]
Description=Media Link Bot
After=network.target

[Service]
Type=simple
User=debian
WorkingDirectory=/home/debian/media-bot
ExecStart=/usr/bin/python3 /home/debian/media-bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target

2. Enable and start:
$ sudo systemctl enable media-bot
$ sudo systemctl start media-bot

3. View status/logs:
$ sudo systemctl status media-bot
$ sudo journalctl -u media-bot -f

╔════════════════════════════════════════════════════════════════════╗
║                    EXAMPLE .env FILE                              ║
╚════════════════════════════════════════════════════════════════════╝

BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
ADMIN_ID=987654321
SCRAPE_SITE_URL=https://example.com/media
SCRAPE_CHANNEL_ID=-100123456789
SCRAPE_DELAY=1
SCRAPE_TIMEOUT=30
DATABASE_PATH=./data/media_bot.db

╔════════════════════════════════════════════════════════════════════╗
║                      QUICK TEST                                   ║
╚════════════════════════════════════════════════════════════════════╝

1. Start bot:
   $ python3 bot.py

2. In Telegram - Send: /start
   → Should see welcome message

3. Send: /search test
   → Should search or scrape

4. Send: /stats
   → Should show statistics

5. If admin - Send: /scrapeall
   → Should scrape and export

╔════════════════════════════════════════════════════════════════════╗
║                      WHAT'S INCLUDED                              ║
╚════════════════════════════════════════════════════════════════════╝

✅ Integrated Database
   - No external dependencies
   - Auto-creates tables
   - Stores: media, scraped links, admins, activities

✅ Web Scraping
   - Beautiful Soup for parsing
   - Async with aiohttp
   - Delay system to prevent rate limiting
   - Configurable timeout

✅ Admin System
   - /addsudo to add admins
   - Admin-only commands
   - Activity logging

✅ Auto Search Scraping
   - Search not in DB?
   - Bot scrapes website automatically
   - Results saved for next time

✅ Telegram Export
   - /scrapeall exports as .txt file
   - Organized by link type
   - Timestamp included

╔════════════════════════════════════════════════════════════════════╗
║                   FILE DESCRIPTIONS                               ║
╚════════════════════════════════════════════════════════════════════╝

bot.py
------
Main application file (19KB, 400+ lines)
✓ Integrated database (no imports needed)
✓ Web scraper with delay system
✓ All command handlers
✓ Telegram bot setup
✓ Admin management
✓ Error handling & logging

requirements.txt
────────────────
Python dependencies (4 packages)
✓ python-telegram-bot==20.3
✓ beautifulsoup4==4.12.2
✓ aiohttp==3.9.1
✓ python-dotenv==1.0.0

.env.example
────────────
Configuration template
Copy to .env and fill in your values

SETUP.txt
─────────
Detailed setup instructions
Database info, troubleshooting, examples

README.txt
──────────
This file - quick reference

╔════════════════════════════════════════════════════════════════════╗
║                        VERSION INFO                               ║
╚════════════════════════════════════════════════════════════════════╝

Version: 2.1
Status: ✅ Production Ready
Features: 8+ working features
Tested: ✅ All features verified
Ready: ✅ Ready for deployment

╔════════════════════════════════════════════════════════════════════╗
║                        NEED HELP?                                 ║
╚════════════════════════════════════════════════════════════════════╝

1. Read SETUP.txt for detailed guide
2. Check logs: cat logs/bot.log
3. Verify .env configuration
4. Test database: sqlite3 data/media_bot.db
5. Check website accessibility

═══════════════════════════════════════════════════════════════════════
Ready to go? Run: python3 bot.py
═══════════════════════════════════════════════════════════════════════
