@echo off

REM ===== REQUIRED SETTINGS =====

REM Your Discord webhook URL (get from Discord server settings)
set DISCORD_WEBHOOK_URL= 

REM FTP connection details (get from G-Portal or your hosting provider)
set FTP_HOST=
set FTP_PORT=
set FTP_USER=
set FTP_PASS=

REM ===== OPTIONAL SETTINGS =====

REM Where the logs are stored on your server
REM Default: /Logs
REM Change if your server uses a different path
set LOG_BASE_PATH=/Logs

REM How often to check for new events (in seconds)
REM Default: 30
REM Lower = more real-time, but uses slightly more resources
REM Higher = less frequent checks, saves bandwidth
REM Examples:
REM   set CHECK_INTERVAL=15   (check every 15 seconds - very responsive)
REM   set CHECK_INTERVAL=30   (check every 30 seconds - balanced)
REM   set CHECK_INTERVAL=60   (check every 60 seconds - relaxed)
set CHECK_INTERVAL=30

REM Skill level-up notifications
REM Default: milestones
REM Options:
REM   all        = Notify for EVERY skill level-up (level 1, 2, 3, 4, 5... can be VERY spammy!)
REM   milestones = Only notify at levels 5 and 10 (recommended - balanced)
REM   none       = Never notify about skills (only deaths/respawns)
REM Examples:
REM   set SKILL_NOTIFICATIONS=all         (get notifications for every single level)
REM   set SKILL_NOTIFICATIONS=milestones  (only levels 5 and 10)
REM   set SKILL_NOTIFICATIONS=none        (no skill notifications at all)
set SKILL_NOTIFICATIONS=all

pythonw main.py
