import os
import time
import ftplib
import re
import requests
import json
from datetime import datetime, timedelta
from io import BytesIO
from collections import defaultdict

# Configuration - Set these as environment variables
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
FTP_HOST = os.getenv('FTP_HOST')
FTP_PORT = int(os.getenv('FTP_PORT', '34231'))
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASS')
LOG_BASE_PATH = os.getenv('LOG_BASE_PATH', '/Logs')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '30'))
SKILL_NOTIFICATIONS = os.getenv('SKILL_NOTIFICATIONS', 'milestones')  # 'all', 'milestones', or 'none'
PLAYER_STATS_FILE = 'player_stats.json'

# Track last processed position per file
file_positions = {}
last_events = set()  # Prevent duplicate notifications
player_stats = {}  # Complete player statistics
unsaved_changes = False  # Track if we have unsaved data

# Skill milestone levels (for notifications)
SKILL_MILESTONES = [5, 10]

def load_player_stats():
    """Load player statistics from file"""
    global player_stats, file_positions
    try:
        if os.path.exists(PLAYER_STATS_FILE):
            with open(PLAYER_STATS_FILE, 'r') as f:
                data = json.load(f)
                player_stats = data.get('player_stats', {})
                file_positions = data.get('file_positions', {})
            print(f"✓ Loaded stats for {len(player_stats)} players")
    except Exception as e:
        print(f"⚠️ Could not load player stats: {e}")
        player_stats = {}
        file_positions = {}

def save_player_stats():
    """Save player statistics to file"""
    global unsaved_changes
    try:
        with open(PLAYER_STATS_FILE, 'w') as f:
            json.dump({
                'player_stats': player_stats,
                'file_positions': file_positions
            }, f, indent=2)
        unsaved_changes = False  # Mark as saved
    except Exception as e:
        print(f"⚠️ Could not save player stats: {e}")

def init_player(username, steam_id):
    """Initialize a new player in the stats system"""
    if username not in player_stats:
        player_stats[username] = {
            'steam_id': steam_id,
            'total_deaths': 0,
            'total_respawns': 0,
            'current_character': {
                'alive': False,
                'spawn_time': None,
                'hours_survived': 0,
                'last_location': [0, 0, 0],
                'skills': {}
            },
            'lifetime_stats': {
                'total_hours_survived': 0,
                'longest_survival': 0,
                'skill_milestones': {}
            }
        }

def format_time(hours):
    """Convert hours to readable format (X days, Y hours)"""
    days = int(hours // 24)
    remaining_hours = int(hours % 24)
    
    if days > 0:
        return f"{days} day{'s' if days != 1 else ''}, {remaining_hours} hour{'s' if remaining_hours != 1 else ''}"
    else:
        return f"{remaining_hours} hour{'s' if remaining_hours != 1 else ''}"

def get_death_ordinal(count):
    """Convert death count to ordinal (1st, 2nd, 3rd, etc.)"""
    if 10 <= count % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(count % 10, 'th')
    return f"{count}{suffix}"

def get_death_emoji(count):
    """Get emoji based on death count"""
    if count == 1:
        return "💀"
    elif count <= 3:
        return "☠️"
    elif count <= 5:
        return "⚰️"
    elif count <= 10:
        return "👻"
    else:
        return "🏴‍☠️"

def send_discord_notification(embed_data):
    """Generic function to send any embed to Discord"""
    payload = {
        "username": "Zomboid Stats Tracker",
        "embeds": [embed_data]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code in [200, 204]:
            return True
        else:
            print(f"✗ Failed to send notification: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error sending notification: {e}")
        return False

def send_death_notification(username, hours_survived, coordinates):
    """Send enhanced death notification"""
    player = player_stats[username]
    death_count = player['total_deaths']
    
    ordinal = get_death_ordinal(death_count)
    emoji = get_death_emoji(death_count)
    
    # Get top skills from previous character
    skills = player['current_character'].get('skills', {})
    top_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:3]
    top_skills_text = ", ".join([f"{skill} {level}" for skill, level in top_skills if level > 0])
    
    # Build description
    details = []
    details.append(f"⏱️ **Survived:** {format_time(hours_survived)}")
    details.append(f"📍 **Location:** {coordinates}")
    if top_skills_text:
        details.append(f"🎯 **Peak Skills:** {top_skills_text}")
    details.append("")
    details.append(f"**Total Deaths:** {death_count}")
    details.append(f"**Longest Survival:** {format_time(player['lifetime_stats']['longest_survival'])}")
    
    # Choose color based on death count
    if death_count == 1:
        color = 0xFF0000
    elif death_count <= 3:
        color = 0xFF6600
    elif death_count <= 5:
        color = 0xFF9900
    elif death_count <= 10:
        color = 0xFFCC00
    else:
        color = 0x990000
    
    embed = {
        "title": f"{emoji} {username} has died for the {ordinal} time!",
        "description": "\n".join(details),
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "Rest in pieces 💀"}
    }
    
    return send_discord_notification(embed)

def send_respawn_notification(username, character_num):
    """Send respawn notification"""
    player = player_stats[username]
    
    details = []
    details.append(f"💀 **Death Count:** {player['total_deaths']}")
    if player['total_deaths'] > 0:
        # Calculate average survival from lifetime stats
        avg_survival = player['lifetime_stats']['total_hours_survived'] / player['total_deaths']
        details.append(f"📊 **Average Survival:** {format_time(avg_survival)}")
    details.append(f"🎮 **Character #{character_num}**")
    
    embed = {
        "title": f"🔄 {username} is back in the game!",
        "description": "\n".join(details),
        "color": 0x00FF00,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "Good luck out there!"}
    }
    
    return send_discord_notification(embed)

def send_skill_notification(username, skill, level, hours_survived):
    """Send skill level-up notification"""
    embed = {
        "title": f"🎉 {username} leveled up!",
        "description": f"**{skill}** reached level **{level}**\n⏱️ After {format_time(hours_survived)} survived",
        "color": 0xFFD700,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "Keep grinding! 💪"}
    }
    
    return send_discord_notification(embed)

def send_leaderboard(leaderboard_type="death"):
    """Send various leaderboards to Discord"""
    if not player_stats:
        return
    
    if leaderboard_type == "death":
        # Death leaderboard with average survival
        sorted_players = sorted(
            [(name, data) for name, data in player_stats.items() if data['total_deaths'] > 0],
            key=lambda x: x[1]['total_deaths'],
            reverse=True
        )[:10]
        
        if not sorted_players:
            return
        
        lines = []
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (name, data) in enumerate(sorted_players):
            medal = medals[i] if i < 3 else f"**{i+1}.**"
            deaths = data['total_deaths']
            avg = data['lifetime_stats']['total_hours_survived'] / deaths if deaths > 0 else 0
            lines.append(f"{medal} {name}: **{deaths}** death{'s' if deaths != 1 else ''} (avg: {format_time(avg)})")
        
        embed = {
            "title": "💀 Death Leaderboard 💀",
            "description": "\n".join(lines),
            "color": 0x9900FF,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": f"Total tracked players: {len(player_stats)}"}
        }
    
    elif leaderboard_type == "survival":
        # Longest survival streaks - use current hours for alive players
        sorted_players = sorted(
            [(name, data) for name, data in player_stats.items()],
            key=lambda x: max(x[1]['lifetime_stats']['longest_survival'], 
                            x[1]['current_character']['hours_survived'] if x[1]['current_character']['alive'] else 0),
            reverse=True
        )[:10]
        
        if not sorted_players:
            return
        
        lines = []
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (name, data) in enumerate(sorted_players):
            medal = medals[i] if i < 3 else f"**{i+1}.**"
            longest = data['lifetime_stats']['longest_survival']
            current = data['current_character']['hours_survived'] if data['current_character']['alive'] else 0
            display_hours = max(longest, current)
            
            if display_hours == 0:
                continue
            alive_marker = " 🟢" if data['current_character']['alive'] else ""
            lines.append(f"{medal} {name}: {format_time(display_hours)}{alive_marker}")
        
        if not lines:
            return
        
        embed = {
            "title": "⏱️ Longest Survival Streaks ⏱️",
            "description": "\n".join(lines) + "\n\n🟢 = Currently Alive",
            "color": 0x00BFFF,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Survival of the fittest!"}
        }
    
    elif leaderboard_type == "hours":
        # Total hours survived
        sorted_players = sorted(
            [(name, data) for name, data in player_stats.items() if data['lifetime_stats']['total_hours_survived'] > 0],
            key=lambda x: x[1]['lifetime_stats']['total_hours_survived'],
            reverse=True
        )[:10]
        
        if not sorted_players:
            return
        
        lines = []
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (name, data) in enumerate(sorted_players):
            medal = medals[i] if i < 3 else f"**{i+1}.**"
            total_hours = data['lifetime_stats']['total_hours_survived']
            lines.append(f"{medal} {name}: {format_time(total_hours)}")
        
        embed = {
            "title": "🏆 Most Experienced Survivors 🏆",
            "description": "\n".join(lines),
            "color": 0xFFD700,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Total playtime across all lives"}
        }
    
    elif leaderboard_type.startswith("skill_"):
        # Skill-specific leaderboard
        skill_name = leaderboard_type.replace("skill_", "")
        
        # Get players with this skill
        players_with_skill = []
        for name, data in player_stats.items():
            if data['current_character']['alive']:
                skill_level = data['current_character']['skills'].get(skill_name, 0)
                if skill_level > 0:
                    players_with_skill.append((name, skill_level))
            
            # Also check lifetime milestones
            milestone = data['lifetime_stats']['skill_milestones'].get(skill_name, 0)
            if milestone > 0 and not data['current_character']['alive']:
                players_with_skill.append((name, milestone))
        
        if not players_with_skill:
            return
        
        sorted_players = sorted(players_with_skill, key=lambda x: x[1], reverse=True)[:10]
        
        lines = []
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (name, level) in enumerate(sorted_players):
            medal = medals[i] if i < 3 else f"**{i+1}.**"
            lines.append(f"{medal} {name}: Level **{level}**")
        
        skill_emoji = {
            "Aiming": "🎯",
            "Fitness": "💪",
            "Strength": "🏋️",
            "Cooking": "🍳",
            "Farming": "🌾",
            "Mechanics": "🔧",
            "Carpentry": "🔨"
        }
        
        emoji = skill_emoji.get(skill_name, "📊")
        
        embed = {
            "title": f"{emoji} Top {skill_name} Masters {emoji}",
            "description": "\n".join(lines),
            "color": 0x1E90FF,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": f"Highest {skill_name} levels"}
        }
    
    return send_discord_notification(embed)

def parse_perklog_line(line):
    """
    Parse a line from PerkLog.txt
    Format: [timestamp][SteamID][Username][X,Y,Z][EventType][Details][Hours Survived: X].
    Note: There may be spaces between brackets!
    """
    # Pattern allows optional whitespace between any brackets
    pattern = r'\[(.*?)\]\s*\[(.*?)\]\s*\[(.*?)\]\s*\[(\d+),(\d+),(\d+)\]\s*\[(.*?)\].*?\[Hours Survived: ([\d.]+)\]\.?'
    
    match = re.search(pattern, line)
    if not match:
        return None
    
    timestamp = match.group(1)
    steam_id = match.group(2)
    username = match.group(3)
    x, y, z = match.group(4), match.group(5), match.group(6)
    event_type = match.group(7)
    hours_survived = float(match.group(8))
    
    coordinates = f"({x}, {y}, {z})"
    
    # For details, we need to extract what's between event_type and Hours Survived
    # This could be another bracketed section or nothing
    details = ""
    if event_type == "Level Changed":
        # Extract skill and level from the line
        level_pattern = r'\[Level Changed\]\[(.*?)\]\[(\d+)\]'
        level_match = re.search(level_pattern, line)
        if level_match:
            details = f"{level_match.group(1)}][{level_match.group(2)}"
    elif event_type.startswith("Created Player"):
        # Extract the full skill dump from the NEXT line if it exists (handled elsewhere)
        pass
    
    return {
        'timestamp': timestamp,
        'steam_id': steam_id,
        'username': username,
        'coordinates': coordinates,
        'event_type': event_type,
        'details': details,
        'hours_survived': hours_survived
    }

def parse_skills_from_details(details):
    """Parse skill levels from skill dump string"""
    skills = {}
    # Format: "Cooking=0, Fitness=5, Strength=5, ..."
    skill_pairs = details.split(', ')
    for pair in skill_pairs:
        if '=' in pair:
            skill, level = pair.split('=')
            skills[skill.strip()] = int(level)
    return skills

def handle_death_event(event_data):
    """Handle a player death event"""
    global unsaved_changes
    username = event_data['username']
    steam_id = event_data['steam_id']
    hours_survived = event_data['hours_survived']
    coordinates = event_data['coordinates']
    
    init_player(username, steam_id)
    
    player = player_stats[username]
    player['total_deaths'] += 1
    player['current_character']['alive'] = False
    player['current_character']['hours_survived'] = hours_survived
    player['current_character']['last_location'] = coordinates
    
    # Update lifetime stats
    player['lifetime_stats']['total_hours_survived'] += hours_survived
    if hours_survived > player['lifetime_stats']['longest_survival']:
        player['lifetime_stats']['longest_survival'] = hours_survived
    
    unsaved_changes = True  # Mark data as changed
    
    print(f"💀 Death: {username} survived {format_time(hours_survived)} (Death #{player['total_deaths']})")
    send_death_notification(username, hours_survived, coordinates)
    save_player_stats()

def handle_spawn_event(event_data):
    """Handle a new character spawn event"""
    global unsaved_changes
    username = event_data['username']
    steam_id = event_data['steam_id']
    
    init_player(username, steam_id)
    
    player = player_stats[username]
    player['total_respawns'] += 1
    player['current_character'] = {
        'alive': True,
        'spawn_time': datetime.now().isoformat(),
        'hours_survived': 0,
        'last_location': event_data['coordinates'],
        'skills': {}
    }
    
    # Parse initial skills if present in details
    if event_data['details']:
        skills = parse_skills_from_details(event_data['details'])
        player['current_character']['skills'] = skills
    
    unsaved_changes = True  # Mark data as changed
    
    character_num = player['total_respawns']
    print(f"🔄 Respawn: {username} (Character #{character_num})")
    send_respawn_notification(username, character_num)
    save_player_stats()

def handle_level_change_event(event_data):
    """Handle a skill level-up event"""
    global unsaved_changes
    username = event_data['username']
    steam_id = event_data['steam_id']
    hours_survived = event_data['hours_survived']
    
    init_player(username, steam_id)
    
    # Parse skill and level from details
    # Format: "Skill][Level" e.g., "Aiming][3"
    details_parts = event_data['details'].split('][')
    if len(details_parts) >= 2:
        skill = details_parts[0]
        level = int(details_parts[1])
        
        player = player_stats[username]
        player['current_character']['skills'][skill] = level
        player['current_character']['hours_survived'] = hours_survived
        
        # Update lifetime milestone if this is the highest they've reached
        current_milestone = player['lifetime_stats']['skill_milestones'].get(skill, 0)
        if level > current_milestone:
            player['lifetime_stats']['skill_milestones'][skill] = level
        
        unsaved_changes = True  # Mark data as changed
        
        print(f"📈 Level Up: {username} - {skill} level {level}")
        
        # Send notification based on settings
        should_notify = False
        if SKILL_NOTIFICATIONS == 'all':
            should_notify = True
        elif SKILL_NOTIFICATIONS == 'milestones' and level in SKILL_MILESTONES:
            should_notify = True
        
        if should_notify:
            send_skill_notification(username, skill, level, hours_survived)
        
        save_player_stats()

def handle_login_event(event_data):
    """Handle a player login event"""
    global unsaved_changes
    username = event_data['username']
    steam_id = event_data['steam_id']
    
    init_player(username, steam_id)
    
    # Parse skills if present
    if event_data['details']:
        skills = parse_skills_from_details(event_data['details'])
        player = player_stats[username]
        player['current_character']['skills'] = skills
        player['current_character']['alive'] = True
        player['current_character']['hours_survived'] = event_data['hours_survived']
        unsaved_changes = True  # Mark data as changed
    
    print(f"👋 Login: {username} ({format_time(event_data['hours_survived'])} survived)")

def get_log_folders_to_check(ftp):
    """Get list of log folders to check"""
    folders = []
    folders.append("")
    
    try:
        ftp.cwd(LOG_BASE_PATH)
        
        all_items = []
        try:
            lines = []
            ftp.retrlines('LIST', lines.append)
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 9:
                    name = parts[-1]
                    if line.startswith('d') and name.startswith('logs_') and '-' in name:
                        all_items.append(name)
        except:
            all_items = ftp.nlst()
        
        log_folders = [item for item in all_items if item.startswith('logs_') and '-' in item]
        
        if log_folders:
            log_folders.sort(reverse=True)
            most_recent = log_folders[0]
            folders.append(most_recent)
            print(f"ℹ️ Found archived log folder: {most_recent}")
    
    except Exception as e:
        print(f"⚠️ Could not list archived log folders: {e}")
        today = datetime.now()
        folders.append(f"logs_{today.strftime('%d-%m')}")
        yesterday = today - timedelta(days=1)
        folders.append(f"logs_{yesterday.strftime('%d-%m')}")
    
    return folders

def list_perklog_files(ftp, folder_path):
    """List all PerkLog.txt files in a specific log folder"""
    try:
        files = []
        ftp.cwd(folder_path)
        
        try:
            lines = []
            ftp.retrlines('LIST', lines.append)
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 9:
                    filename = parts[-1]
                    if 'PerkLog' in filename and filename.endswith('.txt'):
                        files.append(filename)
        except:
            file_list = ftp.nlst()
            for filename in file_list:
                if 'PerkLog' in filename and filename.endswith('.txt'):
                    files.append(filename)
        
        return sorted(files)
    except Exception as e:
        print(f"⚠️ Could not list files in {folder_path}: {e}")
        return []

def download_log_tail(ftp, log_path, from_position=0):
    """Download the log file from FTP starting from last position"""
    try:
        file_size = ftp.size(log_path)
        
        if file_size is None:
            print(f"✗ Could not determine size of {log_path}")
            return None, from_position
        
        print(f"DEBUG - File: {log_path}, Size: {file_size}, From: {from_position}")
        
        if file_size < from_position:
            from_position = 0
            print(f"ℹ️ Log file {log_path} rotated, starting from beginning")
        
        if file_size == from_position:
            return "", from_position
        
        buffer = BytesIO()
        ftp.retrbinary(f'RETR {log_path}', buffer.write, rest=from_position)
        
        content = buffer.getvalue().decode('utf-8', errors='ignore')
        new_position = file_size
        
        print(f"DEBUG - Downloaded {len(content)} bytes")
        
        return content, new_position
        
    except Exception as e:
        print(f"✗ Error reading {log_path}: {e}")
        return None, from_position

def monitor_server():
    """Main monitoring loop"""
    global last_events, file_positions
    
    load_player_stats()
    
    print("=" * 50)
    print("Project Zomboid Stats Tracker Started")
    print("=" * 50)
    print(f"FTP Server: {FTP_HOST}:{FTP_PORT}")
    print(f"Log Base Path: {LOG_BASE_PATH}")
    print(f"Check Interval: {CHECK_INTERVAL}s")
    print(f"Discord Webhook: {DISCORD_WEBHOOK_URL[:30]}...")
    print(f"Tracking {len(player_stats)} players")
    print(f"Skill Notifications: {SKILL_NOTIFICATIONS}")
    print("=" * 50)
    print("\nMonitoring for events...\n")
    
    consecutive_errors = 0
    max_errors = 5
    check_count = 0
    leaderboard_check_interval = 100
    events_since_last_leaderboard = False
    last_daily_leaderboard_date = None
    last_weekly_leaderboard_date = None
    
    while True:
        try:
            ftp = ftplib.FTP()
            ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
            ftp.login(FTP_USER, FTP_PASS)
            
            log_folders = get_log_folders_to_check(ftp)
            
            for folder_name in log_folders:
                folder_path = f"{LOG_BASE_PATH}/{folder_name}" if folder_name else LOG_BASE_PATH
                
                try:
                    perklog_files = list_perklog_files(ftp, folder_path)
                    
                    for log_filename in perklog_files:
                        log_path = f"{folder_path}/{log_filename}"
                        
                        last_pos = file_positions.get(log_path, 0)
                        new_content, new_pos = download_log_tail(ftp, log_path, last_pos)
                        
                        if new_content:
                            consecutive_errors = 0
                            file_positions[log_path] = new_pos
                            
                            lines = new_content.split('\n')
                            
                            for line in lines:
                                if not line.strip():
                                    continue
                                
                                # Debug: print first few lines to see format
                                if check_count == 0:
                                    print(f"DEBUG - Processing line: {line[:100]}")
                                
                                event_data = parse_perklog_line(line)
                                
                                if event_data:
                                    print(f"✓ Parsed event: {event_data['event_type']} - {event_data['username']}")
                                    
                                    # Create unique event ID
                                    event_id = f"{event_data['username']}_{event_data['event_type']}_{event_data['timestamp']}"
                                    
                                    if event_id not in last_events:
                                        last_events.add(event_id)
                                        events_since_last_leaderboard = True
                                        
                                        # Handle different event types
                                        if event_data['event_type'] == 'Died':
                                            handle_death_event(event_data)
                                        elif 'Created Player' in event_data['event_type']:
                                            handle_spawn_event(event_data)
                                        elif event_data['event_type'] == 'Level Changed':
                                            handle_level_change_event(event_data)
                                        elif event_data['event_type'] == 'Login':
                                            handle_login_event(event_data)
                                        
                                        # Keep only last 500 events in memory
                                        if len(last_events) > 500:
                                            last_events = set(list(last_events)[-500:])
                
                except Exception as e:
                    print(f"⚠️ Error processing folder {folder_path}: {e}")
                    continue
            
            ftp.quit()
            
            # Scheduled leaderboards
            current_time = datetime.now()
            current_date = current_time.date()
            current_hour = current_time.hour
            current_minute = current_time.minute
            current_weekday = current_time.weekday()
            
            # Daily leaderboards at noon and midnight
            if current_minute == 0 and last_daily_leaderboard_date != current_date:
                if current_hour == 12 or current_hour == 0:
                    if player_stats:
                        print(f"\n📊 Sending scheduled {'noon' if current_hour == 12 else 'midnight'} leaderboards...")
                        send_leaderboard("death")
                        time.sleep(2)
                        send_leaderboard("survival")
                        time.sleep(2)
                        send_leaderboard("hours")
                        last_daily_leaderboard_date = current_date
                        events_since_last_leaderboard = False
            
            # Weekly skill leaderboards (Sunday at midnight)
            if current_weekday == 6 and current_hour == 0 and current_minute == 0:
                if last_weekly_leaderboard_date != current_date and player_stats:
                    print(f"\n📊 Sending weekly skill leaderboards...")
                    top_skills = ['Aiming', 'Fitness', 'Strength', 'Cooking', 'Mechanics']
                    for skill in top_skills:
                        send_leaderboard(f"skill_{skill}")
                        time.sleep(2)
                    last_weekly_leaderboard_date = current_date
            
            # Activity-based leaderboard
            check_count += 1
            if check_count % leaderboard_check_interval == 0:
                if events_since_last_leaderboard and player_stats:
                    print(f"\n📊 Sending activity-based leaderboard...")
                    send_leaderboard("death")
                    events_since_last_leaderboard = False
            
            # Save stats periodically (only if there are unsaved changes)
            if check_count % 10 == 0 and unsaved_changes:
                print("💾 Periodic save (unsaved changes detected)")
                save_player_stats()
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\nStopping stats tracker...")
            save_player_stats()
            break
        except Exception as e:
            consecutive_errors += 1
            print(f"✗ Unexpected error: {e}")
            if consecutive_errors >= max_errors:
                print(f"⚠️ Too many errors, waiting longer before retry...")
                time.sleep(CHECK_INTERVAL * 3)
                consecutive_errors = 0
            else:
                time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    required_vars = {
        'DISCORD_WEBHOOK_URL': DISCORD_WEBHOOK_URL,
        'FTP_HOST': FTP_HOST,
        'FTP_USER': FTP_USER,
        'FTP_PASS': FTP_PASS
    }
    
    missing_vars = [name for name, value in required_vars.items() if not value]
    
    if missing_vars:
        print("❌ ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these environment variables before running.")
        exit(1)
    
    monitor_server()
