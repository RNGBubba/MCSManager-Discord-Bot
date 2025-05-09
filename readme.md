
# Discord MCS Manager Bot - Setup & Command Guide

## Table of Contents
- [Initial Setup](#initial-setup)
- [Bot Configuration](#bot-configuration)
- [Command Categories](#command-categories)
  - [Auto-Restart Commands](#auto-restart-commands)
  - [Channel Commands](#channel-commands)
  - [Docker Commands](#docker-commands)
  - [Enhanced Logging](#enhanced-logging)
  - [Fun Commands](#fun-commands)
  - [Giveaway System](#giveaway-system)
  - [Instance Commands](#instance-commands)
  - [Invite Tracker](#invite-tracker)
  - [Leveling System](#leveling-system)
  - [Moderation Commands](#moderation-commands)
  - [Node Commands](#node-commands)
  - [Reaction Roles](#reaction-roles)
  - [Role Commands](#role-commands)
  - [Schedule Commands](#schedule-commands)
  - [Stats Commands](#stats-commands)
  - [System Commands](#system-commands)
  - [User Commands](#user-commands)
  - [Utility Commands](#utility-commands)
- [Troubleshooting](#troubleshooting)

## Initial Setup

### Requirements
- Python 3.13 or higher
- discord.py library
- Additional dependencies as listed in requirements.txt

### Installation Steps (Short Way)
1. Clone or download the bot files to your machine
3. Edit and rename the `.env.example` to `.env` file in the root directory with the following:
   ```
   DISCORD_BOT_TOKEN="" #Bot Token
   MCSMANAGER_ADDRESS="" #URL to connect to your MCS Manager
   MCSMANAGER_API_KEY="" #Your MCS Manager API Key

   # Weather API Key [Optional] (for /utility weather command)
   # WEATHER_API_KEY=your_weather_api_key_here

   # Translation API Key [Optional] (for Translate Message context menu)
   # TRANSLATION_API_KEY=your_translation_api_key_here
   ```
3. To start the bot and install requirements, run the bat file: (Will Check for and install Python, Pip, & Bot Requirements)
   ```
   AIO Start.bat
   ```

### Installation Steps (Long Way)
1. Clone or download the bot files to your machine
2. Install required dependencies:
   ```
   pip3 install -r requirements.txt
   ```
3. Edit and rename the `.env.example` to `.env` file in the root directory with the following:
   ```
   DISCORD_BOT_TOKEN="" #Bot Token
   MCSMANAGER_ADDRESS="" #URL to connect to your MCS Manager
   MCSMANAGER_API_KEY="" #Your MCS Manager API Key

   # Weather API Key [Optional] (for /utility weather command)
   # WEATHER_API_KEY=your_weather_api_key_here

   # Translation API Key [Optional] (for Translate Message context menu)
   # TRANSLATION_API_KEY=your_translation_api_key_here
   ```
4. To start the bot, run:
   ```
   python __init__.py
   ```

### Creating a Discord Bot Account
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and name your bot
3. Navigate to the "Bot" tab and click "Add Bot"
4. Under the "Privileged Gateway Intents" section, enable all intents
5. Copy your bot token and paste it in the `.env` file
6. To invite the bot to your server, go to the "OAuth2" tab
7. Select "bot" and "applications.commands" scopes
8. Select appropriate permissions (Admin is recommended for full functionality)
9. Copy the generated URL and open it in your browser to add the bot to your server

## Bot Configuration

The bot uses several configuration files to store settings:
- `auto_restart_config.json` - Auto-restart settings
- `invite_data.json` - Invite tracking data
- `reaction_roles.json` - Reaction roles configuration

These files will be automatically created when you first configure the respective features.

## Command Categories

### Auto-Restart Commands

Auto-restart commands help you schedule automatic restarts for instances (typically game servers).

#### `/autorestart setup`
Sets up automatic server restarts.
- **Parameters**:
  - `instance_name`: Name of the instance to restart
  - `channel`: Channel to send restart notifications
  - `interval_hours`: Restart interval in hours (default: 4)
- **Example**: `/autorestart setup instance_name:survival channel:#server-status interval_hours:6`

#### `/autorestart disable`
Disables automatic restarts for an instance.
- **Parameters**:
  - `instance_name`: Name of the instance
- **Example**: `/autorestart disable instance_name:survival`

#### `/autorestart enable`
Enables automatic restarts for an instance.
- **Parameters**:
  - `instance_name`: Name of the instance
- **Example**: `/autorestart enable instance_name:survival`

#### `/autorestart list`
Lists all configured auto-restarts.
- **Example**: `/autorestart list`

#### `/autorestart update`
Updates auto-restart configuration.
- **Parameters**:
  - `instance_name`: Name of the instance
  - `channel`: New notification channel (optional)
  - `interval_hours`: New restart interval in hours (optional)
- **Example**: `/autorestart update instance_name:survival channel:#announcements interval_hours:8`

#### `/autorestart delete`
Deletes auto-restart configuration.
- **Parameters**:
  - `instance_name`: Name of the instance
- **Example**: `/autorestart delete instance_name:survival`

#### `/autorestart now`
Triggers an immediate restart.
- **Parameters**:
  - `instance_name`: Name of the instance to restart
  - `countdown`: Enable countdown messages (default: True)
- **Example**: `/autorestart now instance_name:survival countdown:True`

### Channel Commands

Channel commands help manage and get information about Discord channels.

#### `/channel info`
Gets detailed information about a channel.
- **Parameters**:
  - `channel`: The channel to get information about (optional, defaults to current channel)
- **Example**: `/channel info channel:#general`

### Docker Commands

These commands help manage Docker containers, typically for game servers or other applications.

#### `/docker list`
Lists all Docker containers.
- **Example**: `/docker list`

#### `/docker start`
Starts a Docker container.
- **Parameters**:
  - `container_name`: Name of the container
- **Example**: `/docker start container_name:mc_server`

#### `/docker stop`
Stops a Docker container.
- **Parameters**:
  - `container_name`: Name of the container
- **Example**: `/docker stop container_name:mc_server`

#### `/docker restart`
Restarts a Docker container.
- **Parameters**:
  - `container_name`: Name of the container
- **Example**: `/docker restart container_name:mc_server`

### Enhanced Logging

Advanced logging capabilities for tracking server events and user actions.

#### `/logging setup`
Sets up enhanced logging in a specific channel.
- **Parameters**:
  - `channel`: Channel for logging
  - `log_type`: Type of events to log
- **Example**: `/logging setup channel:#server-logs log_type:All Events`

#### `/logging disable`
Disables logging for a specific event type.
- **Parameters**:
  - `log_type`: Type of events to stop logging
- **Example**: `/logging disable log_type:Member Events`

### Fun Commands

Entertainment commands for server members.

#### `/8ball`
Ask the Magic 8-Ball a question.
- **Parameters**:
  - `question`: Your yes/no question
- **Example**: `/8ball question:Will I win the lottery?`

#### `/roll`
Roll a die or random number.
- **Parameters**:
  - `sides`: Number of sides on the die (default: 6)
- **Example**: `/roll sides:20`

#### `/coinflip`
Flip a coin.
- **Example**: `/coinflip`

#### `/rps`
Play Rock, Paper, Scissors with the bot.
- **Parameters**:
  - `choice`: Your choice (rock, paper, or scissors)
- **Example**: `/rps choice:rock`

### Giveaway System

Run giveaways on your server.

#### `/giveaway create`
Creates a new giveaway.
- **Parameters**:
  - `prize`: The prize being given away
  - `winners`: Number of winners
  - `duration`: Duration of the giveaway (e.g., 1d 12h 30m)
  - `channel`: Channel to host the giveaway
- **Example**: `/giveaway create prize:Nitro Classic winners:2 duration:3d channel:#giveaways`

#### `/giveaway end`
Ends a giveaway early.
- **Parameters**:
  - `message_id`: ID of the giveaway message
- **Example**: `/giveaway end message_id:123456789123456789`

#### `/giveaway reroll`
Rerolls winners for a giveaway.
- **Parameters**:
  - `message_id`: ID of the giveaway message
  - `winners`: Number of new winners to pick
- **Example**: `/giveaway reroll message_id:123456789123456789 winners:1`

### Instance Commands

Manage game or application instances.

#### `/instance list`
Lists all instances.
- **Example**: `/instance list`

#### `/instance info`
Gets detailed information about an instance.
- **Parameters**:
  - `instance_name`: Name of the instance
- **Example**: `/instance info instance_name:survival`

#### `/instance start`
Starts an instance.
- **Parameters**:
  - `instance_name`: Name of the instance
- **Example**: `/instance start instance_name:survival`

#### `/instance stop`
Stops an instance.
- **Parameters**:
  - `instance_name`: Name of the instance
- **Example**: `/instance stop instance_name:survival`

#### `/instance restart`
Restarts an instance.
- **Parameters**:
  - `instance_name`: Name of the instance
- **Example**: `/instance restart instance_name:survival`

#### `/instance kill`
Force kills an instance.
- **Parameters**:
  - `instance_name`: Name of the instance
- **Example**: `/instance kill instance_name:survival`

### Invite Tracker

Track who invited users to your server.

#### `/invites setup`
Sets up invite tracking.
- **Example**: `/invites setup`

#### `/invites leaderboard`
Displays the invite leaderboard.
- **Parameters**:
  - `limit`: Number of entries to show
- **Example**: `/invites leaderboard limit:10`

#### `/invites check`
Checks a specific user's invites.
- **Parameters**:
  - `user`: User to check
- **Example**: `/invites check user:@username`

### Leveling System

XP and level system for your server members.

#### `/level setup`
Sets up the leveling system.
- **Parameters**:
  - `channel`: Channel for level-up announcements (optional)
- **Example**: `/level setup channel:#level-ups`

#### `/level rank`
Displays a user's current rank and XP.
- **Parameters**:
  - `user`: User to check (optional, defaults to you)
- **Example**: `/level rank user:@username`

#### `/level leaderboard`
Displays the server's XP leaderboard.
- **Parameters**:
  - `limit`: Number of entries to show
- **Example**: `/level leaderboard limit:10`

#### `/level rewards add`
Adds a role reward for reaching a specific level.
- **Parameters**:
  - `level`: Level required
  - `role`: Role to award
- **Example**: `/level rewards add level:10 role:@VIP`

#### `/level rewards list`
Lists all level role rewards.
- **Example**: `/level rewards list`

### Moderation Commands

Tools for server moderation.

#### `/warn`
Warns a user.
- **Parameters**:
  - `user`: User to warn
  - `reason`: Reason for the warning
- **Example**: `/warn user:@username reason:Spamming in chat`

#### `/mute`
Mutes a user temporarily.
- **Parameters**:
  - `user`: User to mute
  - `duration`: Duration of the mute
  - `reason`: Reason for the mute
- **Example**: `/mute user:@username duration:1h reason:Inappropriate language`

#### `/unmute`
Unmutes a user.
- **Parameters**:
  - `user`: User to unmute
- **Example**: `/unmute user:@username`

#### `/kick`
Kicks a user from the server.
- **Parameters**:
  - `user`: User to kick
  - `reason`: Reason for the kick
- **Example**: `/kick user:@username reason:Violating server rules`

#### `/ban`
Bans a user from the server.
- **Parameters**:
  - `user`: User to ban
  - `delete_days`: Days of messages to delete
  - `reason`: Reason for the ban
- **Example**: `/ban user:@username delete_days:1 reason:Severe rule violation`

#### `/unban`
Unbans a user from the server.
- **Parameters**:
  - `user_id`: ID of the user to unban
- **Example**: `/unban user_id:123456789123456789`

#### `/purge`
Deletes multiple messages at once.
- **Parameters**:
  - `amount`: Number of messages to delete
  - `user`: Filter messages by user (optional)
- **Example**: `/purge amount:50 user:@username`

### Node Commands

Manage node-based services.

#### `/node status`
Checks the status of nodes.
- **Example**: `/node status`

#### `/node restart`
Restarts a specific node.
- **Parameters**:
  - `node_name`: Name of the node
- **Example**: `/node restart node_name:node1`

### Reaction Roles

Set up roles that members can get by reacting to messages.

#### `/reactionrole create`
Creates a new reaction role message.
- **Parameters**:
  - `channel`: Channel for the message
  - `title`: Title of the embed
  - `description`: Description of the embed
- **Example**: `/reactionrole create channel:#roles title:Server Roles description:React to get roles!`

#### `/reactionrole add`
Adds a role to a reaction role message.
- **Parameters**:
  - `message_id`: ID of the reaction role message
  - `role`: Role to add
  - `emoji`: Emoji to use for the role
  - `description`: Description of the role
- **Example**: `/reactionrole add message_id:123456789123456789 role:@Gamer emoji:🎮 description:For gaming enthusiasts`

#### `/reactionrole remove`
Removes a role from a reaction role message.
- **Parameters**:
  - `message_id`: ID of the reaction role message
  - `role`: Role to remove
- **Example**: `/reactionrole remove message_id:123456789123456789 role:@Gamer`

#### `/reactionrole list`
Lists all reaction role messages.
- **Example**: `/reactionrole list`

### Role Commands

Manage server roles.

#### `/role create`
Creates a new role.
- **Parameters**:
  - `name`: Name of the role
  - `color`: Color of the role
  - `mentionable`: Whether the role is mentionable
  - `hoisted`: Whether the role appears separately in the member list
- **Example**: `/role create name:VIP color:#ff0000 mentionable:True hoisted:True`

#### `/role delete`
Deletes a role.
- **Parameters**:
  - `role`: Role to delete
- **Example**: `/role delete role:@VIP`

#### `/role add`
Adds a role to a user.
- **Parameters**:
  - `user`: User to give the role to
  - `role`: Role to give
- **Example**: `/role add user:@username role:@VIP`

#### `/role remove`
Removes a role from a user.
- **Parameters**:
  - `user`: User to remove the role from
  - `role`: Role to remove
- **Example**: `/role remove user:@username role:@VIP`

#### `/role info`
Shows information about a role.
- **Parameters**:
  - `role`: Role to get information about
- **Example**: `/role info role:@VIP`

### Schedule Commands

Schedule messages and events.

#### `/schedule message`
Schedules a message to be sent later.
- **Parameters**:
  - `channel`: Channel to send the message in
  - `time`: When to send the message
  - `message`: Message content
- **Example**: `/schedule message channel:#announcements time:tomorrow at 3pm message:Don't forget our event!`

#### `/schedule list`
Lists all scheduled messages.
- **Example**: `/schedule list`

#### `/schedule cancel`
Cancels a scheduled message.
- **Parameters**:
  - `id`: ID of the scheduled message
- **Example**: `/schedule cancel id:123`

### Stats Commands

Display server and user statistics.

#### `/stats server`
Shows server statistics.
- **Example**: `/stats server`

#### `/stats user`
Shows user statistics.
- **Parameters**:
  - `user`: User to check (optional, defaults to you)
- **Example**: `/stats user user:@username`

#### `/stats voice`
Shows voice channel statistics.
- **Example**: `/stats voice`

### System Commands

System-related commands for the bot.

#### `/system info`
Shows system information.
- **Example**: `/system info`

#### `/system ping`
Checks the bot's latency.
- **Example**: `/system ping`

#### `/system uptime`
Shows how long the bot has been running.
- **Example**: `/system uptime`

### User Commands

User management commands.

#### `/user info`
Shows detailed information about a user.
- **Parameters**:
  - `user`: User to get information about
- **Example**: `/user info user:@username`

#### `/user avatar`
Shows a user's avatar.
- **Parameters**:
  - `user`: User to get avatar for
- **Example**: `/user avatar user:@username`

#### `/user whois`
Shows who invited a user to the server.
- **Parameters**:
  - `user`: User to check
- **Example**: `/user whois user:@username`

### Utility Commands

Miscellaneous utility commands.

#### `/poll create`
Creates a poll.
- **Parameters**:
  - `question`: Poll question
  - `options`: Options, separated by commas
  - `duration`: How long the poll should last
- **Example**: `/poll create question:Favorite color? options:Red,Blue,Green duration:1 day`

#### `/embed create`
Creates a custom embed message.
- **Parameters**:
  - `title`: Embed title
  - `description`: Embed description
  - `color`: Embed color
  - `image`: Image URL (optional)
  - `thumbnail`: Thumbnail URL (optional)
- **Example**: `/embed create title:Announcement description:Important server news! color:#ff0000`

### Configuration Files
All configuration files are stored in JSON format in the bot's root directory:
- `auto_restart_config.json`
- `invite_data.json`
- `reaction_roles.json`

## Troubleshooting

### Bot Doesn't Start
- Check if your token is correct in the `.env` file
- Ensure you have all required dependencies installed
- Check if the bot has the necessary permissions in your Discord server

### Commands Don't Work
- Make sure the bot has the necessary permissions
- Check if you're using the command correctly (refer to the command documentation)
- Restart the bot to ensure all commands are registered

### Common Issues
- "Missing Permissions" error: The bot needs additional permissions
- "Command not found" error: The command may not be registered correctly
- Rate limiting: Discord has rate limits on bot actions, so some commands may fail if used too frequently

For any other issues, please contact the developer: Mr Bubba (Discord ID: 1130162662907580456).
