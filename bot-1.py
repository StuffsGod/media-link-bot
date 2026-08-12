"""
Telegram Media Bot - Main application file
Handles all bot commands, message processing, and Force Subscribe logic.
"""

import os
import logging
from typing import Optional, List
from dotenv import load_dotenv

from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton,
    ChatPermissions, ChatMember
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes, ConversationHandler
)
from telegram.constants import ParseMode, ChatAction
from telegram.error import TelegramError

from database import Database
from url_parser import URLParser

# Load environment variables
load_dotenv()

# ==================== CONFIGURATION ====================

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
DATABASE_PATH = os.getenv('DATABASE_PATH', './data/media_bot.db')
FSUB_CHANNEL_ID = os.getenv('FSUB_CHANNEL_ID')
if FSUB_CHANNEL_ID:
    FSUB_CHANNEL_ID = int(FSUB_CHANNEL_ID)

BOT_MADE_BY = os.getenv('BOT_MADE_BY', '@Franited')
POWERED_BY = os.getenv('POWERED_BY', '@Dokjaxvibe')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', './logs/bot.log')

# ==================== LOGGING SETUP ====================

os.makedirs(os.path.dirname(LOG_FILE) or '.', exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== CONVERSATION STATES ====================

FSub_VERIFY, EDIT_FSUB, WAIT_CHANNEL_MSG = range(3)

# ==================== DATABASE INITIALIZATION ====================

try:
    db = Database(DATABASE_PATH)
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise

# ==================== UTILITY FUNCTIONS ====================

def get_admin_check(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id == ADMIN_ID


async def check_fsub(app: Application, user_id: int) -> bool:
    """
    Check if user is subscribed to FSub channel.
    
    Args:
        app: Telegram application instance
        user_id: User ID to check
        
    Returns:
        True if no FSub configured or user is subscribed
    """
    if not FSUB_CHANNEL_ID:
        return True
    
    fsub_config = db.get_fsub_channel()
    if not fsub_config:
        return True
    
    try:
        member = await app.bot.get_chat_member(FSUB_CHANNEL_ID, user_id)
        
        # Check if user is member (not restricted/kicked)
        if member.status in ['member', 'administrator', 'creator', 'restricted']:
            # For restricted members, check if they can view messages
            if member.status == 'restricted':
                return member.can_send_messages or member.can_view_messages
            return True
        
        return False
        
    except TelegramError:
        return False


def create_fsub_buttons(channel_invite_link: Optional[str] = None) -> InlineKeyboardMarkup:
    """Create Force Subscribe buttons."""
    buttons = []
    
    if channel_invite_link:
        buttons.append([
            InlineKeyboardButton("✅ Join Channel", url=channel_invite_link)
        ])
    
    buttons.append([
        InlineKeyboardButton("🔄 Check Subscription", callback_data="check_fsub")
    ])
    
    return InlineKeyboardMarkup(buttons)


def create_link_buttons(urls: List[str]) -> InlineKeyboardMarkup:
    """Create buttons for media links."""
    buttons = []
    
    # Add download buttons (max 3 per row)
    for i, url in enumerate(urls[:6]):  # Max 6 links as buttons
        label = f"📥 Link {i+1}" if len(urls) > 1 else "📥 Download"
        buttons.append([InlineKeyboardButton(label, url=url)])
    
    # Add "Show All" button if more links exist
    if len(urls) > 6:
        buttons.append([
            InlineKeyboardButton("📄 Show All Links", callback_data="show_all_links")
        ])
    
    return InlineKeyboardMarkup(buttons)


def format_media_message(file_name: str, file_size: Optional[str], 
                        caption: Optional[str], urls: List[str]) -> str:
    """Format media information for display."""
    text = f"<b>📁 {file_name}</b>\n"
    
    if file_size:
        text += f"<b>📊 Size:</b> {file_size}\n"
    
    text += "\n<b>🔗 Available Links:</b>\n"
    
    for i, url in enumerate(urls, 1):
        text += f"{i}. {url}\n"
    
    if caption:
        text += f"\n<b>📝 Description:</b>\n{caption}\n"
    
    text += f"\n<i>Powered by {POWERED_BY}</i>"
    
    return text


# ==================== COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user_id = update.effective_user.id
    
    await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    
    welcome_text = (
        f"🤖 <b>Welcome to Media Link Bot!</b>\n\n"
        f"Bot made by {BOT_MADE_BY}\n"
        f"Powered by {POWERED_BY}\n\n"
        f"<b>Available Commands:</b>\n"
        f"/help - Show all available commands\n"
        f"/search - Search saved media\n"
        f"/latest - View latest media entries\n"
        f"/stats - View bot statistics\n"
        f"/about - About this bot\n\n"
        f"<b>For Admins:</b>\n"
        f"/admin - Admin control panel\n"
    )
    
    # Log activity
    db.log_activity(user_id, "START", None)
    
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    user_id = update.effective_user.id
    is_admin = get_admin_check(user_id)
    
    help_text = (
        "<b>📖 Help - Available Commands</b>\n\n"
        "<b>General Commands:</b>\n"
        "/start - Welcome message\n"
        "/help - Show this message\n"
        "/about - Bot information\n"
        "/stats - View statistics\n\n"
        "<b>Search Commands:</b>\n"
        "/search <query> - Search media by name\n"
        "/latest - View 10 latest entries\n\n"
    )
    
    if is_admin:
        help_text += (
            "<b>Admin Commands:</b>\n"
            "/admin - Open admin panel\n"
            "/configure_fsub - Setup Force Subscribe\n"
            "/verify_bot - Check bot permissions\n"
            "/stats_detailed - Full statistics\n"
            "/clear_fsub - Remove FSub configuration\n"
        )
    
    db.log_activity(user_id, "HELP", None)
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command."""
    user_id = update.effective_user.id
    
    about_text = (
        f"<b>📱 About This Bot</b>\n\n"
        f"<b>Purpose:</b>\n"
        f"Manage and distribute media/file links with Force Subscribe support.\n\n"
        f"<b>Features:</b>\n"
        f"✅ Save and organize media links\n"
        f"✅ Search saved media\n"
        f"✅ Force Subscribe verification\n"
        f"✅ Admin control panel\n"
        f"✅ Activity logging\n"
        f"✅ Statistics tracking\n\n"
        f"<b>Bot Creator:</b> {BOT_MADE_BY}\n"
        f"<b>Powered by:</b> {POWERED_BY}\n"
    )
    
    db.log_activity(user_id, "ABOUT", None)
    await update.message.reply_text(about_text, parse_mode=ParseMode.HTML)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command."""
    user_id = update.effective_user.id
    
    db.update_statistics()
    stats = db.get_statistics()
    
    stats_text = (
        f"<b>📊 Bot Statistics</b>\n\n"
        f"<b>Media Entries:</b> {stats.get('total_media_entries', 0)}\n"
        f"<b>Total Users:</b> {stats.get('total_users', 0)}\n"
        f"<b>Total Requests:</b> {stats.get('total_requests', 0)}\n"
    )
    
    db.log_activity(user_id, "STATS", None)
    await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /search command."""
    user_id = update.effective_user.id
    
    # Check FSub
    if not await check_fsub(context.application, user_id):
        fsub_config = db.get_fsub_channel()
        await update.message.reply_text(
            "❌ <b>You must join our channel to use this feature.</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=create_fsub_buttons()
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ <b>Please provide a search query.</b>\n\n"
            "<code>/search movie_name</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    query = " ".join(context.args)
    results = db.search_media(query, limit=20)
    
    if not results:
        await update.message.reply_text(
            f"❌ <b>No results found for:</b> <code>{query}</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    response = f"<b>🔍 Search Results for: {query}</b>\n\n"
    
    for i, media in enumerate(results[:10], 1):
        response += f"{i}. <b>{media['file_name']}</b>\n"
        if media.get('file_size'):
            response += f"   Size: {media['file_size']}\n"
        response += "\n"
    
    db.log_activity(user_id, "SEARCH", query)
    await update.message.reply_text(response, parse_mode=ParseMode.HTML)


async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /latest command."""
    user_id = update.effective_user.id
    
    # Check FSub
    if not await check_fsub(context.application, user_id):
        await update.message.reply_text(
            "❌ <b>You must join our channel to use this feature.</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=create_fsub_buttons()
        )
        return
    
    results = db.get_all_media(limit=10)
    
    if not results:
        await update.message.reply_text(
            "📭 <b>No media entries saved yet.</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    response = "<b>📋 Latest Media Entries</b>\n\n"
    
    for i, media in enumerate(results, 1):
        response += f"{i}. <b>{media['file_name']}</b>\n"
        if media.get('file_size'):
            response += f"   Size: {media['file_size']}\n"
        response += "\n"
    
    db.log_activity(user_id, "LATEST", None)
    await update.message.reply_text(response, parse_mode=ParseMode.HTML)


# ==================== ADMIN COMMANDS ====================

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /admin command - show admin panel."""
    user_id = update.effective_user.id
    
    if not get_admin_check(user_id):
        await update.message.reply_text("❌ <b>Unauthorized.</b> This command is for admins only.", parse_mode=ParseMode.HTML)
        return
    
    media_count = db.get_total_media_count()
    fsub_config = db.get_fsub_channel()
    
    admin_text = (
        "<b>⚙️ Admin Control Panel</b>\n\n"
        f"<b>📊 Statistics:</b>\n"
        f"  • Media Entries: {media_count}\n"
        f"  • FSub Channel: {'✅ Configured' if fsub_config else '❌ Not Configured'}\n\n"
        "<b>🔧 Admin Options:</b>\n"
    )
    
    buttons = [
        [InlineKeyboardButton("🔗 Configure FSub", callback_data="admin_fsub")],
        [InlineKeyboardButton("✅ Verify Bot Permissions", callback_data="admin_verify")],
        [InlineKeyboardButton("📊 Detailed Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("🗑️ Clear FSub", callback_data="admin_clear_fsub")],
    ]
    
    db.log_activity(user_id, "ADMIN_PANEL", None)
    
    await update.message.reply_text(
        admin_text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def configure_fsub_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /configure_fsub command."""
    user_id = update.effective_user.id
    
    if not get_admin_check(user_id):
        await update.message.reply_text("❌ <b>Unauthorized.</b>", parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    
    await update.message.reply_text(
        "📋 <b>Force Subscribe Setup</b>\n\n"
        "Please forward any message from the channel you want to set as FSub channel.\n"
        "The bot will automatically detect the channel ID.",
        parse_mode=ParseMode.HTML
    )
    
    return WAIT_CHANNEL_MSG


async def handle_forwarded_fsub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle forwarded message for FSub setup."""
    user_id = update.effective_user.id
    
    if not get_admin_check(user_id):
        return ConversationHandler.END
    
    if not update.message.forward_from_chat:
        await update.message.reply_text(
            "❌ <b>Invalid message.</b> Please forward a message from the channel.",
            parse_mode=ParseMode.HTML
        )
        return WAIT_CHANNEL_MSG
    
    channel_id = update.message.forward_from_chat.id
    channel_username = update.message.forward_from_chat.username
    
    # Save FSub configuration
    db.set_fsub_channel(channel_id, channel_username)
    
    # Verify bot is admin in channel
    try:
        bot_member = await context.bot.get_chat_member(channel_id, context.bot.id)
        has_admin = bot_member.status == 'administrator'
    except:
        has_admin = False
    
    config_text = (
        f"✅ <b>FSub Channel Configured!</b>\n\n"
        f"<b>Channel ID:</b> <code>{channel_id}</code>\n"
        f"<b>Channel Username:</b> @{channel_username if channel_username else 'Private'}\n"
        f"<b>Bot Admin Status:</b> {'✅ Yes' if has_admin else '⚠️ Bot is not admin in this channel'}\n"
    )
    
    db.log_activity(user_id, "CONFIGURE_FSUB", str(channel_id))
    
    await update.message.reply_text(config_text, parse_mode=ParseMode.HTML)
    
    return ConversationHandler.END


# ==================== MESSAGE HANDLERS ====================

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle forwarded messages - save media entries."""
    user_id = update.effective_user.id
    
    if not get_admin_check(user_id):
        await update.message.reply_text("❌ Only admins can forward media to save.", parse_mode=ParseMode.HTML)
        return
    
    # Get message text/caption
    text = update.message.text or ""
    caption = update.message.caption or ""
    
    # Parse message for file info
    file_name, file_size, urls = URLParser.parse_message(text, caption)
    
    if not urls:
        await update.message.reply_text(
            "⚠️ <b>No URLs found in this message.</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Determine channel ID
    channel_id = 0
    if update.message.forward_from_chat:
        channel_id = update.message.forward_from_chat.id
    
    # Save to database
    message_id = update.message.message_id
    success = db.save_media_entry(
        message_id=message_id,
        channel_id=channel_id,
        file_name=file_name,
        file_size=file_size,
        caption=caption if caption else None,
        urls=urls
    )
    
    if success:
        response = (
            f"✅ <b>Media Saved Successfully!</b>\n\n"
            f"<b>File Name:</b> {file_name}\n"
            f"<b>File Size:</b> {file_size or 'Not specified'}\n"
            f"<b>URLs Found:</b> {len(urls)}\n"
            f"<b>Message ID:</b> <code>{message_id}</code>\n"
        )
        db.log_activity(user_id, "SAVE_MEDIA", file_name)
    else:
        response = "❌ <b>Failed to save media entry.</b>"
    
    await update.message.reply_text(response, parse_mode=ParseMode.HTML)


# ==================== CALLBACK HANDLERS ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback button presses."""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()  # Remove loading state
    
    if query.data == "check_fsub":
        if await check_fsub(context.application, user_id):
            await query.edit_message_text(
                "✅ <b>Thank you for subscribing!</b>\n"
                "You now have access to all content.",
                parse_mode=ParseMode.HTML
            )
            db.verify_subscription(user_id, FSUB_CHANNEL_ID)
        else:
            await query.edit_message_text(
                "❌ <b>You haven't joined the channel yet.</b>\n"
                "Please join first and then tap 'Check Subscription'.",
                parse_mode=ParseMode.HTML,
                reply_markup=create_fsub_buttons()
            )
    
    elif query.data == "admin_fsub":
        if not get_admin_check(user_id):
            await query.answer("Unauthorized", show_alert=True)
            return
        
        await query.edit_message_text(
            "📋 <b>Setup Force Subscribe</b>\n\n"
            "Forward any message from the channel you want to set as FSub.",
            parse_mode=ParseMode.HTML
        )
        # Note: In production, transition to conversation handler
    
    elif query.data == "admin_verify":
        if not get_admin_check(user_id):
            await query.answer("Unauthorized", show_alert=True)
            return
        
        try:
            me = await context.bot.get_me()
            await query.edit_message_text(
                f"✅ <b>Bot Status: OK</b>\n\n"
                f"<b>Bot Username:</b> @{me.username}\n"
                f"<b>Bot ID:</b> {me.id}\n"
                f"<b>Status:</b> 🟢 Online and responding",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ <b>Error checking bot status:</b>\n{str(e)}",
                parse_mode=ParseMode.HTML
            )
    
    elif query.data == "admin_stats":
        if not get_admin_check(user_id):
            await query.answer("Unauthorized", show_alert=True)
            return
        
        db.update_statistics()
        stats = db.get_statistics()
        
        stats_text = (
            f"<b>📊 Detailed Statistics</b>\n\n"
            f"<b>Media Entries:</b> {stats.get('total_media_entries', 0)}\n"
            f"<b>Unique Users:</b> {stats.get('total_users', 0)}\n"
            f"<b>Total API Calls:</b> {stats.get('total_requests', 0)}\n"
            f"<b>Last Updated:</b> {stats.get('last_updated', 'Never')}\n"
        )
        
        await query.edit_message_text(stats_text, parse_mode=ParseMode.HTML)
    
    elif query.data == "admin_clear_fsub":
        if not get_admin_check(user_id):
            await query.answer("Unauthorized", show_alert=True)
            return
        
        if db.remove_fsub_channel():
            await query.edit_message_text(
                "✅ <b>FSub configuration cleared.</b>",
                parse_mode=ParseMode.HTML
            )
            db.log_activity(user_id, "CLEAR_FSUB", None)
        else:
            await query.edit_message_text(
                "❌ <b>Failed to clear FSub configuration.</b>",
                parse_mode=ParseMode.HTML
            )


# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error(f"Update {update} caused error {context.error}")


# ==================== APPLICATION SETUP ====================

def setup_application() -> Application:
    """Setup and return the Telegram bot application."""
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("latest", latest_command))
    app.add_handler(CommandHandler("admin", admin_command))
    
    # FSub configuration conversation
    fsub_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("configure_fsub", configure_fsub_command)],
        states={
            WAIT_CHANNEL_MSG: [
                MessageHandler(filters.FORWARDED, handle_forwarded_fsub)
            ]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
    )
    app.add_handler(fsub_conv_handler)
    
    # Message handlers
    app.add_handler(MessageHandler(filters.FORWARDED, handle_forwarded_message))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    return app


# ==================== MAIN ====================

def main():
    """Start the bot."""
    logger.info("Starting Media Link Bot...")
    logger.info(f"Admin ID: {ADMIN_ID}")
    logger.info(f"Database: {DATABASE_PATH}")
    logger.info(f"FSub Enabled: {bool(FSUB_CHANNEL_ID)}")
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        raise ValueError("BOT_TOKEN must be set in .env file")
    
    if not ADMIN_ID or ADMIN_ID == 0:
        logger.error("ADMIN_ID not found or invalid in environment variables!")
        raise ValueError("ADMIN_ID must be set in .env file")
    
    app = setup_application()
    
    logger.info("Bot is running. Press Ctrl+C to stop.")
    print(f"\n{'='*50}")
    print(f"🤖 Media Link Bot")
    print(f"{'='*50}")
    print(f"Bot Token: {BOT_TOKEN[:20]}***")
    print(f"Admin ID: {ADMIN_ID}")
    print(f"Database: {DATABASE_PATH}")
    print(f"FSub Channel: {FSUB_CHANNEL_ID or 'Not configured'}")
    print(f"{'='*50}\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
