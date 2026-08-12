"""
Database module for managing SQLite persistence.
Handles saved media entries, Force Subscribe configuration, and logging.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import json

logger = logging.getLogger(__name__)


class Database:
    """SQLite database handler for media bot."""
    
    def __init__(self, db_path: str = "./data/media_bot.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_tables()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_tables(self):
        """Initialize database tables."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Media entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS media_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER UNIQUE,
                    channel_id INTEGER,
                    file_name TEXT NOT NULL,
                    file_size TEXT,
                    caption TEXT,
                    urls TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Force Subscribe configuration
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fsub_config (
                    id INTEGER PRIMARY KEY,
                    channel_id INTEGER UNIQUE,
                    channel_username TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User subscriptions tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_subscriptions (
                    user_id INTEGER PRIMARY KEY,
                    channel_id INTEGER,
                    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified_at TIMESTAMP
                )
            """)
            
            # Bot statistics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id INTEGER PRIMARY KEY,
                    total_media_entries INTEGER DEFAULT 0,
                    total_users INTEGER DEFAULT 0,
                    total_requests INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Activity logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indices for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_id ON media_entries(message_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_channel_id ON media_entries(channel_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_name ON media_entries(file_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON media_entries(created_at)")
            
            conn.commit()
            conn.close()
            logger.info("Database tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database tables: {e}")
            raise
    
    # ==================== MEDIA ENTRIES ====================
    
    def save_media_entry(
        self,
        message_id: int,
        channel_id: int,
        file_name: str,
        file_size: Optional[str],
        caption: Optional[str],
        urls: List[str]
    ) -> bool:
        """
        Save a media entry to database.
        
        Args:
            message_id: Telegram message ID
            channel_id: Source channel ID
            file_name: Name of the file
            file_size: Size of the file (optional)
            caption: Message caption/text
            urls: List of file URLs
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            urls_json = json.dumps(urls)
            
            cursor.execute("""
                INSERT OR REPLACE INTO media_entries 
                (message_id, channel_id, file_name, file_size, caption, urls, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (message_id, channel_id, file_name, file_size, caption, urls_json))
            
            conn.commit()
            conn.close()
            logger.info(f"Saved media entry: {file_name} (msg_id: {message_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error saving media entry: {e}")
            return False
    
    def get_media_entry(self, message_id: int) -> Optional[Dict]:
        """
        Retrieve a media entry by message ID.
        
        Args:
            message_id: Telegram message ID
            
        Returns:
            Dictionary with media entry or None
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM media_entries WHERE message_id = ?
            """, (message_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row['id'],
                    'message_id': row['message_id'],
                    'channel_id': row['channel_id'],
                    'file_name': row['file_name'],
                    'file_size': row['file_size'],
                    'caption': row['caption'],
                    'urls': json.loads(row['urls']),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving media entry: {e}")
            return None
    
    def search_media(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search media entries by file name or caption.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching media entries
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            search_term = f"%{query}%"
            cursor.execute("""
                SELECT * FROM media_entries 
                WHERE file_name LIKE ? OR caption LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (search_term, search_term, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'message_id': row['message_id'],
                    'file_name': row['file_name'],
                    'file_size': row['file_size'],
                    'urls': json.loads(row['urls']),
                    'created_at': row['created_at']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching media: {e}")
            return []
    
    def get_all_media(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        Get all media entries with pagination.
        
        Args:
            limit: Number of entries to return
            offset: Pagination offset
            
        Returns:
            List of media entries
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM media_entries 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'message_id': row['message_id'],
                    'file_name': row['file_name'],
                    'file_size': row['file_size'],
                    'urls': json.loads(row['urls']),
                    'created_at': row['created_at']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving all media: {e}")
            return []
    
    def delete_media_entry(self, message_id: int) -> bool:
        """
        Delete a media entry.
        
        Args:
            message_id: Message ID to delete
            
        Returns:
            True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM media_entries WHERE message_id = ?", (message_id,))
            
            conn.commit()
            conn.close()
            logger.info(f"Deleted media entry: {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting media entry: {e}")
            return False
    
    def get_total_media_count(self) -> int:
        """Get total number of saved media entries."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM media_entries")
            result = cursor.fetchone()
            conn.close()
            
            return result['count'] if result else 0
            
        except Exception as e:
            logger.error(f"Error counting media entries: {e}")
            return 0
    
    # ==================== FORCE SUBSCRIBE ====================
    
    def set_fsub_channel(self, channel_id: int, channel_username: Optional[str] = None) -> bool:
        """
        Set or update Force Subscribe channel.
        
        Args:
            channel_id: Channel ID
            channel_username: Channel username (optional)
            
        Returns:
            True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO fsub_config (channel_id, channel_username)
                VALUES (?, ?)
            """, (channel_id, channel_username))
            
            conn.commit()
            conn.close()
            logger.info(f"FSub channel configured: {channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting FSub channel: {e}")
            return False
    
    def get_fsub_channel(self) -> Optional[Dict]:
        """Get current Force Subscribe channel configuration."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM fsub_config LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'channel_id': row['channel_id'],
                    'channel_username': row['channel_username'],
                    'added_at': row['added_at']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting FSub channel: {e}")
            return None
    
    def remove_fsub_channel(self) -> bool:
        """Remove Force Subscribe configuration."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM fsub_config")
            
            conn.commit()
            conn.close()
            logger.info("FSub channel removed")
            return True
            
        except Exception as e:
            logger.error(f"Error removing FSub channel: {e}")
            return False
    
    # ==================== USER SUBSCRIPTIONS ====================
    
    def verify_subscription(self, user_id: int, channel_id: int) -> bool:
        """
        Mark user as verified subscriber.
        
        Args:
            user_id: User ID
            channel_id: Channel ID
            
        Returns:
            True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_subscriptions 
                (user_id, channel_id, verified_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (user_id, channel_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error verifying subscription: {e}")
            return False
    
    def is_user_subscribed(self, user_id: int, channel_id: int) -> bool:
        """
        Check if user is verified subscriber.
        
        Args:
            user_id: User ID
            channel_id: Channel ID
            
        Returns:
            True if verified
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM user_subscriptions 
                WHERE user_id = ? AND channel_id = ? AND verified_at IS NOT NULL
            """, (user_id, channel_id))
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Error checking subscription: {e}")
            return False
    
    # ==================== ACTIVITY LOGGING ====================
    
    def log_activity(self, user_id: int, action: str, details: Optional[str] = None) -> bool:
        """
        Log user activity.
        
        Args:
            user_id: User ID
            action: Action type
            details: Additional details
            
        Returns:
            True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO activity_logs (user_id, action, details)
                VALUES (?, ?, ?)
            """, (user_id, action, details))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            return False
    
    # ==================== STATISTICS ====================
    
    def update_statistics(self) -> bool:
        """Update bot statistics."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(DISTINCT user_id) as count FROM activity_logs")
            total_users = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM media_entries")
            total_media = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM activity_logs")
            total_requests = cursor.fetchone()['count']
            
            cursor.execute("""
                INSERT OR REPLACE INTO bot_stats 
                (id, total_media_entries, total_users, total_requests, last_updated)
                VALUES (1, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (total_media, total_users, total_requests))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get bot statistics."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM bot_stats WHERE id = 1")
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'total_media_entries': row['total_media_entries'],
                    'total_users': row['total_users'],
                    'total_requests': row['total_requests'],
                    'last_updated': row['last_updated']
                }
            
            return {
                'total_media_entries': 0,
                'total_users': 0,
                'total_requests': 0,
                'last_updated': None
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
