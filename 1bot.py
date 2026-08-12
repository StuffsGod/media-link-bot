#!/usr/bin/env python3
"""
Enhanced Telegram Media Link Bot with Web Scraping
- Auto-scraping when search not found in DB
- /scrapeall command for full site scraping
- /addsudo for admin management
- Telegram channel link storage
"""

import logging
import os
import json
import asyncio
import aiohttp
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
from telegram.constants import ChatAction
from bs4 import BeautifulSoup
import sqlite3
from url_parser import URLParser
from database import Database

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
SCRAPE_CHANNEL_ID = os.getenv('SCRAPE_CHANNEL_ID')  # Channel to save scraped links
DATABASE_PATH = os.getenv('DATABASE_PATH', './data/media_bot.db')
SCRAPE_SITE_URL = os.getenv('SCRAPE_SITE_URL')  # Website to scrape from

# States for conversation
WAITING_FOR_SUDO_ID = 1
WAITING_FOR_SCRAPE_SITE = 2


class EnhancedBot:
    def __init__(self):
        self.db = Database(DATABASE_PATH)
        self.url_parser = URLParser()
        self.admins = self._load_admins()
        self.scrape_site = SCRAPE_SITE_URL or "https://example.com"
        
    def _load_admins(self):
        """Load admin IDs from database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT admin_id FROM admins')
            admins = {row[0] for row in cursor.fetchall()}
            admins.add(ADMIN_ID)  # Always include main admin
            return admins
        except sqlite3.OperationalError:
            logger.warning("Admins table doesn't exist yet")
            return {ADMIN_ID}
        finally:
            conn.close()
    
    def _save_admin(self, admin_id: int):
        """Save admin to database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    admin_id INTEGER PRIMARY KEY,
                    added_by INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute(
                'INSERT OR IGNORE INTO admins (admin_id, added_by) VALUES (?, ?)',
                (admin_id, ADMIN_ID)
            )
            conn.commit()
            self.admins.add(admin_id)
            logger.info(f"Admin {admin_id} added")
        except Exception as e:
            logger.error(f"Error saving admin: {e}")
        finally:
            conn.close()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.admins
    
    async def scrape_website(self, url: str = None) -> dict:
        """Scrape website for links and media"""
        if url is None:
            url = self.scrape_site
        
        logger.info(f"Starting scrape of {url}")
        scraped_data = {
            'links': [],
            'media': [],
            'files': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract all links
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if href.startswith('http') or href.startswith('www'):
                                scraped_data['links'].append({
                                    'url': href,
                                    'text': link.get_text(strip=True),
                                    'scraped_at': datetime.now().isoformat()
                                })
                        
                        # Extract media links (mp4, mkv, pdf, etc)
                        media_extensions = ['.mp4', '.mkv', '.avi', '.pdf', '.zip', '.rar', '.7z']
                        for link in soup.find_all('a', href=True):
                            href = link['href'].lower()
                            if any(ext in href for ext in media_extensions):
                                scraped_data['media'].append({
                                    'url': link['href'],
                                    'text': link.get_text(strip=True) or 'Download',
                                    'type': [ext for ext in media_extensions if ext in href][0],
                                    'scraped_at': datetime.now().isoformat()
                                })
                        
                        logger.info(f"Scraped {len(scraped_data['links'])} links, {len(scraped_data['media'])} media files")
        except asyncio.TimeoutError:
            logger.error(f"Timeout while scraping {url}")
        except Exception as e:
            logger.error(f"Error scraping website: {e}")
        
        return scraped_data
    
    async def save_scraped_to_db(self, scraped_data: dict):
        """Save scraped data to database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraped_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    title TEXT,
                    media_type TEXT,
                    scraped_at TIMESTAMP,
                    added_to_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            for link in scraped_data['links']:
                try:
                    cursor.execute('''
                        INSERT INTO scraped_links (url, title, media_type, scraped_at)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        link['url'],
                        link['text'],
                        'link',
                        link['scraped_at']
                    ))
                except sqlite3.IntegrityError:
                    pass  # Link already exists
            
            for media in scraped_data['media']:
                try:
                    cursor.execute('''
                        INSERT INTO scraped_links (url, title, media_type, scraped_at)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        media['url'],
                        media['text'],
                        media['type'],
                        media['scraped_at']
                    ))
                except sqlite3.IntegrityError:
                    pass  # Link already exists
            
            conn.commit()
            logger.info("Scraped data saved to database")
        except Exception as e:
            logger.error(f"Error saving scraped data: {e}")
        finally:
            conn.close()
    
    async def export_to_telegram(self, app: Application, scraped_data: dict):
        """Export scraped links to Telegram channel as text file"""
        if not SCRAPE_CHANNEL_ID:
            logger.warning("SCRAPE_CHANNEL_ID not configured")
            return
        
        try:
            # Create text file content
            content = f"📊 SCRAPED LINKS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"Total Links: {len(scraped_data['links'])}\n"
            content += f"Media Files: {len(scraped_data['media'])}\n"
            content += "=" * 50 + "\n\n"
            
            content += "🔗 ALL LINKS:\n"
            for link in scraped_data['links']:
                content += f"• {link['text']}\n  {link['url']}\n"
            
            content += "\n\n📁 MEDIA FILES:\n"
            for media in scraped_data['media']:
                content += f"• {media['text']} ({media['type']})\n  {media['url']}\n"
            
            # Save to file
            filename = f"scraped_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Send to channel
            with open(filename, 'rb') as f:
                await app.bot.send_document(
                    chat_id=SCRAPE_CHANNEL_ID,
                    document=f,
                    caption="🔍 Newly Scraped Links"
                )
            
            os.remove(filename)
            logger.info(f"Exported scraped data to Telegram channel {SCRAPE_CHANNEL_ID}")
        except Exception as e:
            logger.error(f"Error exporting to Telegram: {e}")


# Global bot instance
bot_instance = EnhancedBot()


# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user = update.effective_user
    welcome_text = f"""
🎉 Welcome {user.first_name}!

📱 Media Link Bot - Enhanced Version

🔍 Use /search <query> to find media
📊 Use /stats to see statistics
💬 Use /help for all commands

Made with ❤️ for media lovers
    """
    await update.message.reply_text(welcome_text)


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search for media in database"""
    if not context.args:
        await update.message.reply_text("Usage: /search <query>")
        return
    
    query = ' '.join(context.args)
    await update.message.send_chat_action(ChatAction.TYPING)
    
    # Search in database
    results = bot_instance.db.search_media(query)
    
    if results:
        response = f"🔍 Found {len(results)} results for '{query}':\n\n"
        for i, result in enumerate(results[:10], 1):
            response += f"{i}. {result['file_name']}\n"
            response += f"   Size: {result['file_size']}\n"
            response += f"   Links: {len(json.loads(result['urls']))}\n\n"
        await update.message.reply_text(response)
    else:
        # Not found in DB, trigger scraping
        await update.message.reply_text(
            f"❌ '{query}' not found in database.\n"
            "🔍 Scraping website for this query...",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ Scraping...", callback_data="scraping")]
            ])
        )
        
        # Auto-scrape from website
        scraped_data = await bot_instance.scrape_website()
        
        # Search in scraped results
        found_in_scraped = [
            link for link in scraped_data['media'] + scraped_data['links']
            if query.lower() in (link.get('text') or link['url']).lower()
        ]
        
        if found_in_scraped:
            response = f"✅ Found {len(found_in_scraped)} results from website scrape:\n\n"
            for i, item in enumerate(found_in_scraped[:5], 1):
                response += f"{i}. {item.get('text', item['url'])}\n"
                response += f"   🔗 {item['url']}\n\n"
            await update.message.reply_text(response)
            
            # Save scraped results to DB
            await bot_instance.save_scraped_to_db({
                'links': [item for item in found_in_scraped if item.get('type') == 'link'],
                'media': [item for item in found_in_scraped if item.get('type') != 'link'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            await update.message.reply_text(
                "❌ Not found in database or website.\n"
                "Try searching with different keywords."
            )


async def scrapeall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Scrape all links from website (Admin only)"""
    user_id = update.effective_user.id
    
    if not bot_instance.is_admin(user_id):
        await update.message.reply_text("❌ Only admins can use this command!")
        return
    
    await update.message.reply_text(
        "🔍 Starting full website scrape...\n"
        "This may take a few moments."
    )
    
    # Scrape website
    scraped_data = await bot_instance.scrape_website()
    
    # Save to database
    await bot_instance.save_scraped_to_db(scraped_data)
    
    # Export to Telegram
    if SCRAPE_CHANNEL_ID:
        await bot_instance.export_to_telegram(context.application, scraped_data)
    
    response = f"""
✅ Scraping Complete!

📊 Summary:
- Total Links: {len(scraped_data['links'])}
- Media Files: {len(scraped_data['media'])}
- Saved to Database: ✓
- Exported to Channel: {'✓' if SCRAPE_CHANNEL_ID else '✗'}

🕐 Timestamp: {scraped_data['timestamp']}
    """
    await update.message.reply_text(response)
    logger.info(f"Admin {user_id} executed /scrapeall")


async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add new admin (Admin only)"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Only the main admin can add new admins!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /addsudo <user_id>\n"
            "Example: /addsudo 123456789"
        )
        return
    
    try:
        new_admin_id = int(context.args[0])
        bot_instance._save_admin(new_admin_id)
        await update.message.reply_text(f"✅ User {new_admin_id} is now an admin!")
        logger.info(f"Admin {user_id} added new admin {new_admin_id}")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin control panel"""
    user_id = update.effective_user.id
    
    if not bot_instance.is_admin(user_id):
        await update.message.reply_text("❌ Only admins can use this command!")
        return
    
    keyboard = [
        [InlineKeyboardButton("🔍 Scrape All", callback_data="admin_scrapeall")],
        [InlineKeyboardButton("➕ Add Admin", callback_data="admin_addsudo")],
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("🗑️ Clear Cache", callback_data="admin_clear")],
    ]
    
    await update.message.reply_text(
        "🔧 Admin Control Panel",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    user_id = update.effective_user.id
    is_admin = bot_instance.is_admin(user_id)
    
    help_text = """
📚 AVAILABLE COMMANDS

🔍 Search & Browse:
/search <query> - Search for media
/latest - View latest entries
/stats - View statistics

"""
    
    if is_admin:
        help_text += """
🔧 ADMIN COMMANDS:
/admin - Open admin panel
/scrapeall - Scrape entire website
/addsudo <id> - Add new admin

"""
    
    help_text += """
💡 TIPS:
• Admins can scrape entire website with /scrapeall
• Searches automatically scrape if not found
• All scraped links saved to database

❓ Need help? Contact support
    """
    
    await update.message.reply_text(help_text)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show statistics"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) FROM media_entries')
        media_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM scraped_links')
        scraped_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM activity_logs')
        activities = cursor.fetchone()[0]
        
        stats_text = f"""
📊 BOT STATISTICS

📁 Media Entries: {media_count}
🔗 Scraped Links: {scraped_count}
📝 Activities Logged: {activities}

✨ Powered by Enhanced Media Link Bot
        """
        
        await update.message.reply_text(stats_text)
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        await update.message.reply_text("❌ Error fetching statistics")
    finally:
        conn.close()


def main():
    """Start the bot"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("scrapeall", scrapeall))
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("stats", stats))
    
    # Start bot
    logger.info("🤖 Enhanced Media Link Bot Starting...")
    print("""
    ╔═══════════════════════════════════╗
    ║  Enhanced Media Link Bot           ║
    ║  With Web Scraping & Admin Panel   ║
    ╚═══════════════════════════════════╝
    """)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
