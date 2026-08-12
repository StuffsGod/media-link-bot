#!/usr/bin/env python3
"""
Complete Telegram Media Link Bot with Web Scraping
- Fixed search with auto-scrape
- Integrated database (no external imports)
- Telegram channel DB setup
- Delay system for scraping
"""

import logging
import os
import json
import asyncio
import sqlite3
import re
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ChatAction
from telegram.error import TelegramError

try:
    from bs4 import BeautifulSoup
    import aiohttp
except ImportError:
    print("⚠️ Missing dependencies. Install: pip install beautifulsoup4 aiohttp")
    exit(1)

# Load environment
load_dotenv()

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Config
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
SCRAPE_CHANNEL_ID = os.getenv('SCRAPE_CHANNEL_ID')
SCRAPE_SITE_URL = os.getenv('SCRAPE_SITE_URL', 'https://example.com')
DB_PATH = os.getenv('DATABASE_PATH', './data/media_bot.db')
SCRAPE_DELAY = float(os.getenv('SCRAPE_DELAY', '1'))  # Delay between requests (seconds)
SCRAPE_TIMEOUT = int(os.getenv('SCRAPE_TIMEOUT', '30'))

# Create directories
os.makedirs('data', exist_ok=True)


class MediaDatabase:
    """Integrated database handler"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Media entries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS media_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER UNIQUE,
                file_name TEXT,
                file_size TEXT,
                urls TEXT,
                caption TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Scraped links
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                media_type TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Admins
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INTEGER PRIMARY KEY,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Activity logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute(self, query, params=None):
        """Execute query"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            result = cursor.fetchall()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Database error: {e}")
            return None
    
    def search(self, query):
        """Search media"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM media_entries 
                WHERE file_name LIKE ? OR caption LIKE ?
                ORDER BY created_at DESC LIMIT 20
            ''', (f'%{query}%', f'%{query}%'))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def search_scraped(self, query):
        """Search scraped links"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT url, title FROM scraped_links 
                WHERE title LIKE ? OR url LIKE ?
                ORDER BY scraped_at DESC LIMIT 10
            ''', (f'%{query}%', f'%{query}%'))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Scraped search error: {e}")
            return []
    
    def add_scraped(self, url, title, media_type='link'):
        """Add scraped link"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO scraped_links (url, title, media_type)
                VALUES (?, ?, ?)
            ''', (url, title, media_type))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding scraped link: {e}")
            return False
    
    def is_admin(self, user_id):
        """Check admin"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM admins WHERE admin_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None or user_id == ADMIN_ID
    
    def add_admin(self, user_id):
        """Add admin"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO admins (admin_id) VALUES (?)', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding admin: {e}")
            return False
    
    def log_action(self, user_id, action):
        """Log action"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO activity_logs (user_id, action) VALUES (?, ?)', 
                         (user_id, action))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Logging error: {e}")
    
    def get_stats(self):
        """Get statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM media_entries')
            media_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM scraped_links')
            scraped_count = cursor.fetchone()[0]
            conn.close()
            return {'media': media_count, 'scraped': scraped_count}
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {'media': 0, 'scraped': 0}


class WebScraper:
    """Web scraper with delay system"""
    
    def __init__(self, delay=1, timeout=30):
        self.delay = delay
        self.timeout = timeout
    
    async def scrape(self, url):
        """Scrape website with delay"""
        logger.info(f"Starting scrape of {url}")
        links = {'urls': [], 'media': []}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract links
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            text = link.get_text(strip=True) or href
                            
                            if href.startswith('http'):
                                # Check if media
                                media_ext = ['.mp4', '.mkv', '.pdf', '.zip', '.rar', '.7z']
                                is_media = any(ext in href.lower() for ext in media_ext)
                                
                                if is_media:
                                    links['media'].append({'url': href, 'title': text})
                                else:
                                    links['urls'].append({'url': href, 'title': text})
                            
                            # Delay between requests
                            await asyncio.sleep(self.delay)
                        
                        logger.info(f"Scraped: {len(links['urls'])} links, {len(links['media'])} media")
        
        except asyncio.TimeoutError:
            logger.error(f"Scrape timeout for {url}")
        except Exception as e:
            logger.error(f"Scrape error: {e}")
        
        return links


# Global instances
db = MediaDatabase(DB_PATH)
scraper = WebScraper(delay=SCRAPE_DELAY, timeout=SCRAPE_TIMEOUT)


# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user = update.effective_user
    msg = f"""
🎉 **Welcome {user.first_name}!**

📱 **Media Link Bot**

🔍 Commands:
/search <query> - Search for media
/stats - View statistics
/help - All commands

Admin:
/addsudo <id> - Add admin
/scrapeall - Scrape website
/admin - Admin panel
    """
    await update.message.reply_text(msg, parse_mode='Markdown')
    db.log_action(user.id, 'start')


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search command with auto-scrape"""
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text("Usage: /search <query>")
        return
    
    query = ' '.join(context.args)
    await update.message.send_chat_action(ChatAction.TYPING)
    
    db.log_action(user.id, f'search:{query}')
    
    # Search in database
    results = db.search(query)
    
    if results:
        msg = f"🔍 Found {len(results)} results for **{query}**:\n\n"
        for i, result in enumerate(results[:10], 1):
            msg += f"{i}. {result[1]}\n"
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    # Not in DB - scrape website
    await update.message.reply_text(
        f"❌ **{query}** not found in database\n\n"
        "🔍 Scraping website...",
        parse_mode='Markdown'
    )
    
    try:
        links = await scraper.scrape(SCRAPE_SITE_URL)
        
        # Search in scraped results
        found = []
        for item in links['media'] + links['urls']:
            if query.lower() in (item['title'] + item['url']).lower():
                found.append(item)
        
        if found:
            msg = f"✅ Found {len(found)} results from website:\n\n"
            for i, item in enumerate(found[:5], 1):
                msg += f"{i}. {item['title']}\n🔗 {item['url']}\n\n"
                # Save to DB
                db.add_scraped(item['url'], item['title'])
            
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ No results found for **{query}**", 
                                           parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text(f"❌ Error during scrape: {str(e)}", 
                                       parse_mode='Markdown')


async def scrapeall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Scrape all - admin only"""
    user_id = update.effective_user.id
    
    if not db.is_admin(user_id):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    await update.message.reply_text(
        "🔍 Starting website scrape...\n"
        "This may take a while. (Using delay system)"
    )
    
    try:
        links = await scraper.scrape(SCRAPE_SITE_URL)
        
        # Save all to database
        added = 0
        for link in links['media'] + links['urls']:
            if db.add_scraped(link['url'], link['title']):
                added += 1
        
        # Export to telegram
        if SCRAPE_CHANNEL_ID:
            content = f"📊 Scraped Links - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"Total: {len(links['urls']) + len(links['media'])}\n"
            content += "=" * 50 + "\n\n"
            
            content += "🔗 Links:\n"
            for link in links['urls'][:50]:
                content += f"• {link['title']}\n  {link['url']}\n"
            
            content += "\n📁 Media:\n"
            for link in links['media'][:50]:
                content += f"• {link['title']}\n  {link['url']}\n"
            
            # Save and send file
            filename = f"links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            try:
                with open(filename, 'rb') as f:
                    await context.bot.send_document(
                        chat_id=SCRAPE_CHANNEL_ID,
                        document=f,
                        caption="🔍 Scraped Links"
                    )
                os.remove(filename)
            except TelegramError as e:
                logger.error(f"Telegram export error: {e}")
                await update.message.reply_text(f"⚠️ Channel export failed: {str(e)}", 
                                               parse_mode='Markdown')
        
        msg = f"""
✅ **Scraping Complete!**

📊 Summary:
- Links Found: {len(links['urls'])}
- Media Found: {len(links['media'])}
- Added to DB: {added}
- Exported: {'✅' if SCRAPE_CHANNEL_ID else '❌'}

🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        await update.message.reply_text(msg, parse_mode='Markdown')
        db.log_action(user_id, 'scrapeall_done')
    
    except Exception as e:
        logger.error(f"Scrapeall error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='Markdown')


async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add admin - main admin only"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Only main admin can add admins!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /addsudo <user_id>")
        return
    
    try:
        new_admin = int(context.args[0])
        if db.add_admin(new_admin):
            await update.message.reply_text(f"✅ User {new_admin} is now admin!")
            db.log_action(user_id, f'added_admin:{new_admin}')
        else:
            await update.message.reply_text("⚠️ User already admin or error occurred")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel"""
    user_id = update.effective_user.id
    
    if not db.is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    keyboard = [
        [InlineKeyboardButton("🔍 Scrape All", callback_data="scrape")],
        [InlineKeyboardButton("➕ Add Admin", callback_data="addsudo_btn")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats_btn")],
    ]
    
    await update.message.reply_text(
        "🔧 **Admin Panel**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show statistics"""
    s = db.get_stats()
    msg = f"""
📊 **Statistics**

📁 Media Entries: {s['media']}
🔗 Scraped Links: {s['scraped']}

✨ Powered by Enhanced Bot
    """
    await update.message.reply_text(msg, parse_mode='Markdown')


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    user_id = update.effective_user.id
    
    msg = """
📚 **Available Commands**

**User Commands:**
/search <query> - Search media
/stats - View statistics
/help - This message
/start - Welcome message

**Admin Commands:**
/addsudo <id> - Add admin
/scrapeall - Scrape website
/admin - Admin panel

**Setup:**
1. Get BOT_TOKEN from @BotFather
2. Get ADMIN_ID from @userinfobot
3. Set SCRAPE_SITE_URL in .env
4. Set SCRAPE_CHANNEL_ID for exports
5. Run: python3 bot.py

**Features:**
✅ Auto-scrape on search
✅ Full website scraping
✅ Admin management
✅ Telegram exports
✅ Delay system (no rate limit)
    """
    
    await update.message.reply_text(msg, parse_mode='Markdown')


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "scrape":
        await scrapeall(query, context)
    elif query.data == "stats_btn":
        await stats(query, context)


def main():
    """Start bot"""
    print("""
    ╔════════════════════════════════════════╗
    ║   Enhanced Media Link Bot v2.1         ║
    ║   Search + Scraping + Admin Panel      ║
    ╚════════════════════════════════════════╝
    """)
    
    # Validate config
    if not BOT_TOKEN or BOT_TOKEN == 'your_token':
        print("❌ BOT_TOKEN not set in .env")
        return
    
    if ADMIN_ID == 0 or not ADMIN_ID:
        print("❌ ADMIN_ID not set in .env")
        return
    
    print(f"✅ BOT_TOKEN: Set")
    print(f"✅ ADMIN_ID: {ADMIN_ID}")
    print(f"✅ SCRAPE_URL: {SCRAPE_SITE_URL}")
    print(f"✅ SCRAPE_CHANNEL: {SCRAPE_CHANNEL_ID or 'Not set'}")
    print(f"✅ SCRAPE_DELAY: {SCRAPE_DELAY}s")
    print()
    
    # Create app
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("scrapeall", scrapeall))
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Bot is running... (Press Ctrl+C to stop)")
    print()
    
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\n✅ Bot stopped")


if __name__ == "__main__":
    main()
