# 📖 Complete Command Reference

All available commands for Media Link Bot.

---

## 👥 General Commands (Everyone)

### `/start`

**Description:** Welcome message and quick start guide

**Usage:**
```
/start
```

**Response:**
```
🤖 Welcome to Media Link Bot!

Bot made by @Franited
Powered by @Dokjaxvibe

Available Commands:
/help - Show all available commands
/search - Search saved media
/latest - View latest media entries
/stats - View bot statistics
/about - About this bot

For Admins:
/admin - Admin control panel
```

---

### `/help`

**Description:** Show all available commands

**Usage:**
```
/help
```

**Response:**
```
📖 Help - Available Commands

General Commands:
/start - Welcome message
/help - Show this message
/about - Bot information
/stats - View statistics

Search Commands:
/search <query> - Search media by name
/latest - View 10 latest entries

Admin Commands: (admin only)
/admin - Open admin panel
/configure_fsub - Setup Force Subscribe
/verify_bot - Check bot permissions
/stats_detailed - Full statistics
/clear_fsub - Remove FSub configuration
```

---

### `/about`

**Description:** Bot information and credits

**Usage:**
```
/about
```

**Response:**
```
📱 About This Bot

Purpose:
Manage and distribute media/file links with Force Subscribe support.

Features:
✅ Save and organize media links
✅ Search saved media
✅ Force Subscribe verification
✅ Admin control panel
✅ Activity logging
✅ Statistics tracking

Bot Creator: @Franited
Powered by: @Dokjaxvibe
```

---

### `/stats`

**Description:** View bot statistics

**Usage:**
```
/stats
```

**Response:**
```
📊 Bot Statistics

Media Entries: 15
Total Users: 8
Total Requests: 42
```

---

### `/search <query>`

**Description:** Search saved media by file name or caption

**Usage:**
```
/search Avengers
/search Avengers 1080p
/search movie 2024
```

**Example Response:**
```
🔍 Search Results for: Avengers

1. Avengers Endgame 2019
   Size: 2.5 GB

2. Avengers Infinity War 2018
   Size: 1.8 GB

3. Avengers Age of Ultron 2015
   Size: 1.2 GB
```

**Notes:**
- Search is case-insensitive
- Returns up to 20 results
- Searches both file name and description
- Requires user to pass FSub check (if enabled)

---

### `/latest`

**Description:** View 10 most recently added media entries

**Usage:**
```
/latest
```

**Example Response:**
```
📋 Latest Media Entries

1. New Action Movie 2024
   Size: 2.1 GB

2. Comedy Special 2024
   Size: 1.5 GB

3. Documentary Series
   Size: 3.2 GB
```

**Notes:**
- Shows most recent 10 entries
- Sorted by upload date (newest first)
- Requires FSub verification (if enabled)

---

## 👑 Admin Commands (Admin Only)

### `/admin`

**Description:** Open admin control panel with quick actions

**Usage:**
```
/admin
```

**Response:**
```
⚙️ Admin Control Panel

📊 Statistics:
  • Media Entries: 42
  • FSub Channel: ✅ Configured

🔧 Admin Options:
[Configure FSub]  [Verify Bot]  [Detailed Stats]  [Clear FSub]
```

**Buttons Available:**
- 🔗 Configure FSub
- ✅ Verify Bot Permissions
- 📊 Detailed Stats
- 🗑️ Clear FSub

---

### `/configure_fsub`

**Description:** Setup Force Subscribe channel

**Usage:**
```
/configure_fsub
```

**Instructions:**
1. Send `/configure_fsub`
2. Bot asks: "Please forward any message from the channel"
3. Forward a message from your channel to the bot
4. Bot confirms setup and verifies admin status

**Example Flow:**
```
You:  /configure_fsub
Bot:  📋 Force Subscribe Setup
      Please forward any message from the channel you want to set as FSub channel.
      The bot will automatically detect the channel ID.

You:  [Forward message from @yourchannel]

Bot:  ✅ FSub Channel Configured!
      Channel ID: -100123456789
      Channel Username: @yourchannel
      Bot Admin Status: ✅ Yes
```

**Notes:**
- Only admin can use this command
- Bot must be admin in the target channel
- Replaces previous FSub channel if one was set
- Users will be required to join after setup

---

### `/verify_bot`

**Description:** Verify bot status and permissions

**Usage:**
```
/verify_bot
```

**Response:**
```
✅ Bot Status: OK

Bot Username: @your_media_bot
Bot ID: 987654321
Status: 🟢 Online and responding
```

**Checks:**
- ✅ Bot token validity
- ✅ Bot connectivity
- ✅ API response time
- ✅ Database connection

---

### `/stats_detailed`

**Description:** View detailed bot statistics and analytics

**Usage:**
```
/stats_detailed
```

**Response:**
```
📊 Detailed Statistics

Media Entries: 42
Unique Users: 15
Total API Calls: 189
Last Updated: 2024-08-12 14:30:00
```

**Tracked Metrics:**
- Total media entries saved
- Unique users who interacted
- Total bot API calls made
- Last statistics update time

---

### `/clear_fsub`

**Description:** Remove Force Subscribe configuration

**Usage:**
```
/clear_fsub
```

**Response:**
```
✅ FSub configuration cleared.

Users will no longer need to join the channel.
```

**Notes:**
- Removes FSub requirement
- Already verified users' status is kept in database
- Can reconfigure FSub anytime with `/configure_fsub`

---

## 💬 Message Handling

### Forwarding Messages to Save Media

**Description:** Forward or send messages containing file links to save them

**Format:**
```
[File Name] [Size in brackets]
[URL 1]
[URL 2]
[Optional caption/description]
```

**Example:**
```
Avengers Endgame 2019 [2.5 GB]
https://example.com/download/avengers1
https://example.com/download/avengers2

High quality 1080p release with dual audio
```

**Bot Response:**
```
✅ Media Saved Successfully!

File Name: Avengers Endgame 2019
File Size: 2.5 GB
URLs Found: 2
Message ID: 12345
```

**What Gets Saved:**
- ✅ File name (auto-detected)
- ✅ File size (if included)
- ✅ All URLs (HTTP/HTTPS)
- ✅ Message caption/description
- ✅ Timestamp
- ✅ Source channel info

---

## 🔘 Inline Buttons

### Link Access Buttons

When a media link is requested, bot provides clickable buttons:

```
📁 Movie Title
📊 Size: 2.5 GB

🔗 Available Links:
[📥 Link 1]  [📥 Link 2]  [📥 Link 3]
[📄 More Links]
```

**Button Actions:**
- 📥 Link buttons → Open URL directly
- 📄 More Links → Show all URLs in message
- 🔄 Check Subscription → Verify FSub status
- ✅ Join Channel → Follow FSub channel

---

## 🔄 Callback Actions (Buttons)

### Check Subscription

**Triggered by:** "Check Subscription" button in FSub messages

**Action:** Bot verifies if user is member of FSub channel

**Response Options:**
```
✅ Thank you for subscribing!
You now have access to all content.
```

OR

```
❌ You haven't joined the channel yet.
Please join first and then tap 'Check Subscription'.
```

---

## ⚙️ Admin Panel Interactions

### Configure FSub (Button)

**Button:** 🔗 Configure FSub  
**Action:** Start FSub configuration process

---

### Verify Bot (Button)

**Button:** ✅ Verify Bot Permissions  
**Action:** Check bot status and permissions

---

### Detailed Stats (Button)

**Button:** 📊 Detailed Stats  
**Action:** Show analytics dashboard

---

### Clear FSub (Button)

**Button:** 🗑️ Clear FSub  
**Action:** Remove FSub configuration (requires confirmation)

---

## 📊 Activity Logging

Bot logs all actions for auditing:

**Logged Actions:**
- `/start` - User started bot
- `/help` - User requested help
- `/about` - User viewed about
- `/stats` - User requested stats
- `/search <query>` - Search performed
- `/latest` - Latest viewed
- `SAVE_MEDIA` - Admin saved media
- `CONFIGURE_FSUB` - FSub configured
- `CLEAR_FSUB` - FSub cleared

View logs:
```bash
tail -f logs/bot.log
```

---

## 🔐 Permission Model

### General Users
Can use:
- /start
- /help
- /about
- /stats
- /search
- /latest

### Admin (ADMIN_ID only)
Can additionally use:
- /admin
- /configure_fsub
- /verify_bot
- /stats_detailed
- /clear_fsub
- Forward/save media entries

---

## 🚨 Error Messages & Solutions

### "❌ Unauthorized. This command is for admins only."
**Cause:** Non-admin tried admin command  
**Solution:** Only ADMIN_ID can use admin commands

### "❌ Please provide a search query."
**Cause:** `/search` without a query term  
**Solution:** Use `/search <something>`

### "❌ No results found for: ..."
**Cause:** No media saved matching search  
**Solution:** Admin needs to save media first

### "❌ You must join our channel first."
**Cause:** FSub configured and user not member  
**Solution:** Click "Join Channel" button and verify

### "⚠️ No URLs found in this message."
**Cause:** Message forwarded has no links  
**Solution:** Forward message with HTTP/HTTPS URLs

---

## 💡 Command Tips & Tricks

### Searching
```bash
# Exact match
/search "Exact Title"

# Partial match (default)
/search movie

# Multiple terms
/search movie 1080p
```

### Saving Media
```bash
# Minimal format (just URLs)
https://example.com/file1
https://example.com/file2

# Full format (recommended)
Movie Name [Size]
https://example.com/file1
https://example.com/file2
Optional description here
```

### Admin Tasks
```bash
# View all recent activity
/stats_detailed

# Verify everything is working
/verify_bot

# Check search functionality
/search test
```

---

## 📞 Support

For command issues or questions:
- Contact: [@Franited](https://t.me/Franited)
- Check logs: `logs/bot.log`
- Review guide: `README.md`

---

**Last Updated:** August 2024  
**Version:** 1.0  
**Bot Creator:** @Franited
