# ⚙️ Advanced Configuration Guide

This guide is for advanced users who want to customize the bot further.

---

## 📋 Table of Contents

1. [Database Customization](#database-customization)
2. [Logging Configuration](#logging-configuration)
3. [Performance Tuning](#performance-tuning)
4. [Docker Deployment](#docker-deployment)
5. [Environment Variables Reference](#environment-variables-reference)
6. [Database Maintenance](#database-maintenance)
7. [Security Hardening](#security-hardening)

---

## Database Customization

### Using Different Database Path

By default, database is stored at `./data/media_bot.db`. To change:

```env
DATABASE_PATH=/var/lib/media-bot/media_bot.db
```

### Database Backup

**Manual Backup:**

```bash
# Simple copy
cp data/media_bot.db data/media_bot.db.backup

# With timestamp
cp data/media_bot.db "data/media_bot.db.$(date +%Y%m%d_%H%M%S).backup"
```

**Automated Backup (via cron):**

```bash
# Edit crontab
crontab -e

# Add this line (backup daily at 2 AM)
0 2 * * * cp /root/media-bot/data/media_bot.db "/root/media-bot/backups/media_bot.db.$(date +\%Y\%m\%d)"
```

### Database Optimization

**Vacuum database (removes fragmentation):**

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('data/media_bot.db')
conn.execute('VACUUM')
conn.close()
print('Database vacuumed successfully')
"
```

**Check database size:**

```bash
du -sh data/media_bot.db
```

**Create database indices for faster searching:**

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('data/media_bot.db')
cursor = conn.cursor()

# Create indices
cursor.execute('CREATE INDEX IF NOT EXISTS idx_msg_id ON media_entries(message_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_channel ON media_entries(channel_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_filename ON media_entries(file_name)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_created ON media_entries(created_at)')

conn.commit()
conn.close()
print('Indices created')
"
```

---

## Logging Configuration

### Log Levels

Available levels (from verbose to minimal):

```env
LOG_LEVEL=DEBUG      # Most detailed
LOG_LEVEL=INFO       # Standard (recommended)
LOG_LEVEL=WARNING    # Only warnings and errors
LOG_LEVEL=ERROR      # Only errors
```

### Log File Location

Change where logs are stored:

```env
LOG_FILE=/var/log/media-bot/bot.log
```

Make sure directory exists:

```bash
sudo mkdir -p /var/log/media-bot
sudo chmod 755 /var/log/media-bot
```

### Log Rotation

**Using logrotate (Linux):**

```bash
sudo nano /etc/logrotate.d/media-bot
```

Add content:

```
/var/log/media-bot/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
    sharedscripts
}
```

### View Logs

```bash
# Real-time logs
tail -f logs/bot.log

# Last 50 lines
tail -n 50 logs/bot.log

# Search logs
grep "ERROR" logs/bot.log

# Filter by time (last 2 hours)
grep "$(date -d '2 hours ago' '+%Y-%m-%d')" logs/bot.log
```

---

## Performance Tuning

### Database Query Optimization

For large databases with many entries, use pagination:

```python
# Instead of loading all entries
results = db.get_all_media(limit=50, offset=0)

# Then for next page
results = db.get_all_media(limit=50, offset=50)
```

### Search Performance

Search limited to most recent entries:

```bash
# Modify in url_parser.py or bot.py to limit search scope
def search_media_recent(query: str, days: int = 30):
    # Search only entries from last 30 days
    pass
```

### Memory Management

**Monitor memory usage:**

```bash
# On VPS
free -h

# Python process memory
ps aux | grep bot.py
```

**Limit memory in systemd service:**

```ini
[Service]
MemoryLimit=512M
MemoryMax=1G
```

### Database Connection Pooling

For high-traffic bots, consider connection pooling (advanced):

```python
# SQLite doesn't benefit much from pooling
# But you can reuse connections in Database class
```

---

## Docker Deployment

### Build Docker Image

```bash
docker build -t media-bot:latest .
```

### Run with Docker

**Simple run:**

```bash
docker run \
  -e BOT_TOKEN="your_token" \
  -e ADMIN_ID="your_id" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  media-bot:latest
```

**With Docker Compose:**

```bash
docker-compose up -d
```

### Docker Commands

```bash
# View running containers
docker ps

# View logs
docker logs media-link-bot -f

# Stop bot
docker stop media-link-bot

# Start bot
docker start media-link-bot

# Restart bot
docker restart media-link-bot

# Remove container
docker rm media-link-bot

# View resource usage
docker stats media-link-bot
```

### Docker Network Configuration

For multiple services, create custom network:

```bash
docker network create bot-network

docker run \
  --network bot-network \
  --name media-bot \
  media-bot:latest
```

---

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | `123456:ABCabc...` |
| `ADMIN_ID` | Admin user Telegram ID | `123456789` |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DATABASE_PATH` | SQLite database location | `./data/media_bot.db` | `/var/db/media.db` |
| `LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `WARNING`, `ERROR` |
| `LOG_FILE` | Log file location | `./logs/bot.log` | `/var/log/media-bot.log` |
| `FSUB_CHANNEL_ID` | Force Subscribe channel | (disabled) | `-100123456789` |
| `BOT_MADE_BY` | Bot creator attribution | `@Franited` | `@YourName` |
| `POWERED_BY` | Bot powered by attribution | `@Dokjaxvibe` | `@YourHandle` |

### Complete .env Example

```env
# Required
BOT_TOKEN=123456789:ABCDEfghijklmnopqrstuvwxyz1234567890
ADMIN_ID=987654321

# Optional - Database
DATABASE_PATH=./data/media_bot.db

# Optional - Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/bot.log

# Optional - Force Subscribe
FSUB_CHANNEL_ID=-100123456789

# Optional - Attribution
BOT_MADE_BY=@Franited
POWERED_BY=@Dokjaxvibe
```

---

## Database Maintenance

### Clear Old Entries

**Manually delete entries older than 30 days:**

```python
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('data/media_bot.db')
cursor = conn.cursor()

# Calculate date 30 days ago
cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()

# Delete old entries
cursor.execute(
    "DELETE FROM media_entries WHERE created_at < ?",
    (cutoff_date,)
)

conn.commit()
deleted = cursor.rowcount
conn.close()

print(f"Deleted {deleted} old entries")
```

### Export Database

**Export to JSON:**

```bash
python3 << 'EOF'
import sqlite3
import json

conn = sqlite3.connect('data/media_bot.db')
cursor = conn.cursor()

# Get all entries
cursor.execute("SELECT * FROM media_entries")
columns = [description[0] for description in cursor.description]
rows = cursor.fetchall()

# Convert to list of dicts
data = []
for row in rows:
    data.append(dict(zip(columns, row)))

# Save to JSON
with open('backup.json', 'w') as f:
    json.dump(data, f, indent=2, default=str)

conn.close()
print(f"Exported {len(data)} entries to backup.json")
EOF
```

**Export to CSV:**

```bash
python3 << 'EOF'
import sqlite3
import csv

conn = sqlite3.connect('data/media_bot.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM media_entries")
columns = [description[0] for description in cursor.description]
rows = cursor.fetchall()

# Write to CSV
with open('backup.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    writer.writerows(rows)

conn.close()
print(f"Exported to backup.csv")
EOF
```

### Database Statistics

**Get database statistics:**

```bash
python3 << 'EOF'
import sqlite3
import os

db_path = 'data/media_bot.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get counts
cursor.execute("SELECT COUNT(*) FROM media_entries")
media_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT user_id) FROM activity_logs")
user_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM activity_logs")
log_count = cursor.fetchone()[0]

# Get file size
db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB

conn.close()

print(f"Database: {db_path}")
print(f"Size: {db_size:.2f} MB")
print(f"Media Entries: {media_count}")
print(f"Unique Users: {user_count}")
print(f"Activity Logs: {log_count}")
EOF
```

---

## Security Hardening

### File Permissions

**Restrict .env file permissions:**

```bash
chmod 600 .env
chmod 700 data/
chmod 700 logs/
```

**Verify permissions:**

```bash
ls -la .env
ls -la data/
ls -la logs/
```

### Database Encryption

**Encrypt sensitive data in transit:**

Use HTTPS for all URLs stored in database. Validate:

```bash
python3 << 'EOF'
import sqlite3
import re

conn = sqlite3.connect('data/media_bot.db')
cursor = conn.cursor()

cursor.execute("SELECT id, urls FROM media_entries")
rows = cursor.fetchall()

https_count = 0
http_count = 0

for row_id, urls_json in rows:
    if urls_json.startswith('http://'):
        http_count += 1

print(f"HTTPS URLs: {https_count}")
print(f"HTTP URLs (insecure): {http_count}")

if http_count > 0:
    print("⚠️ Warning: Some URLs are using HTTP instead of HTTPS!")

conn.close()
EOF
```

### User Input Sanitization

All user inputs are validated, but you can add custom validation:

```python
def validate_input(user_input: str) -> bool:
    """Add custom input validation"""
    # Block common SQL injection patterns
    dangerous_patterns = ['DROP', 'DELETE', 'UNION', ';--']
    
    for pattern in dangerous_patterns:
        if pattern.upper() in user_input.upper():
            return False
    
    return True
```

### Rate Limiting

**Add rate limiting to prevent abuse:**

```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests=5, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    def is_rate_limited(self, user_id):
        now = time.time()
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.time_window
        ]
        
        if len(self.requests[user_id]) >= self.max_requests:
            return True
        
        self.requests[user_id].append(now)
        return False
```

### Secret Management

**For production, use environment-only secrets:**

```bash
# Never print secrets in logs
echo "Bot token is configured ✓"

# Use masking in output
BOT_TOKEN_MASKED="${BOT_TOKEN:0:10}***"
echo "Using token: $BOT_TOKEN_MASKED"
```

### Audit Logging

**All actions are logged:**

```bash
# View admin actions
grep "admin\|CONFIGURE\|CLEAR" logs/bot.log

# View save operations
grep "SAVE_MEDIA" logs/bot.log

# View searches
grep "SEARCH" logs/bot.log
```

---

## Performance Benchmarks

### Expected Performance

- **Search response time:** < 500ms (for 1000s entries)
- **Media save time:** < 1 second
- **Database size:** ~1KB per media entry
- **Memory usage:** 50-100MB base + 10MB per 1000 concurrent users

### Stress Testing

```bash
# Simple load test (create many entries)
python3 << 'EOF'
import sqlite3
import time
from datetime import datetime

conn = sqlite3.connect('data/media_bot.db')
cursor = conn.cursor()

start = time.time()

for i in range(1000):
    cursor.execute("""
        INSERT INTO media_entries 
        (message_id, channel_id, file_name, file_size, urls)
        VALUES (?, ?, ?, ?, ?)
    """, (
        i,
        -100123,
        f"Test File {i}",
        f"{i} MB",
        '["https://example.com/file"]'
    ))

conn.commit()
elapsed = time.time() - start

print(f"Inserted 1000 entries in {elapsed:.2f} seconds")
print(f"Average: {1000/elapsed:.0f} entries/second")

conn.close()
EOF
```

---

## Troubleshooting Advanced Issues

### High Memory Usage

```bash
# Check what's consuming memory
top -p $(pgrep -f "python bot.py")

# Kill and restart
pkill -f "python bot.py"
sleep 2
python bot.py &
```

### Slow Searches

```bash
# Check if indices exist
sqlite3 data/media_bot.db ".indices"

# Recreate indices if missing
python3 -c "
import sqlite3
conn = sqlite3.connect('data/media_bot.db')
cursor = conn.cursor()
cursor.execute('REINDEX')
conn.commit()
conn.close()
print('Reindexed database')
"
```

### Database Corruption

```bash
# Check database integrity
sqlite3 data/media_bot.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
cp data/media_bot.db.backup data/media_bot.db
```

---

## Monitoring

### Health Check Script

```bash
#!/bin/bash
BOT_PID=$(pgrep -f "python bot.py")

if [ -z "$BOT_PID" ]; then
    echo "Bot is NOT running!"
    exit 1
else
    echo "Bot is running (PID: $BOT_PID)"
    exit 0
fi
```

### Alert Setup (using systemd)

```ini
[Unit]
OnFailure=send-email@%n.service
```

---

This guide covers advanced configuration. For basic setup, see **SETUP_GUIDE.md**.

**Questions?** Contact [@Franited](https://t.me/Franited)
