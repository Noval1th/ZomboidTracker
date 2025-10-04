# Project Zomboid Stats Tracker

Automatically track player deaths, respawns, skill progression, and survival stats on your Project Zomboid server with comprehensive Discord notifications and leaderboards!

![Discord](https://img.shields.io/badge/Discord-Webhook-7289DA?style=for-the-badge&logo=discord&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
[![Twitter](https://img.shields.io/badge/Twitter-@n0valith-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://x.com/n0valith)

---

## ✨ Features

### 📊 **Comprehensive Stat Tracking**
- 💀 **Death notifications** with survival time, coordinates, and peak skills
- 🔄 **Respawn tracking** with character numbers and death counts
- 📈 **Skill progression** with configurable level-up notifications
- 👤 **Complete player profiles** tracking all stats across multiple lives

### 🏆 **Multiple Leaderboards**
- **Death Leaderboard** - Most deaths with average survival time
- **Survival Leaderboard** - Longest single survival streaks
- **Total Hours Leaderboard** - Most experienced players (lifetime hours)
- **Skill Leaderboards** - Top players for each skill (weekly)

### ⚙️ **Smart Automation**
- 🕐 **Scheduled leaderboards** - Daily at noon & midnight, weekly skill boards on Sundays
- 🎮 **Activity-based updates** - Automatic leaderboards during active play sessions
- 💾 **Persistent tracking** - All stats survive server restarts
- 🔄 **Real-time monitoring** - Events detected within 30 seconds

### 🎨 **Rich Discord Integration**
- Color-coded embeds based on death count
- Progressive death emojis (💀 → ☠️ → ⚰️ → 👻 → 🏴‍☠️)
- Readable time formatting (X days, Y hours)
- Live status indicators (🟢 for currently alive players)

---

## 📋 Requirements

- Project Zomboid server with FTP access (tested on G-Portal)
- Discord server with webhook permissions
- Python 3.8 or higher installed
- Windows, Linux, or Mac computer

---

## 🚀 Quick Start

### 1. Install Python

**Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer and **CHECK** "Add Python to PATH"
3. Verify: Open Command Prompt and type `python --version`

**Mac:**
```bash
brew install python3
```

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Download This Repository

**Option A: Using Git**
```bash
git clone https://github.com/yourusername/zomboid-stats-tracker.git
cd zomboid-stats-tracker
```

**Option B: Manual Download**
1. Click the green **"Code"** button at the top of this page
2. Click **"Download ZIP"**
3. Extract to a folder you'll remember (e.g., `C:\zomboid-tracker\`)

### 3. Install Dependencies

Open terminal/command prompt in the project folder:

```bash
pip install -r requirements.txt
```

### 4. Get Your Discord Webhook

1. Go to your Discord server → **Server Settings** → **Integrations** → **Webhooks**
2. Click **"Create Webhook"**
3. Set the name and channel where you want notifications
4. Click **"Copy Webhook URL"** and save it

### 5. Get Your Server's FTP Credentials

**For G-Portal:**
1. Go to your server dashboard
2. In the status page, scroll down to "Access"
3. Copy the Host, Port, Username, and Password

**For Other Hosts:**
- Check your hosting provider's control panel
- Usually in "File Management" or "Advanced" sections

### 6. Set Up Configuration Files

**Windows:**

Create a file called `start_monitor.bat` in the project folder:

```batch
@echo off

REM ===== REQUIRED SETTINGS =====
set DISCORD_WEBHOOK_URL=your_webhook_url_here
set FTP_HOST=your_ftp_host_here
set FTP_PORT=your_ftp_port_here
set FTP_USER=your_ftp_username_here
set FTP_PASS=your_ftp_password_here

REM ===== OPTIONAL SETTINGS =====
set LOG_BASE_PATH=/Logs
set CHECK_INTERVAL=30
set SKILL_NOTIFICATIONS=milestones

pythonw main.py
```

**Then create** `start_monitor_hidden.vbs` (this runs without a console window):

```vbscript
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c start_monitor.bat", 0, False
Set WshShell = Nothing
```

Replace all `your_*_here` values with your actual credentials.

**Mac/Linux:**

Create `start_monitor.sh`:

```bash
#!/bin/bash
export DISCORD_WEBHOOK_URL="your_webhook_url_here"
export FTP_HOST="your_ftp_host_here"
export FTP_PORT="your_ftp_port_here"
export FTP_USER="your_ftp_username_here"
export FTP_PASS="your_ftp_password_here"
export LOG_BASE_PATH="/Logs"
export CHECK_INTERVAL="30"
export SKILL_NOTIFICATIONS="milestones"

python3 main.py
```

Make it executable:
```bash
chmod +x start_monitor.sh
```

### 7. Test It!

**Windows:** Double-click `start_monitor_hidden.vbs`  
**Mac/Linux:** Run `./start_monitor.sh`

Check Task Manager (Windows) or Activity Monitor (Mac) for `pythonw.exe` or `python` to verify it's running.

Have someone die, respawn, or level up in your server to test notifications!

---

## ⚙️ Configuration Options

### Environment Variables Explained

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_WEBHOOK_URL` | ✅ Yes | - | Your Discord webhook URL |
| `FTP_HOST` | ✅ Yes | - | Your server's FTP hostname |
| `FTP_PORT` | ✅ Yes | - | FTP port number |
| `FTP_USER` | ✅ Yes | - | FTP username |
| `FTP_PASS` | ✅ Yes | - | FTP password |
| `LOG_BASE_PATH` | ❌ No | `/Logs` | Base path to server logs |
| `CHECK_INTERVAL` | ❌ No | `30` | Seconds between checks |
| `SKILL_NOTIFICATIONS` | ❌ No | `milestones` | Skill notification mode |

### CHECK_INTERVAL Options

Controls how often the bot checks for new events:

| Value | Speed | Bandwidth | Best For |
|-------|-------|-----------|----------|
| `15` | Very fast | Higher | Active servers with frequent events |
| `30` | Fast | Normal | **Recommended - balanced** |
| `60` | Normal | Lower | Quieter servers |
| `120` | Slow | Minimal | Very quiet servers |

### SKILL_NOTIFICATIONS Options

Controls when skill level-ups trigger Discord notifications:

#### `milestones` ⭐ **Recommended**
- Notifies only at levels 5 and 10
- Celebrates meaningful achievements without spam
- Best for most servers

**Example:**
```
🎉 xCATZx leveled up!
Aiming reached level 5
⏱️ After 12 hours survived
```

#### `all`
- Notifies for EVERY skill level-up (1, 2, 3, 4, 5...)
- Very detailed but can be extremely spammy
- Best for small servers (1-3 players) who want to see everything

#### `none`
- No skill notifications at all
- Only deaths and respawns
- Best for servers wanting minimal notifications

---

## 🖥️ Auto-Start on PC Boot

### Windows - Using Task Scheduler

1. **Open Task Scheduler**
   - Press `Win + R`, type `taskschd.msc`, press Enter

2. **Create a New Task**
   - Click **"Create Task..."** (NOT "Create Basic Task")
   - Name it: `Zomboid Stats Tracker`
   - Check **"Run whether user is logged on or not"**
   - Check **"Run with highest privileges"**

3. **Triggers Tab**
   - Click **"New..."**
   - Begin the task: **"At startup"**
   - Click **OK**

4. **Actions Tab**
   - Click **"New..."**
   - Action: **"Start a program"**
   - Program/script: Browse to your `start_monitor_hidden.vbs` file
     - Example: `C:\zomboid-tracker\start_monitor_hidden.vbs`
   - **Start in**: `C:\zomboid-tracker\` (your project folder path)
   - Click **OK**

5. **Conditions Tab**
   - Uncheck **"Start the task only if the computer is on AC power"**

6. **Settings Tab**
   - Check **"If the task fails, restart every: 1 minute"**
   - Attempt to restart up to: **3 times**

7. Click **OK** and enter your Windows password if prompted

**To test:** Restart your computer or right-click the task → "Run"

### Mac - Using launchd

1. Create `~/Library/LaunchAgents/com.zomboid.statstracker.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.zomboid.statstracker</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/your/start_monitor.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/zomboid-tracker.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/zomboid-tracker-error.log</string>
</dict>
</plist>
```

2. Load and start:
```bash
launchctl load ~/Library/LaunchAgents/com.zomboid.statstracker.plist
launchctl start com.zomboid.statstracker
```

### Linux - Using systemd

1. Create `/etc/systemd/system/zomboid-tracker.service`:

```ini
[Unit]
Description=Project Zomboid Stats Tracker
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/zomboid-stats-tracker
ExecStart=/usr/bin/python3 /path/to/zomboid-stats-tracker/main.py
Environment="DISCORD_WEBHOOK_URL=your_webhook_url"
Environment="FTP_HOST=your_ftp_host"
Environment="FTP_PORT=your_ftp_port"
Environment="FTP_USER=your_ftp_user"
Environment="FTP_PASS=your_ftp_pass"
Environment="LOG_BASE_PATH=/Logs"
Environment="CHECK_INTERVAL=30"
Environment="SKILL_NOTIFICATIONS=milestones"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable zomboid-tracker.service
sudo systemctl start zomboid-tracker.service
sudo systemctl status zomboid-tracker.service
```

---

## 📊 What Gets Tracked

### Player Statistics

Each player has a complete profile tracking:

**Current Character:**
- Alive status (🟢/💀)
- Spawn time
- Hours survived
- Current location
- All skill levels

**Lifetime Stats:**
- Total deaths
- Total respawns
- Total hours survived (across all lives)
- Longest survival streak
- Skill milestones (highest level reached per skill)

### Events Monitored

- **Deaths** - With survival time, location, and peak skills
- **Respawns** - New character creation with stats
- **Skill Level-Ups** - All 26 skills tracked
- **Logins** - Player connections (not notified, but tracked)

---

## 📢 Discord Notifications

### Death Notification
```
💀 xCATZx has died for the 5th time!

⏱️ Survived: 19 hours
📍 Location: (9126, 9351, 0)
🎯 Peak Skills: Aiming 10, Fitness 5, Blunt 3

Total Deaths: 5
Longest Survival: 1 day, 21 hours
```

### Respawn Notification
```
🔄 xCATZx is back in the game!

💀 Death Count: 5
📊 Average Survival: 14 hours
🎮 Character #6
```

### Skill Notification (if enabled)
```
🎉 xCATZx leveled up!

Aiming reached level 5
⏱️ After 12 hours survived
```

### Death Leaderboard
```
💀 Death Leaderboard 💀

🥇 Billy-Wayne: 12 deaths (avg: 8 hours)
🥈 Travis-Lee: 8 deaths (avg: 15 hours)
🥉 Bobby-Gene: 5 deaths (avg: 22 hours)
**4.** xCATZx: 5 deaths (avg: 14 hours)
```

### Survival Leaderboard
```
⏱️ Longest Survival Streaks ⏱️

🥇 Dog Goblin: 3 days, 6 hours 🟢
🥈 Tryskelly: 1 day, 21 hours
🥉 xCATZx: 1 day, 2 hours 🟢

🟢 = Currently Alive
```

### Total Hours Leaderboard
```
🏆 Most Experienced Survivors 🏆

🥇 Billy-Wayne: 6 days, 3 hours
🥈 Dog Goblin: 5 days, 12 hours
🥉 Tryskelly: 4 days, 2 hours
```

### Skill Leaderboard (Weekly)
```
🎯 Top Sharpshooters (Aiming) 🎯

🥇 Dog Goblin: Level 10
🥈 Tryskelly: Level 8
🥉 xCATZx: Level 5
```

---

## 🗓️ Leaderboard Schedule

### Daily Leaderboards
**When:** 12:00 PM (noon) and 12:00 AM (midnight)  
**What:** Death + Survival + Total Hours leaderboards

### Weekly Leaderboards
**When:** Sundays at 12:00 AM (midnight)  
**What:** Top skill leaderboards for:
- Aiming
- Fitness
- Strength
- Cooking
- Mechanics

### Activity-Based Leaderboards
**When:** Every ~50 minutes if there have been deaths/respawns  
**What:** Quick death leaderboard

---

## 🔍 Monitoring & Maintenance

### Checking if It's Running

**Windows:**

**Option 1: Task Manager**
1. Press `Ctrl + Shift + Esc`
2. Go to **Details** tab
3. Look for `pythonw.exe` - if it's there, the bot is running!

**Option 2: Check Discord**
- Are notifications appearing? Then it's working!

**Option 3: Check player_stats.json**
- Navigate to your project folder
- Right-click `player_stats.json` → Properties
- Check "Date Modified" - if recent (last few minutes), bot is active

**Option 4: Create a Log File** (for troubleshooting)
Modify `start_monitor.bat`:
```batch
pythonw main.py >> monitor_log.txt 2>&1
```
Then check `monitor_log.txt` to see all output.

**Mac:**
```bash
ps aux | grep python
# or
launchctl list | grep zomboid
```

**Linux:**
```bash
sudo systemctl status zomboid-tracker.service
```

### Stopping the Bot

**Windows:**
- Task Manager → Details → Find `pythonw.exe` → Right-click → End Task
- Or: Task Scheduler → Right-click task → End or Disable

**Mac:**
```bash
launchctl stop com.zomboid.statstracker
```

**Linux:**
```bash
sudo systemctl stop zomboid-tracker.service
```

### Updating the Bot

1. Download/pull latest version from GitHub
2. Stop the bot
3. Replace `main.py`
4. Restart the bot

Your `player_stats.json` file will be preserved!

---

## 🛠️ Troubleshooting

### Bot not starting

**Check Python installation:**
```bash
python --version  # Should show 3.8+
```

**Check dependencies:**
```bash
pip install -r requirements.txt
```

### No notifications appearing

**Check console/logs for errors:**
- `✗ FTP Error` → Verify FTP credentials
- `✗ Failed to send notification` → Check Discord webhook URL
- `⚠️ Could not list files` → Check LOG_BASE_PATH

**Verify FTP access manually:**
Use FileZilla or another FTP client to connect and browse to `/Logs/`

### Can't find PerkLog.txt

The bot looks for files named `PerkLog.txt` in:
- `/Logs/` (active logs)
- `/Logs/logs_DD-MM/` (archived logs)

Connect via FTP to verify the file exists and the path is correct.

### Duplicate notifications

- Ensure only ONE instance is running (check Task Manager)
- The bot automatically prevents duplicates within a session

### Missing some events

- Events are detected within `CHECK_INTERVAL` seconds
- Decrease `CHECK_INTERVAL` for faster detection
- Verify the log file contains the events (check via FTP)

---

## 📁 Project Structure

```
zomboid-stats-tracker/
├── main.py                    # Main bot script
├── requirements.txt           # Python dependencies  
├── README.md                  # This file
├── .gitignore                 # Git ignore rules
├── LICENSE                    # MIT License
├── start_monitor.bat          # Windows startup script (you create)
├── start_monitor_hidden.vbs   # Windows hidden launcher (you create)
├── start_monitor.sh           # Mac/Linux startup script (you create)
├── monitor_log.txt            # Optional: log output (generated)
└── player_stats.json          # Generated by bot (all player data)
```

---

## 💻 Technical Details

### Data Storage

**player_stats.json** contains:
- Complete player profiles with current and lifetime stats
- All skill levels and milestones
- File positions for log tracking
- Persistent across restarts

### Log Monitoring

- Connects via FTP every 30 seconds (configurable)
- Uses efficient "tail" reading (only downloads new content)
- Tracks position per file to prevent re-processing
- Automatically handles log rotation

### Events Processed

From `PerkLog.txt`:
- `[Died]` - Player deaths
- `[Created Player X]` - New character spawns
- `[Level Changed]` - Skill level-ups
- `[Login]` - Player connections (tracked but not notified)

---

## ⚡ Power & Performance

### Resource Usage
- **CPU:** ~0.1% when idle
- **RAM:** ~50-100MB
- **Bandwidth:** Minimal (only downloads new log content)
- **Disk:** ~1-5MB for player_stats.json

### Electricity Cost
- Idle PC: ~50-100W
- Cost per month: $5-15 (depending on rates)
- Much cheaper than cloud hosting!

### Is It Safe to Leave PC On?
**Yes!** Modern PCs handle 24/7 operation easily:
- ✅ Components rated for continuous use
- ✅ Minimal power draw at idle
- ✅ Less stress than gaming

**Tips:**
- Clean dust every few months
- Ensure good airflow
- Consider a UPS for power protection

---

## 🤝 Contributing

Contributions welcome! Ideas for features:

- [ ] More detailed death cause parsing
- [ ] Web dashboard for viewing stats
- [ ] Custom leaderboard schedules
- [ ] Player comparison tools
- [ ] Export stats to CSV
- [ ] Integration with other Discord bots
- [ ] Multi-server support

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## ❓ FAQ

**Q: Does this require server-side mods?**  
A: No! It only reads log files via FTP.

**Q: Will this work with other hosting providers?**  
A: Yes, as long as you have FTP access to the logs.

**Q: Can I run multiple instances for different servers?**  
A: Yes! Create separate folders with different configuration files.

**Q: What if my server resets/wipes?**  
A: Stats persist in `player_stats.json`. Delete it if you want to reset stats.

**Q: Can I customize the Discord messages?**  
A: Yes! Edit the notification functions in `main.py`.

**Q: Does it track deaths across character deaths?**  
A: Yes! Lifetime stats accumulate across all characters/deaths.

**Q: What about players who change their names?**  
A: Stats are tied to username. Name changes create new entries.

**Q: Can I host this on a VPS instead of my PC?**  
A: Yes! Follow the Linux systemd instructions.

**Q: How do I reset all stats?**  
A: Delete `player_stats.json` and restart the bot.

**Q: Can I export stats to Excel/CSV?**  
A: Not yet, but it's on the roadmap! For now, `player_stats.json` is human-readable.

---

## 📜 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Project Zomboid by The Indie Stone
- Discord for webhook API
- The amazing Project Zomboid community

---

**Made with 💀 for the Project Zomboid community**

*Stay alive out there... or don't. We're tracking either way.*

Created by [@n0valith](https://x.com/n0valith)
