# ╔════════════════════════════════════════════════════╗
# ║               Developed by Mr Bubba                ║
# ║                                                    ║
# ║ Discord Username : Mr Bubba                        ║
# ║ Discord Tag      : exbubba                         ║
# ║ Discord ID       : 1130162662907580456             ║
# ║                                                    ║
# ║      Please respect the developer's work!          ║
# ╚════════════════════════════════════════════════════╝


import discord
from discord import app_commands
from discord.ext import commands
import os
import datetime
import asyncio
import json
import io
import re
import aiohttp
from typing import Optional, Union, List, Dict, Any
from discord.ui import Button, View, Select

class LogNavigationView(View):
    def __init__(self, message_url: str, author: discord.Member):
        super().__init__(timeout=300)
        self.add_item(Button(label="Go to Message", url=message_url, style=discord.ButtonStyle.link))
        self.add_item(Button(label="User Profile", url=f"discord://-/users/{author.id}", style=discord.ButtonStyle.link))

class LogConfigView(View):
    def __init__(self, cog, guild_id: int):
        super().__init__(timeout=180)
        self.cog = cog
        self.guild_id = guild_id
        
        self.add_item(self.get_color_selector())
        
        self.add_item(Button(label="Reset to Default", custom_id="reset_config", style=discord.ButtonStyle.danger))
        self.add_item(Button(label="Save Configuration", custom_id="save_config", style=discord.ButtonStyle.success))
    
    def get_color_selector(self):
        select = Select(
            placeholder="Select log event colors",
            options=[
                discord.SelectOption(label="Message Delete", value="message_delete", description="Color for deleted messages"),
                discord.SelectOption(label="Message Edit", value="message_edit", description="Color for edited messages"),
                discord.SelectOption(label="Member Join", value="member_join", description="Color for member joins"),
                discord.SelectOption(label="Member Leave", value="member_leave", description="Color for member leaves"),
                discord.SelectOption(label="Voice Events", value="voice", description="Color for voice events"),
                discord.SelectOption(label="Role Events", value="role", description="Color for role events"),
                discord.SelectOption(label="Channel Events", value="channel", description="Color for channel events"),
            ],
            min_values=1,
            max_values=1
        )
        return select

class EnhancedLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
        
        self.default_colors = {
            "message_delete": discord.Color.red(),
            "message_edit": discord.Color.gold(),
            "member_join": discord.Color.green(),
            "member_leave": discord.Color.red(),
            "member_update": discord.Color.blue(),
            "voice": discord.Color.purple(),
            "channel": discord.Color.teal(),
            "role": discord.Color.orange(),
            "server": discord.Color.dark_blue(),
            "moderation": discord.Color.dark_red()
        }
        
        self.load_env_vars()
        
        self.guild_configs = {}
        self.load_configs()
        
    def load_env_vars(self):
        """Load environment variables from .env file"""
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
            
            if not os.path.exists(env_path):
                print(f"Warning: .env file not found at {env_path}")
                return
                
            with open(env_path, 'r') as f:
                lines = f.readlines()
                
            log_vars_count = 0
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    
                    if key.startswith(('LOG_CHANNEL_', 'LOG_MESSAGE_CHANNEL_', 'LOG_MEMBER_CHANNEL_', 
                                      'LOG_VOICE_CHANNEL_', 'LOG_SERVER_CHANNEL_', 'LOG_WEBHOOK_')):
                        os.environ[key] = value
                        log_vars_count += 1
            
            print(f"Loaded {log_vars_count} logging variables from .env file")
        except Exception as e:
            print(f"Failed to load environment variables from .env file: {e}")
    
    def load_configs(self):
        """Load guild configurations from file"""
        try:
            if os.path.exists("log_configs.json"):
                with open("log_configs.json", "r") as f:
                    data = json.load(f)
                    self.guild_configs = {int(k): v for k, v in data.items()}
        except Exception as e:
            print(f"Failed to load logging configurations: {e}")
    
    def save_configs(self):
        """Save guild configurations to file and update .env file"""
        try:
            with open("log_configs.json", "w") as f:
                json.dump(self.guild_configs, f, indent=4)
                
            self.update_env_file()
        except Exception as e:
            print(f"Failed to save logging configurations: {e}")
            
    def update_env_file(self):
        """Update the .env file with current environment variables related to logging"""
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
            
            log_vars_pattern = re.compile(r'^(LOG_CHANNEL_|LOG_MESSAGE_CHANNEL_|LOG_MEMBER_CHANNEL_|LOG_VOICE_CHANNEL_|LOG_SERVER_CHANNEL_|LOG_WEBHOOK_)')
            
            preserved_lines = []
            
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#') or not log_vars_pattern.match(line.split('=')[0] if '=' in line else ''):
                        preserved_lines.append(line)
            else:
                preserved_lines = [
                    "# Discord Bot Configuration",
                    "DISCORD_BOT_TOKEN=\"your_token_here\"",
                    "EPHEMERAL_MESSAGE=True",
                    ""
                ]
                print(f"Creating new .env file at {env_path}")
            
            log_vars = []
            for key, value in os.environ.items():
                if log_vars_pattern.match(key):
                    log_vars.append(f"{key}=\"{value}\"")
            
            if log_vars:
                all_lines = preserved_lines + [''] + ['# Logging Configuration'] + log_vars
            else:
                all_lines = preserved_lines
            
            with open(env_path, 'w') as f:
                f.write('\n'.join(all_lines))
                
            print(f"Updated .env file with {len(log_vars)} logging variables")
        except Exception as e:
            print(f"Failed to update .env file: {e}")
    
    def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Get configuration for a specific guild"""
        if guild_id not in self.guild_configs:
            self.guild_configs[guild_id] = {
                "colors": self.default_colors.copy(),
                "embed_settings": {
                    "show_timestamp": True,
                    "show_footer": True,
                    "show_author": True,
                    "include_buttons": True,
                    "include_user_profile": True,
                    "thumbnail_type": "user_avatar"
                }
            }
        return self.guild_configs[guild_id]
    
    def get_log_color(self, guild_id: int, event_type: str) -> discord.Color:
        """Get the color for a specific event type in a guild"""
        config = self.get_guild_config(guild_id)
        return discord.Color.from_rgb(
            *config["colors"].get(event_type, self.default_colors[event_type]).to_rgb()
        )
    
    log_group = app_commands.Group(name="logs", description="Configure Discord logging")
    
    @log_group.command(name="setup", description="Set up logging for this server")
    @app_commands.describe(
        channel="The channel to use for logging",
        log_type="The type of events to log",
        webhook_url="Optional webhook URL to use instead of a channel"
    )
    @app_commands.choices(log_type=[
        app_commands.Choice(name="All Events", value="all"),
        app_commands.Choice(name="Moderation Actions", value="mod"),
        app_commands.Choice(name="Message Events", value="message"),
        app_commands.Choice(name="Member Events", value="member"),
        app_commands.Choice(name="Voice Events", value="voice"),
        app_commands.Choice(name="Server Events", value="server")
    ])
    @app_commands.default_permissions(administrator=True)
    async def logs_setup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        log_type: app_commands.Choice[str],
        webhook_url: Optional[str] = None
    ):
        await interaction.response.defer(ephemeral=True)
        
        try:
            if webhook_url:
                if not webhook_url.startswith("https://discord.com/api/webhooks/"):
                    await interaction.followup.send("Invalid webhook URL. Please provide a valid Discord webhook URL.")
                    return
                
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(webhook_url, session=session)
                    try:
                        await webhook.send("Webhook test - this message will be deleted", wait=True)
                    except Exception as e:
                        await interaction.followup.send(f"Failed to send test message to webhook: {e}")
                        return
                
                os.environ[f"LOG_WEBHOOK_{interaction.guild.id}_{log_type.value}"] = webhook_url
            else:
                if not channel.permissions_for(interaction.guild.me).send_messages:
                    await interaction.followup.send(f"I don't have permission to send messages in {channel.mention}.")
                    return
                    
                if log_type.value == "all" or log_type.value == "mod":
                    os.environ[f"LOG_CHANNEL_{interaction.guild.id}"] = str(channel.id)
                    
                if log_type.value == "all" or log_type.value == "message":
                    os.environ[f"LOG_MESSAGE_CHANNEL_{interaction.guild.id}"] = str(channel.id)
                    
                if log_type.value == "all" or log_type.value == "member":
                    os.environ[f"LOG_MEMBER_CHANNEL_{interaction.guild.id}"] = str(channel.id)
                    
                if log_type.value == "all" or log_type.value == "voice":
                    os.environ[f"LOG_VOICE_CHANNEL_{interaction.guild.id}"] = str(channel.id)
                    
                if log_type.value == "all" or log_type.value == "server":
                    os.environ[f"LOG_SERVER_CHANNEL_{interaction.guild.id}"] = str(channel.id)
            
            self.update_env_file()
            
            embed = discord.Embed(
                title="Logging Setup",
                description=f"Logging has been set up for {log_type.name} in {channel.mention if not webhook_url else 'a webhook'}.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            
            if webhook_url:
                embed.add_field(name="Webhook Mode", value="Logs will be sent via webhook", inline=False)
            
            await interaction.followup.send(embed=embed)
            
            test_embed = discord.Embed(
                title="Logging System Activated",
                description=f"This channel will now receive logs for: {log_type.name}",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            test_embed.add_field(name="Setup By", value=interaction.user.mention)
            test_embed.add_field(name="Log Type", value=log_type.name)
            test_embed.add_field(name="Timestamp", value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            test_embed.add_field(
                name="Server Information",
                value=f"Name: {interaction.guild.name}\nID: {interaction.guild.id}\nMembers: {len(interaction.guild.members)}",
                inline=False
            )
            
            test_embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            test_embed.set_footer(text="Logging system is now active | Enhanced Logging Module")
            
            if webhook_url:
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(webhook_url, session=session)
                    await webhook.send(embed=test_embed)
            else:
                await channel.send(embed=test_embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @log_group.command(name="disable", description="Disable logging for this server")
    @app_commands.describe(
        log_type="The type of events to disable logging for"
    )
    @app_commands.choices(log_type=[
        app_commands.Choice(name="All Events", value="all"),
        app_commands.Choice(name="Moderation Actions", value="mod"),
        app_commands.Choice(name="Message Events", value="message"),
        app_commands.Choice(name="Member Events", value="member"),
        app_commands.Choice(name="Voice Events", value="voice"),
        app_commands.Choice(name="Server Events", value="server")
    ])
    @app_commands.default_permissions(administrator=True)
    async def logs_disable(
        self,
        interaction: discord.Interaction,
        log_type: app_commands.Choice[str]
    ):
        await interaction.response.defer(ephemeral=True)
        
        try:
            if log_type.value == "all" or log_type.value == "mod":
                if f"LOG_CHANNEL_{interaction.guild.id}" in os.environ:
                    del os.environ[f"LOG_CHANNEL_{interaction.guild.id}"]
                if f"LOG_WEBHOOK_{interaction.guild.id}_mod" in os.environ:
                    del os.environ[f"LOG_WEBHOOK_{interaction.guild.id}_mod"]
                
            if log_type.value == "all" or log_type.value == "message":
                if f"LOG_MESSAGE_CHANNEL_{interaction.guild.id}" in os.environ:
                    del os.environ[f"LOG_MESSAGE_CHANNEL_{interaction.guild.id}"]
                if f"LOG_WEBHOOK_{interaction.guild.id}_message" in os.environ:
                    del os.environ[f"LOG_WEBHOOK_{interaction.guild.id}_message"]
                
            if log_type.value == "all" or log_type.value == "member":
                if f"LOG_MEMBER_CHANNEL_{interaction.guild.id}" in os.environ:
                    del os.environ[f"LOG_MEMBER_CHANNEL_{interaction.guild.id}"]
                if f"LOG_WEBHOOK_{interaction.guild.id}_member" in os.environ:
                    del os.environ[f"LOG_WEBHOOK_{interaction.guild.id}_member"]
                
            if log_type.value == "all" or log_type.value == "voice":
                if f"LOG_VOICE_CHANNEL_{interaction.guild.id}" in os.environ:
                    del os.environ[f"LOG_VOICE_CHANNEL_{interaction.guild.id}"]
                if f"LOG_WEBHOOK_{interaction.guild.id}_voice" in os.environ:
                    del os.environ[f"LOG_WEBHOOK_{interaction.guild.id}_voice"]
                
            if log_type.value == "all" or log_type.value == "server":
                if f"LOG_SERVER_CHANNEL_{interaction.guild.id}" in os.environ:
                    del os.environ[f"LOG_SERVER_CHANNEL_{interaction.guild.id}"]
                if f"LOG_WEBHOOK_{interaction.guild.id}_server" in os.environ:
                    del os.environ[f"LOG_WEBHOOK_{interaction.guild.id}_server"]
            
            self.update_env_file()
            
            embed = discord.Embed(
                title="Logging Disabled",
                description=f"Logging has been disabled for {log_type.name}.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @log_group.command(name="status", description="Check logging status for this server")
    @app_commands.default_permissions(administrator=True)
    async def logs_status(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer(ephemeral=True)
        
        try:
            embed = discord.Embed(
                title="Logging Status",
                description=f"Current logging configuration for {interaction.guild.name}",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            mod_channel_id = os.getenv(f"LOG_CHANNEL_{interaction.guild.id}")
            message_channel_id = os.getenv(f"LOG_MESSAGE_CHANNEL_{interaction.guild.id}")
            member_channel_id = os.getenv(f"LOG_MEMBER_CHANNEL_{interaction.guild.id}")
            voice_channel_id = os.getenv(f"LOG_VOICE_CHANNEL_{interaction.guild.id}")
            server_channel_id = os.getenv(f"LOG_SERVER_CHANNEL_{interaction.guild.id}")
            
            mod_webhook = os.getenv(f"LOG_WEBHOOK_{interaction.guild.id}_mod")
            message_webhook = os.getenv(f"LOG_WEBHOOK_{interaction.guild.id}_message")
            member_webhook = os.getenv(f"LOG_WEBHOOK_{interaction.guild.id}_member")
            voice_webhook = os.getenv(f"LOG_WEBHOOK_{interaction.guild.id}_voice")
            server_webhook = os.getenv(f"LOG_WEBHOOK_{interaction.guild.id}_server")

            if mod_channel_id or mod_webhook:
                if mod_channel_id:
                    channel = interaction.guild.get_channel(int(mod_channel_id))
                    embed.add_field(
                        name="Moderation Logs",
                        value=f"Enabled in {channel.mention if channel else 'Unknown Channel'}"
                    )
                else:
                    embed.add_field(name="Moderation Logs", value="Enabled via webhook")
            else:
                embed.add_field(name="Moderation Logs", value="Disabled")
                
            if message_channel_id or message_webhook:
                if message_channel_id:
                    channel = interaction.guild.get_channel(int(message_channel_id))
                    embed.add_field(
                        name="Message Logs",
                        value=f"Enabled in {channel.mention if channel else 'Unknown Channel'}"
                    )
                else:
                    embed.add_field(name="Message Logs", value="Enabled via webhook")
            else:
                embed.add_field(name="Message Logs", value="Disabled")
                
            if member_channel_id or member_webhook:
                if member_channel_id:
                    channel = interaction.guild.get_channel(int(member_channel_id))
                    embed.add_field(
                        name="Member Logs",
                        value=f"Enabled in {channel.mention if channel else 'Unknown Channel'}"
                    )
                else:
                    embed.add_field(name="Member Logs", value="Enabled via webhook")
            else:
                embed.add_field(name="Member Logs", value="Disabled")
                
            if voice_channel_id or voice_webhook:
                if voice_channel_id:
                    channel = interaction.guild.get_channel(int(voice_channel_id))
                    embed.add_field(
                        name="Voice Logs",
                        value=f"Enabled in {channel.mention if channel else 'Unknown Channel'}"
                    )
                else:
                    embed.add_field(name="Voice Logs", value="Enabled via webhook")
            else:
                embed.add_field(name="Voice Logs", value="Disabled")
                
            if server_channel_id or server_webhook:
                if server_channel_id:
                    channel = interaction.guild.get_channel(int(server_channel_id))
                    embed.add_field(
                        name="Server Logs",
                        value=f"Enabled in {channel.mention if channel else 'Unknown Channel'}"
                    )
                else:
                    embed.add_field(name="Server Logs", value="Enabled via webhook")
            else:
                embed.add_field(name="Server Logs", value="Disabled")
            
            config = self.get_guild_config(interaction.guild.id)
            embed.add_field(
                name="Custom Configuration",
                value="Custom colors and settings are enabled" if interaction.guild.id in self.guild_configs else "Using default settings",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @log_group.command(name="customize", description="Customize logging appearance")
    @app_commands.describe(
        setting="The setting to customize",
        value="The value to set (for colors, use hex code like #FF0000)"
    )
    @app_commands.choices(setting=[
        app_commands.Choice(name="Message Delete Color", value="color_message_delete"),
        app_commands.Choice(name="Message Edit Color", value="color_message_edit"),
        app_commands.Choice(name="Member Join Color", value="color_member_join"),
        app_commands.Choice(name="Member Leave Color", value="color_member_leave"),
        app_commands.Choice(name="Voice Event Color", value="color_voice"),
        app_commands.Choice(name="Channel Event Color", value="color_channel"),
        app_commands.Choice(name="Role Event Color", value="color_role"),
        app_commands.Choice(name="Show Timestamps", value="show_timestamp"),
        app_commands.Choice(name="Show Footer", value="show_footer"),
        app_commands.Choice(name="Show Author", value="show_author"),
        app_commands.Choice(name="Include Buttons", value="include_buttons"),
        app_commands.Choice(name="Include User Profile", value="include_user_profile"),
        app_commands.Choice(name="Thumbnail Type", value="thumbnail_type")
    ])
    @app_commands.default_permissions(administrator=True)
    async def logs_customize(
        self,
        interaction: discord.Interaction,
        setting: app_commands.Choice[str],
        value: str
    ):
        await interaction.response.defer(ephemeral=True)
        
        try:
            config = self.get_guild_config(interaction.guild.id)
            setting_key = setting.value
            
            if setting_key.startswith("color_"):
                event_type = setting_key.replace("color_", "")
                
                if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value):
                    await interaction.followup.send("Invalid color format. Please use hex format (e.g., #FF0000 for red).")
                    return
                
                value = value.lstrip('#')
                rgb = tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
                
                config["colors"][event_type] = discord.Color.from_rgb(*rgb)
                
                await interaction.followup.send(f"Updated {setting.name} to {value}")
            
            elif setting_key in ["show_timestamp", "show_footer", "show_author", "include_buttons", "include_user_profile"]:
                if value.lower() in ["true", "yes", "1", "on"]:
                    config["embed_settings"][setting_key] = True
                    await interaction.followup.send(f"Enabled {setting.name}")
                elif value.lower() in ["false", "no", "0", "off"]:
                    config["embed_settings"][setting_key] = False
                    await interaction.followup.send(f"Disabled {setting.name}")
                else:
                    await interaction.followup.send("Invalid value. Please use 'true' or 'false'.")
                    return
            
            elif setting_key == "thumbnail_type":
                if value.lower() in ["user_avatar", "guild_icon", "none"]:
                    config["embed_settings"][setting_key] = value.lower()
                    await interaction.followup.send(f"Set {setting.name} to {value.lower()}")
                else:
                    await interaction.followup.send("Invalid value. Please use 'user_avatar', 'guild_icon', or 'none'.")
                    return
            
            self.save_configs()
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @log_group.command(name="reset", description="Reset logging customization to defaults")
    @app_commands.default_permissions(administrator=True)
    async def logs_reset(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer(ephemeral=True)
        
        try:
            if interaction.guild.id in self.guild_configs:
                del self.guild_configs[interaction.guild.id]
                self.save_configs()
                
            await interaction.followup.send("Logging customization has been reset to default settings.")
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log deleted messages with enhanced details"""
        if message.guild is None or message.author.bot:
            return
            
        log_channel_id = os.getenv(f"LOG_MESSAGE_CHANNEL_{message.guild.id}")
        webhook_url = os.getenv(f"LOG_WEBHOOK_{message.guild.id}_message")
        
        if not log_channel_id and not webhook_url:
            return
            
        try:
            config = self.get_guild_config(message.guild.id)
            embed_settings = config["embed_settings"]
            
            embed = discord.Embed(
                title="📝 Message Deleted",
                description=f"A message was deleted in {message.channel.mention}",
                color=self.get_log_color(message.guild.id, "message_delete"),
                timestamp=datetime.datetime.now() if embed_settings["show_timestamp"] else None
            )
            
            if embed_settings["show_author"]:
                embed.set_author(
                    name=f"{message.author.name}#{message.author.discriminator}",
                    icon_url=message.author.display_avatar.url
                )
            
            if message.content:
                content = message.content
                if len(content) > 4000:
                    content = content[:3997] + "..."
                embed.add_field(name="Content", value=content, inline=False)
            
            if message.attachments:
                files_info = []
                for attachment in message.attachments:
                    file_type = "Unknown"
                    if attachment.content_type:
                        file_type = attachment.content_type
                    
                    size_bytes = attachment.size
                    if size_bytes < 1024:
                        size_str = f"{size_bytes} B"
                    elif size_bytes < 1024 * 1024:
                        size_str = f"{size_bytes/1024:.2f} KB"
                    else:
                        size_str = f"{size_bytes/(1024*1024):.2f} MB"
                    
                    files_info.append(f"[{attachment.filename}]({attachment.proxy_url}) ({size_str}, {file_type})")
                
                embed.add_field(name=f"Attachments [{len(message.attachments)}]", value="\n".join(files_info), inline=False)
            
            metadata = []
            metadata.append(f"**Channel:** {message.channel.mention} (ID: {message.channel.id})")
            metadata.append(f"**Message ID:** {message.id}")
            metadata.append(f"**Created:** <t:{int(message.created_at.timestamp())}:F> (<t:{int(message.created_at.timestamp())}:R>)")
            
            if message.edited_at:
                metadata.append(f"**Last Edited:** <t:{int(message.edited_at.timestamp())}:F> (<t:{int(message.edited_at.timestamp())}:R>)")
            
            embed.add_field(name="Message Details", value="\n".join(metadata), inline=False)
            
            user_info = []
            user_info.append(f"**User:** {message.author.mention} (ID: {message.author.id})")
            user_info.append(f"**Created:** <t:{int(message.author.created_at.timestamp())}:F> (<t:{int(message.author.created_at.timestamp())}:R>)")
            
            if hasattr(message.author, "joined_at") and message.author.joined_at:
                user_info.append(f"**Joined:** <t:{int(message.author.joined_at.timestamp())}:F> (<t:{int(message.author.joined_at.timestamp())}:R>)")
            
            if hasattr(message.author, "roles") and len(message.author.roles) > 1:
                top_role = message.author.top_role
                user_info.append(f"**Top Role:** {top_role.mention}")
            
            embed.add_field(name="User Details", value="\n".join(user_info), inline=False)
            
            if embed_settings["thumbnail_type"] == "user_avatar":
                embed.set_thumbnail(url=message.author.display_avatar.url)
            elif embed_settings["thumbnail_type"] == "guild_icon" and message.guild.icon:
                embed.set_thumbnail(url=message.guild.icon.url)
            
            if embed_settings["show_footer"]:
                embed.set_footer(text=f"Message ID: {message.id} | User ID: {message.author.id}")
            
            view = None
            if embed_settings["include_buttons"]:
                view = View(timeout=300)
                if embed_settings["include_user_profile"]:
                    view.add_item(Button(
                        label="User Profile", 
                        url=f"discord://-/users/{message.author.id}", 
                        style=discord.ButtonStyle.link
                    ))
            
            if webhook_url:
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(webhook_url, session=session)
                    await webhook.send(embed=embed, view=view)
            else:
                log_channel = message.guild.get_channel(int(log_channel_id))
                if log_channel:
                    await log_channel.send(embed=embed, view=view)
            
        except Exception as e:
            print(f"Failed to log message deletion: {e}")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log edited messages with enhanced details and navigation"""
        if before.guild is None or before.author.bot or before.content == after.content:
            return
            
        log_channel_id = os.getenv(f"LOG_MESSAGE_CHANNEL_{before.guild.id}")
        webhook_url = os.getenv(f"LOG_WEBHOOK_{before.guild.id}_message")
        
        if not log_channel_id and not webhook_url:
            return
            
        try:
            config = self.get_guild_config(before.guild.id)
            embed_settings = config["embed_settings"]
            
            embed = discord.Embed(
                title="✏️ Message Edited",
                description=f"A message was edited in {before.channel.mention}",
                color=self.get_log_color(before.guild.id, "message_edit"),
                timestamp=datetime.datetime.now() if embed_settings["show_timestamp"] else None
            )

            if embed_settings["show_author"]:
                embed.set_author(
                    name=f"{before.author.name}#{before.author.discriminator}",
                    icon_url=before.author.display_avatar.url
                )
            
            before_content = before.content
            if len(before_content) > 1024:
                before_content = before_content[:1021] + "..."
                
            after_content = after.content
            if len(after_content) > 1024:
                after_content = after_content[:1021] + "..."
                
            embed.add_field(name="Before", value=f"```{before_content}```", inline=False)
            embed.add_field(name="After", value=f"```{after_content}```", inline=False)
            
            metadata = []
            metadata.append(f"**Channel:** {before.channel.mention} (ID: {before.channel.id})")
            metadata.append(f"**Message ID:** {before.id}")
            metadata.append(f"**Created:** <t:{int(before.created_at.timestamp())}:F> (<t:{int(before.created_at.timestamp())}:R>)")
            metadata.append(f"**Edited:** <t:{int(datetime.datetime.now().timestamp())}:F> (<t:{int(datetime.datetime.now().timestamp())}:R>)")
            
            embed.add_field(name="Message Details", value="\n".join(metadata), inline=False)
            
            user_info = []
            user_info.append(f"**User:** {before.author.mention} (ID: {before.author.id})")
            user_info.append(f"**Created:** <t:{int(before.author.created_at.timestamp())}:F> (<t:{int(before.author.created_at.timestamp())}:R>)")
            
            if hasattr(before.author, "joined_at") and before.author.joined_at:
                user_info.append(f"**Joined:** <t:{int(before.author.joined_at.timestamp())}:F> (<t:{int(before.author.joined_at.timestamp())}:R>)")
            
            if hasattr(before.author, "roles") and len(before.author.roles) > 1:
                top_role = before.author.top_role
                user_info.append(f"**Top Role:** {top_role.mention}")
            
            embed.add_field(name="User Details", value="\n".join(user_info), inline=False)
            
            if embed_settings["thumbnail_type"] == "user_avatar":
                embed.set_thumbnail(url=before.author.display_avatar.url)
            elif embed_settings["thumbnail_type"] == "guild_icon" and before.guild.icon:
                embed.set_thumbnail(url=before.guild.icon.url)
            
            embed.add_field(name="Jump to Message", value=f"[Click to see message]({before.jump_url})", inline=False)
            
            if embed_settings["show_footer"]:
                embed.set_footer(text=f"Message ID: {before.id} | User ID: {before.author.id}")
            
            view = None
            if embed_settings["include_buttons"]:
                view = LogNavigationView(before.jump_url, before.author)
            
            if webhook_url:
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(webhook_url, session=session)
                    await webhook.send(embed=embed, view=view)
            else:
                log_channel = before.guild.get_channel(int(log_channel_id))
                if log_channel:
                    await log_channel.send(embed=embed, view=view)
            
        except Exception as e:
            print(f"Failed to log message edit: {e}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Log member joins with enhanced details"""
        log_channel_id = os.getenv(f"LOG_MEMBER_CHANNEL_{member.guild.id}")
        webhook_url = os.getenv(f"LOG_WEBHOOK_{member.guild.id}_member")
        
        if not log_channel_id and not webhook_url:
            return
            
        try:
            config = self.get_guild_config(member.guild.id)
            embed_settings = config["embed_settings"]
            
            embed = discord.Embed(
                title="👋 Member Joined",
                description=f"{member.mention} joined the server",
                color=self.get_log_color(member.guild.id, "member_join"),
                timestamp=datetime.datetime.now() if embed_settings["show_timestamp"] else None
            )
            
            if embed_settings["show_author"]:
                embed.set_author(
                    name=f"{member.name}#{member.discriminator}",
                    icon_url=member.display_avatar.url
                )
            
            user_info = []
            user_info.append(f"**User:** {member.mention} (ID: {member.id})")
            user_info.append(f"**Account Created:** <t:{int(member.created_at.timestamp())}:F> (<t:{int(member.created_at.timestamp())}:R>)")
            
            account_age = (datetime.datetime.utcnow() - member.created_at).days
            user_info.append(f"**Account Age:** {account_age} days")
            
            if account_age < 7:
                user_info.append(f"⚠️ **Warning:** This account is less than a week old")
            
            embed.add_field(name="User Details", value="\n".join(user_info), inline=False)
            
            server_info = []
            server_info.append(f"**Server:** {member.guild.name}")
            server_info.append(f"**Member Count:** {len(member.guild.members)}")
            server_info.append(f"**Joined:** <t:{int(datetime.datetime.utcnow().timestamp())}:F>")
            
            embed.add_field(name="Server Details", value="\n".join(server_info), inline=False)
            
            if embed_settings["thumbnail_type"] == "user_avatar":
                embed.set_thumbnail(url=member.display_avatar.url)
            elif embed_settings["thumbnail_type"] == "guild_icon" and member.guild.icon:
                embed.set_thumbnail(url=member.guild.icon.url)
            
            if embed_settings["show_footer"]:
                embed.set_footer(text=f"Member #{len(member.guild.members)} | User ID: {member.id}")
            
            view = None
            if embed_settings["include_buttons"] and embed_settings["include_user_profile"]:
                view = View(timeout=300)
                view.add_item(Button(
                    label="User Profile", 
                    url=f"discord://-/users/{member.id}", 
                    style=discord.ButtonStyle.link
                ))
            
            if webhook_url:
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(webhook_url, session=session)
                    await webhook.send(embed=embed, view=view)
            else:
                log_channel = member.guild.get_channel(int(log_channel_id))
                if log_channel:
                    await log_channel.send(embed=embed, view=view)
            
        except Exception as e:
            print(f"Failed to log member join: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log member leaves with enhanced details"""
        log_channel_id = os.getenv(f"LOG_MEMBER_CHANNEL_{member.guild.id}")
        webhook_url = os.getenv(f"LOG_WEBHOOK_{member.guild.id}_member")
        
        if not log_channel_id and not webhook_url:
            return
            
        try:
            config = self.get_guild_config(member.guild.id)
            embed_settings = config["embed_settings"]
            
            embed = discord.Embed(
                title="👋 Member Left",
                description=f"{member.mention} left the server",
                color=self.get_log_color(member.guild.id, "member_leave"),
                timestamp=datetime.datetime.now() if embed_settings["show_timestamp"] else None
            )
            
            if embed_settings["show_author"]:
                embed.set_author(
                    name=f"{member.name}#{member.discriminator}",
                    icon_url=member.display_avatar.url
                )
            
            user_info = []
            user_info.append(f"**User:** {member.mention} (ID: {member.id})")
            user_info.append(f"**Account Created:** <t:{int(member.created_at.timestamp())}:F> (<t:{int(member.created_at.timestamp())}:R>)")
            
            if member.joined_at:
                user_info.append(f"**Joined Server:** <t:{int(member.joined_at.timestamp())}:F> (<t:{int(member.joined_at.timestamp())}:R>)")
                
                now = datetime.datetime.utcnow()
                joined_at = member.joined_at.replace(tzinfo=None) if member.joined_at.tzinfo else member.joined_at
                time_in_server = now - joined_at
                days = time_in_server.days
                hours, remainder = divmod(time_in_server.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                time_str = []
                if days > 0:
                    time_str.append(f"{days} days")
                if hours > 0:
                    time_str.append(f"{hours} hours")
                if minutes > 0:
                    time_str.append(f"{minutes} minutes")
                
                user_info.append(f"**Time in Server:** {', '.join(time_str)}")
            
            embed.add_field(name="User Details", value="\n".join(user_info), inline=False)
            
            if len(member.roles) > 1:
                roles = [role.mention for role in member.roles if role.name != "@everyone"]
                roles_text = ", ".join(roles)
                if len(roles_text) > 1024:
                    roles_text = roles_text[:1021] + "..."
                embed.add_field(name=f"Roles [{len(roles)}]", value=roles_text, inline=False)
            
            server_info = []
            server_info.append(f"**Server:** {member.guild.name}")
            server_info.append(f"**Member Count:** {len(member.guild.members)} (after leave)")
            server_info.append(f"**Left:** <t:{int(datetime.datetime.utcnow().timestamp())}:F>")
            
            embed.add_field(name="Server Details", value="\n".join(server_info), inline=False)
            
            if embed_settings["thumbnail_type"] == "user_avatar":
                embed.set_thumbnail(url=member.display_avatar.url)
            elif embed_settings["thumbnail_type"] == "guild_icon" and member.guild.icon:
                embed.set_thumbnail(url=member.guild.icon.url)
            
            if embed_settings["show_footer"]:
                embed.set_footer(text=f"Member left | Now {len(member.guild.members)} members | User ID: {member.id}")
            
            view = None
            if embed_settings["include_buttons"] and embed_settings["include_user_profile"]:
                view = View(timeout=300)
                view.add_item(Button(
                    label="User Profile", 
                    url=f"discord://-/users/{member.id}", 
                    style=discord.ButtonStyle.link
                ))
            
            if webhook_url:
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(webhook_url, session=session)
                    await webhook.send(embed=embed, view=view)
            else:
                log_channel = member.guild.get_channel(int(log_channel_id))
                if log_channel:
                    await log_channel.send(embed=embed, view=view)
            
        except Exception as e:
            print(f"Failed to log member leave: {e}")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Log voice state changes with enhanced details"""
        if before.channel == after.channel and before.self_mute == after.self_mute and before.self_deaf == after.self_deaf and before.self_stream == after.self_stream and before.self_video == after.self_video:
            return
            
        log_channel_id = os.getenv(f"LOG_VOICE_CHANNEL_{member.guild.id}")
        webhook_url = os.getenv(f"LOG_WEBHOOK_{member.guild.id}_voice")
        
        if not log_channel_id and not webhook_url:
            return
            
        try:
            config = self.get_guild_config(member.guild.id)
            embed_settings = config["embed_settings"]
            
            if before.channel is None and after.channel is not None:
                title = "🔊 Voice Channel Joined"
                description = f"{member.mention} joined voice channel {after.channel.mention}"
                color = discord.Color.green()
                action = "joined"
            elif before.channel is not None and after.channel is None:
                title = "🔊 Voice Channel Left"
                description = f"{member.mention} left voice channel {before.channel.mention}"
                color = discord.Color.red()
                action = "left"
            elif before.channel != after.channel:
                title = "🔊 Voice Channel Moved"
                description = f"{member.mention} moved from {before.channel.mention} to {after.channel.mention}"
                color = discord.Color.blue()
                action = "moved"
            elif before.self_mute != after.self_mute:
                if after.self_mute:
                    title = "🔊 Member Self-Muted"
                    description = f"{member.mention} muted themselves in {after.channel.mention}"
                    action = "self-muted"
                else:
                    title = "🔊 Member Self-Unmuted"
                    description = f"{member.mention} unmuted themselves in {after.channel.mention}"
                    action = "self-unmuted"
                color = discord.Color.gold()
            elif before.self_deaf != after.self_deaf:
                if after.self_deaf:
                    title = "🔊 Member Self-Deafened"
                    description = f"{member.mention} deafened themselves in {after.channel.mention}"
                    action = "self-deafened"
                else:
                    title = "🔊 Member Self-Undeafened"
                    description = f"{member.mention} undeafened themselves in {after.channel.mention}"
                    action = "self-undeafened"
                color = discord.Color.gold()
            elif before.self_stream != after.self_stream:
                if after.self_stream:
                    title = "🔊 Member Started Streaming"
                    description = f"{member.mention} started streaming in {after.channel.mention}"
                    action = "started streaming"
                else:
                    title = "🔊 Member Stopped Streaming"
                    description = f"{member.mention} stopped streaming in {after.channel.mention}"
                    action = "stopped streaming"
                color = discord.Color.purple()
            elif before.self_video != after.self_video:
                if after.self_video:
                    title = "🔊 Member Started Video"
                    description = f"{member.mention} turned on their camera in {after.channel.mention}"
                    action = "started video"
                else:
                    title = "🔊 Member Stopped Video"
                    description = f"{member.mention} turned off their camera in {after.channel.mention}"
                    action = "stopped video"
                color = discord.Color.purple()
            else:
                title = "🔊 Voice State Updated"
                description = f"{member.mention}'s voice state was updated in {after.channel.mention if after.channel else before.channel.mention}"
                color = discord.Color.blurple()
                action = "updated voice state"
            
            embed = discord.Embed(
                title=title,
                description=description,
                color=self.get_log_color(member.guild.id, "voice"),
                timestamp=datetime.datetime.now() if embed_settings["show_timestamp"] else None
            )
            
            if embed_settings["show_author"]:
                embed.set_author(
                    name=f"{member.name}#{member.discriminator}",
                    icon_url=member.display_avatar.url
                )
            
            user_info = []
            user_info.append(f"**User:** {member.mention} (ID: {member.id})")
            
            if hasattr(member, "joined_at") and member.joined_at:
                user_info.append(f"**Joined Server:** <t:{int(member.joined_at.timestamp())}:R>")
            
            if hasattr(member, "roles") and len(member.roles) > 1:
                top_role = member.top_role
                user_info.append(f"**Top Role:** {top_role.mention}")
            
            embed.add_field(name="User Details", value="\n".join(user_info), inline=False)
            
            voice_details = []
            
            if before.channel and after.channel and before.channel != after.channel:
                voice_details.append(f"**From Channel:** {before.channel.mention} (ID: {before.channel.id})")
                voice_details.append(f"**To Channel:** {after.channel.mention} (ID: {after.channel.id})")
            elif before.channel and not after.channel:
                voice_details.append(f"**Left Channel:** {before.channel.mention} (ID: {before.channel.id})")
            elif not before.channel and after.channel:
                voice_details.append(f"**Joined Channel:** {after.channel.mention} (ID: {after.channel.id})")
            elif after.channel:
                voice_details.append(f"**Channel:** {after.channel.mention} (ID: {after.channel.id})")
            
            if before.self_mute != after.self_mute:
                voice_details.append(f"**Self Mute:** {before.self_mute} → {after.self_mute}")
            elif after.self_mute:
                voice_details.append(f"**Self Mute:** {after.self_mute}")
                
            if before.self_deaf != after.self_deaf:
                voice_details.append(f"**Self Deaf:** {before.self_deaf} → {after.self_deaf}")
            elif after.self_deaf:
                voice_details.append(f"**Self Deaf:** {after.self_deaf}")
                
            if before.self_stream != after.self_stream:
                voice_details.append(f"**Streaming:** {before.self_stream} → {after.self_stream}")
            elif after.self_stream:
                voice_details.append(f"**Streaming:** {after.self_stream}")
                
            if before.self_video != after.self_video:
                voice_details.append(f"**Video:** {before.self_video} → {after.self_video}")
            elif after.self_video:
                voice_details.append(f"**Video:** {after.self_video}")
                
            if before.mute != after.mute:
                voice_details.append(f"**Server Mute:** {before.mute} → {after.mute}")
            elif after.mute:
                voice_details.append(f"**Server Mute:** {after.mute}")
                
            if before.deaf != after.deaf:
                voice_details.append(f"**Server Deaf:** {before.deaf} → {after.deaf}")
            elif after.deaf:
                voice_details.append(f"**Server Deaf:** {after.deaf}")
            
            voice_details.append(f"**Timestamp:** <t:{int(datetime.datetime.now().timestamp())}:F>")
            
            embed.add_field(name="Voice State Details", value="\n".join(voice_details), inline=False)
            
            if embed_settings["thumbnail_type"] == "user_avatar":
                embed.set_thumbnail(url=member.display_avatar.url)
            elif embed_settings["thumbnail_type"] == "guild_icon" and member.guild.icon:
                embed.set_thumbnail(url=member.guild.icon.url)
            
            if embed_settings["show_footer"]:
                embed.set_footer(text=f"Voice State Update | User ID: {member.id}")
            
            view = None
            if embed_settings["include_buttons"] and embed_settings["include_user_profile"]:
                view = View(timeout=300)
                view.add_item(Button(
                    label="User Profile", 
                    url=f"discord://-/users/{member.id}", 
                    style=discord.ButtonStyle.link
                ))
                
                if after.channel:
                    view.add_item(Button(
                        label=f"Go to {after.channel.name}", 
                        url=f"discord://-/channels/{member.guild.id}/{after.channel.id}", 
                        style=discord.ButtonStyle.link
                    ))
            
            if webhook_url:
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(webhook_url, session=session)
                    await webhook.send(embed=embed, view=view)
            else:
                log_channel = member.guild.get_channel(int(log_channel_id))
                if log_channel:
                    await log_channel.send(embed=embed, view=view)
            
        except Exception as e:
            print(f"Failed to log voice state update: {e}")
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Log channel creation with enhanced details"""
        log_channel_id = os.getenv(f"LOG_SERVER_CHANNEL_{channel.guild.id}")
        webhook_url = os.getenv(f"LOG_WEBHOOK_{channel.guild.id}_server")
        
        if not log_channel_id and not webhook_url:
            return
            
        try:
            config = self.get_guild_config(channel.guild.id)
            embed_settings = config["embed_settings"]
            
            embed = discord.Embed(
                title="📝 Channel Created",
                description=f"A new channel was created: {channel.mention}",
                color=self.get_log_color(channel.guild.id, "channel"),
                timestamp=datetime.datetime.now() if embed_settings["show_timestamp"] else None
            )
            
            channel_info = []
            channel_info.append(f"**Name:** {channel.name}")
            channel_info.append(f"**ID:** {channel.id}")
            channel_info.append(f"**Type:** {str(channel.type).replace('_', ' ').title()}")
            
            if hasattr(channel, "category") and channel.category:
                channel_info.append(f"**Category:** {channel.category.name}")
                
            if hasattr(channel, "position"):
                channel_info.append(f"**Position:** {channel.position}")
                
            if hasattr(channel, "nsfw"):
                channel_info.append(f"**NSFW:** {channel.nsfw}")
                
            if hasattr(channel, "slowmode_delay") and channel.slowmode_delay > 0:
                channel_info.append(f"**Slowmode:** {channel.slowmode_delay} seconds")
                
            channel_info.append(f"**Created:** <t:{int(channel.created_at.timestamp())}:F>")
            
            embed.add_field(name="Channel Details", value="\n".join(channel_info), inline=False)
            
            if embed_settings["thumbnail_type"] == "guild_icon" and channel.guild.icon:
                embed.set_thumbnail(url=channel.guild.icon.url)
            
            if embed_settings["show_footer"]:
                embed.set_footer(text=f"Channel ID: {channel.id}")
            
            view = None
            if embed_settings["include_buttons"]:
                view = View(timeout=300)
                view.add_item(Button(
                    label=f"Go to Channel", 
                    url=f"discord://-/channels/{channel.guild.id}/{channel.id}", 
                    style=discord.ButtonStyle.link
                ))
            
            if webhook_url:
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(webhook_url, session=session)
                    await webhook.send(embed=embed, view=view)
            else:
                log_channel = channel.guild.get_channel(int(log_channel_id))
                if log_channel:
                    await log_channel.send(embed=embed, view=view)
            
        except Exception as e:
            print(f"Failed to log channel creation: {e}")
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Log channel deletion with enhanced details"""
        log_channel_id = os.getenv(f"LOG_SERVER_CHANNEL_{channel.guild.id}")
        webhook_url = os.getenv(f"LOG_WEBHOOK_{channel.guild.id}_server")
        
        if not log_channel_id and not webhook_url:
            return
            
        try:
            config = self.get_guild_config(channel.guild.id)
            embed_settings = config["embed_settings"]
            
            embed = discord.Embed(
                title="📝 Channel Deleted",
                description=f"A channel was deleted: #{channel.name}",
                color=self.get_log_color(channel.guild.id, "channel"),
                timestamp=datetime.datetime.now() if embed_settings["show_timestamp"] else None
            )
            
            channel_info = []
            channel_info.append(f"**Name:** {channel.name}")
            channel_info.append(f"**ID:** {channel.id}")
            channel_info.append(f"**Type:** {str(channel.type).replace('_', ' ').title()}")
            
            if hasattr(channel, "category") and channel.category:
                channel_info.append(f"**Category:** {channel.category.name}")
                
            channel_info.append(f"**Created:** <t:{int(channel.created_at.timestamp())}:F>")
            channel_info.append(f"**Deleted:** <t:{int(datetime.datetime.now().timestamp())}:F>")
            
            embed.add_field(name="Channel Details", value="\n".join(channel_info), inline=False)
            
            if embed_settings["thumbnail_type"] == "guild_icon" and channel.guild.icon:
                embed.set_thumbnail(url=channel.guild.icon.url)
            
            if embed_settings["show_footer"]:
                embed.set_footer(text=f"Channel ID: {channel.id}")
            
            if webhook_url:
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(webhook_url, session=session)
                    await webhook.send(embed=embed)
            else:
                log_channel = channel.guild.get_channel(int(log_channel_id))
                if log_channel:
                    await log_channel.send(embed=embed)
            
        except Exception as e:
            print(f"Failed to log channel deletion: {e}")
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """Log role creation with enhanced details"""
        log_channel_id = os.getenv(f"LOG_SERVER_CHANNEL_{role.guild.id}")
        webhook_url = os.getenv(f"LOG_WEBHOOK_{role.guild.id}_server")
        
        if not log_channel_id and not webhook_url:
            return
            
        try:
            config = self.get_guild_config(role.guild.id)
            embed_settings = config["embed_settings"]
            
            embed = discord.Embed(
                title="📝 Role Created",
                description=f"A new role was created: {role.mention}",
                color=role.color,
                timestamp=datetime.datetime.now() if embed_settings["show_timestamp"] else None
            )
            
            role_info = []
            role_info.append(f"**Name:** {role.name}")
            role_info.append(f"**ID:** {role.id}")
            role_info.append(f"**Color:** {str(role.color)}")
            role_info.append(f"**Position:** {role.position}")
            role_info.append(f"**Mentionable:** {role.mentionable}")
            role_info.append(f"**Hoisted:** {role.hoist}")
            
            role_info.append(f"**Created:** <t:{int(role.created_at.timestamp())}:F>")
            
            embed.add_field(name="Role Details", value="\n".join(role_info), inline=False)
            
            permissions = []
            for perm, value in role.permissions:
                if value:
                    permissions.append(f"`{perm.replace('_', ' ').title()}`")
            
            if permissions:
                embed.add_field(name="Permissions", value=", ".join(permissions), inline=False)
            
            if embed_settings["thumbnail_type"] == "guild_icon" and role.guild.icon:
                embed.set_thumbnail(url=role.guild.icon.url)
            
            if embed_settings["show_footer"]:
                embed.set_footer(text=f"Role ID: {role.id}")
            
            if webhook_url:
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(webhook_url, session=session)
                    await webhook.send(embed=embed)
            else:
                log_channel = role.guild.get_channel(int(log_channel_id))
                if log_channel:
                    await log_channel.send(embed=embed)
            
        except Exception as e:
            print(f"Failed to log role creation: {e}")
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Log role deletion with enhanced details"""
        log_channel_id = os.getenv(f"LOG_SERVER_CHANNEL_{role.guild.id}")
        webhook_url = os.getenv(f"LOG_WEBHOOK_{role.guild.id}_server")
        
        if not log_channel_id and not webhook_url:
            return
            
        try:
            config = self.get_guild_config(role.guild.id)
            embed_settings = config["embed_settings"]
            
            embed = discord.Embed(
                title="📝 Role Deleted",
                description=f"A role was deleted: @{role.name}",
                color=role.color,
                timestamp=datetime.datetime.now() if embed_settings["show_timestamp"] else None
            )
            
            role_info = []
            role_info.append(f"**Name:** {role.name}")
            role_info.append(f"**ID:** {role.id}")
            role_info.append(f"**Color:** {str(role.color)}")
            role_info.append(f"**Position:** {role.position}")
            role_info.append(f"**Mentionable:** {role.mentionable}")
            role_info.append(f"**Hoisted:** {role.hoist}")
            
            role_info.append(f"**Created:** <t:{int(role.created_at.timestamp())}:F>")
            role_info.append(f"**Deleted:** <t:{int(datetime.datetime.now().timestamp())}:F>")
            
            embed.add_field(name="Role Details", value="\n".join(role_info), inline=False)
            
            if embed_settings["thumbnail_type"] == "guild_icon" and role.guild.icon:
                embed.set_thumbnail(url=role.guild.icon.url)
            
            if embed_settings["show_footer"]:
                embed.set_footer(text=f"Role ID: {role.id}")
            
            if webhook_url:
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(webhook_url, session=session)
                    await webhook.send(embed=embed)
            else:
                log_channel = role.guild.get_channel(int(log_channel_id))
                if log_channel:
                    await log_channel.send(embed=embed)
            
        except Exception as e:
            print(f"Failed to log role deletion: {e}")

async def setup(bot):
    await bot.add_cog(EnhancedLogging(bot))