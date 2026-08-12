"""
Enhanced Database Module for Media Link Bot
Supports: Media entries, Scraped links, Admin management, Activity logs
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class EnhancedDatabase:
    def __init__(self, db_path: str = './data/media_bot.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize all database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Media Entries Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS media_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER UNIQUE,
                    channel_id INTEGER,
                    file_name TEXT,
                    file_size TEXT,
                    caption TEXT,
                    urls TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Scraped Links Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraped_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    title TEXT,
                    media_type TEXT,
                    description TEXT,
                    file_size TEXT,
                    scraped_at TIMESTAMP,
                    added_to_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Admin Users Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    admin_id INTEGER PRIMARY KEY,
                    username TEXT,
                    added_by INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # FSub Configuration
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fsub_config (
                    channel_id INTEGER PRIMARY KEY,
                    channel_username TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User Subscriptions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    channel_id INTEGER,
                    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Activity Logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Bot Statistics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_media_entries INTEGER,
                    total_scraped_links INTEGER,
                    total_users INTEGER,
                    total_requests INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Scraping Jobs Log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraping_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_type TEXT,
                    url TEXT,
                    status TEXT,
                    links_found INTEGER DEFAULT 0,
                    media_found INTEGER DEFAULT 0,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
        
        finally:
            conn.close()
    
    def add_media_entry(self, message_id: int, channel_id: int, file_name: str, 
                       file_size: str, caption: str, urls: List[str]) -> bool:
        """Add media entry to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO media_entries 
                (message_id, channel_id, file_name, file_size, caption, urls)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                message_id,
                channel_id,
                file_name,
                file_size,
                caption,
                json.dumps(urls)
            ))
            conn.commit()
            logger.info(f"Added media entry: {file_name}")
            return True
        
        except sqlite3.IntegrityError:
            logger.warning(f"Media entry {message_id} already exists")
            return False
        
        except Exception as e:
            logger.error(f"Error adding media entry: {e}")
            return False
        
        finally:
            conn.close()
    
    def search_media(self, query: str) -> List[Dict]:
        """Search media by name or caption"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM media_entries
                WHERE file_name LIKE ? OR caption LIKE ?
                ORDER BY created_at DESC
                LIMIT 20
            ''', (f'%{query}%', f'%{query}%'))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'message_id': row[1],
                    'channel_id': row[2],
                    'file_name': row[3],
                    'file_size': row[4],
                    'caption': row[5],
                    'urls': row[6],
                    'created_at': row[7]
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching media: {e}")
            return []
        
        finally:
            conn.close()
    
    def add_scraped_link(self, url: str, title: str, media_type: str = 'link',
                        description: str = '', file_size: str = '') -> bool:
        """Add scraped link to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO scraped_links 
                (url, title, media_type, description, file_size, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                url,
                title,
                media_type,
                description,
                file_size,
                datetime.now()
            ))
            conn.commit()
            return True
        
        except sqlite3.IntegrityError:
            logger.debug(f"Link {url} already exists")
            return False
        
        except Exception as e:
            logger.error(f"Error adding scraped link: {e}")
            return False
        
        finally:
            conn.close()
    
    def bulk_add_scraped_links(self, links: List[Dict]) -> int:
        """Add multiple scraped links at once"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        added_count = 0
        
        try:
            for link in links:
                try:
                    cursor.execute('''
                        INSERT INTO scraped_links 
                        (url, title, media_type, description, file_size, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        link.get('url'),
                        link.get('title', ''),
                        link.get('media_type', 'link'),
                        link.get('description', ''),
                        link.get('file_size', ''),
                        datetime.now()
                    ))
                    added_count += 1
                except sqlite3.IntegrityError:
                    pass  # Link already exists
            
            conn.commit()
            logger.info(f"Added {added_count} scraped links")
            return added_count
        
        except Exception as e:
            logger.error(f"Error bulk adding scraped links: {e}")
            return added_count
        
        finally:
            conn.close()
    
    def search_scraped_links(self, query: str, limit: int = 10) -> List[Dict]:
        """Search scraped links"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM scraped_links
                WHERE title LIKE ? OR description LIKE ? OR url LIKE ?
                ORDER BY added_to_db DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'url': row[1],
                    'title': row[2],
                    'media_type': row[3],
                    'description': row[4],
                    'file_size': row[5],
                    'added_at': row[7]
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching scraped links: {e}")
            return []
        
        finally:
            conn.close()
    
    def add_admin(self, admin_id: int, username: str = '', added_by: int = 0) -> bool:
        """Add admin to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO admins (admin_id, username, added_by)
                VALUES (?, ?, ?)
            ''', (admin_id, username, added_by))
            conn.commit()
            logger.info(f"Admin {admin_id} added/updated")
            return True
        
        except Exception as e:
            logger.error(f"Error adding admin: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_all_admins(self) -> List[Dict]:
        """Get all admin users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM admins ORDER BY added_at DESC')
            results = []
            for row in cursor.fetchall():
                results.append({
                    'admin_id': row[0],
                    'username': row[1],
                    'added_by': row[2],
                    'added_at': row[3]
                })
            return results
        
        except Exception as e:
            logger.error(f"Error fetching admins: {e}")
            return []
        
        finally:
            conn.close()
    
    def log_activity(self, user_id: int, action: str, details: str = '') -> bool:
        """Log user activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO activity_logs (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (user_id, action, details))
            conn.commit()
            return True
        
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            return False
        
        finally:
            conn.close()
    
    def log_scraping_job(self, job_type: str, url: str, status: str,
                        links_found: int = 0, media_found: int = 0,
                        error_message: str = '') -> bool:
        """Log scraping job"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO scraping_jobs 
                (job_type, url, status, links_found, media_found, started_at, completed_at, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_type,
                url,
                status,
                links_found,
                media_found,
                datetime.now(),
                datetime.now() if status == 'completed' else None,
                error_message
            ))
            conn.commit()
            return True
        
        except Exception as e:
            logger.error(f"Error logging scraping job: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_statistics(self) -> Dict:
        """Get bot statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM media_entries')
            media_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM scraped_links')
            scraped_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT user_id) FROM activity_logs')
            unique_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM activity_logs')
            total_actions = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM admins')
            admin_count = cursor.fetchone()[0]
            
            return {
                'media_entries': media_count,
                'scraped_links': scraped_count,
                'unique_users': unique_users,
                'total_actions': total_actions,
                'total_admins': admin_count,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
        
        finally:
            conn.close()
    
    def get_latest_entries(self, limit: int = 10) -> List[Dict]:
        """Get latest media entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM media_entries
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'file_name': row[3],
                    'file_size': row[4],
                    'created_at': row[7]
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Error getting latest entries: {e}")
            return []
        
        finally:
            conn.close()
    
    def cleanup_old_scraped_links(self, days: int = 30) -> int:
        """Delete scraped links older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM scraped_links
                WHERE datetime(added_to_db) < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            deleted = cursor.rowcount
            conn.commit()
            logger.info(f"Deleted {deleted} old scraped links")
            return deleted
        
        except Exception as e:
            logger.error(f"Error cleaning up old links: {e}")
            return 0
        
        finally:
            conn.close()
