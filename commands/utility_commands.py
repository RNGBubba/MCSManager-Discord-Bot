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
import datetime
import os
import time
import platform
import asyncio
import aiohttp
import json
import re
from typing import Optional, List

class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
        self.reminders = {}
        self.bot.loop.create_task(self.reminder_checker())
        
    utility_group = app_commands.Group(name="utility", description="Utility and helper commands")
    
    @utility_group.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        """Check the bot's latency"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        start_time = time.time()
        message = await interaction.followup.send("Pinging...")
        end_time = time.time()
        
        api_latency = round((end_time - start_time) * 1000)
        websocket_latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="API Latency", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="Websocket Latency", value=f"{websocket_latency}ms", inline=True)
        
        await message.edit(content=None, embed=embed)
    
    @utility_group.command(name="serverinfo", description="Get information about the server")
    async def serverinfo(self, interaction: discord.Interaction):
        """Get detailed information about the server"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        guild = interaction.guild
        
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        total_members = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = len([m for m in guild.members if m.bot])
        
        features = ", ".join(guild.features) if guild.features else "None"
        
        embed = discord.Embed(
            title=f"{guild.name} Server Information",
            description=guild.description or "No description",
            color=guild.me.color if guild.me.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Created On", value=f"<t:{int(guild.created_at.timestamp())}:F>\n(<t:{int(guild.created_at.timestamp())}:R>)", inline=True)
        
        embed.add_field(name="Members", value=f"Total: {total_members}\nHumans: {humans}\nBots: {bots}", inline=True)
        
        embed.add_field(name="Channels", value=f"Text: {text_channels}\nVoice: {voice_channels}\nCategories: {categories}", inline=True)
        
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        
        embed.add_field(name="Boost Level", value=f"Level {guild.premium_tier}", inline=True)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
        embed.add_field(name="Boosters", value=len(guild.premium_subscribers), inline=True)
        
        if features:
            embed.add_field(name="Server Features", value=features, inline=False)
        
        if guild.banner:
            embed.set_image(url=guild.banner.url)
            
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)
    
    @utility_group.command(name="userinfo", description="Get information about a user")
    @app_commands.describe(user="The user to get information about (defaults to yourself)")
    async def userinfo(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Get detailed information about a user"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        user = user or interaction.user
        
        roles = [role.mention for role in user.roles if role.name != "@everyone"]
        roles.reverse()
        
        sorted_members = sorted(interaction.guild.members, key=lambda m: m.joined_at or datetime.datetime.now())
        join_pos = sorted_members.index(user) + 1
        
        embed = discord.Embed(
            title=f"User Information - {user.display_name}",
            color=user.color if user.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        
        embed.add_field(name="User ID", value=user.id, inline=True)
        embed.add_field(name="Username", value=user.name, inline=True)
        embed.add_field(name="Discriminator", value=f"#{user.discriminator}" if user.discriminator != "0" else "None", inline=True)
        
        embed.add_field(name="Account Created", value=f"<t:{int(user.created_at.timestamp())}:F>\n(<t:{int(user.created_at.timestamp())}:R>)", inline=True)
        embed.add_field(name="Joined Server", value=f"<t:{int(user.joined_at.timestamp())}:F>\n(<t:{int(user.joined_at.timestamp())}:R>)" if user.joined_at else "Unknown", inline=True)
        embed.add_field(name="Join Position", value=f"{join_pos} of {len(interaction.guild.members)}", inline=True)
        
        status_emojis = {
            "online": "🟢",
            "idle": "🟡",
            "dnd": "🔴",
            "offline": "⚫"
        }
        
        status = status_emojis.get(str(user.status), "⚫")
        embed.add_field(name="Status", value=f"{status} {str(user.status).capitalize()}", inline=True)
        
        embed.add_field(name="Bot", value="Yes" if user.bot else "No", inline=True)
        
        if user.premium_since:
            embed.add_field(name="Boosting Since", value=f"<t:{int(user.premium_since.timestamp())}:F>\n(<t:{int(user.premium_since.timestamp())}:R>)", inline=True)
        
        if roles:
            embed.add_field(name=f"Roles [{len(roles)}]", value=" ".join(roles[:10]) + (f" and {len(roles) - 10} more..." if len(roles) > 10 else ""), inline=False)
        else:
            embed.add_field(name="Roles", value="None", inline=False)
        
        key_permissions = []
        permissions = user.guild_permissions
        
        if permissions.administrator:
            key_permissions.append("Administrator")
        else:
            if permissions.manage_guild:
                key_permissions.append("Manage Server")
            if permissions.ban_members:
                key_permissions.append("Ban Members")
            if permissions.kick_members:
                key_permissions.append("Kick Members")
            if permissions.manage_channels:
                key_permissions.append("Manage Channels")
            if permissions.manage_messages:
                key_permissions.append("Manage Messages")
            if permissions.manage_roles:
                key_permissions.append("Manage Roles")
            if permissions.mention_everyone:
                key_permissions.append("Mention Everyone")
            if permissions.manage_webhooks:
                key_permissions.append("Manage Webhooks")
            if permissions.manage_emojis:
                key_permissions.append("Manage Emojis")
        
        if key_permissions:
            embed.add_field(name="Key Permissions", value=", ".join(key_permissions), inline=False)
        
        if hasattr(user, "banner") and user.banner:
            embed.set_image(url=user.banner.url)
            
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        view = UserInfoView(interaction.user, user)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @utility_group.command(name="avatar", description="Get a user's avatar")
    @app_commands.describe(user="The user to get the avatar of (defaults to yourself)")
    async def avatar(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Get a user's avatar in full size"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        user = user or interaction.user
        
        embed = discord.Embed(
            title=f"{user.display_name}'s Avatar",
            color=user.color if user.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        view = AvatarView(user.display_avatar.url)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @utility_group.command(name="reminder", description="Set a reminder")
    @app_commands.describe(
        time="Time until reminder (e.g., 1h30m, 2d, 45s)",
        reminder="What to remind you about"
    )
    async def reminder(self, interaction: discord.Interaction, time: str, reminder: str):
        """Set a reminder for yourself"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        seconds = 0
        pattern = re.compile(r'(\d+)([dhms])')
        matches = pattern.findall(time.lower())
        
        if not matches:
            await interaction.followup.send("Invalid time format. Use a combination of d (days), h (hours), m (minutes), s (seconds). Example: 1h30m")
            return
            
        for value, unit in matches:
            value = int(value)
            if unit == 'd':
                seconds += value * 86400
            elif unit == 'h':
                seconds += value * 3600
            elif unit == 'm':
                seconds += value * 60
            elif unit == 's':
                seconds += value
        
        if seconds < 5:
            await interaction.followup.send("Reminder time must be at least 5 seconds.")
            return
            
        if seconds > 2592000:
            await interaction.followup.send("Reminder time cannot exceed 30 days.")
            return
        
        reminder_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        
        reminder_data = {
            "user_id": interaction.user.id,
            "channel_id": interaction.channel_id,
            "message": reminder,
            "time": reminder_time.timestamp(),
            "set_time": datetime.datetime.now().timestamp()
        }
        
        if interaction.user.id not in self.reminders:
            self.reminders[interaction.user.id] = []
            
        self.reminders[interaction.user.id].append(reminder_data)
        
        time_parts = []
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            time_parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            time_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            time_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0:
            time_parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
            
        time_str = ", ".join(time_parts)
        
        embed = discord.Embed(
            title="⏰ Reminder Set",
            description=f"I'll remind you about: **{reminder}**",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Time", value=time_str, inline=True)
        embed.add_field(name="Reminder At", value=f"<t:{int(reminder_time.timestamp())}:F>\n(<t:{int(reminder_time.timestamp())}:R>)", inline=True)
        embed.set_footer(text=f"Reminder for {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)
    
    @utility_group.command(name="reminders", description="List your active reminders")
    async def reminders(self, interaction: discord.Interaction):
        """List all your active reminders"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        if interaction.user.id not in self.reminders or not self.reminders[interaction.user.id]:
            await interaction.followup.send("You don't have any active reminders.")
            return
            
        embed = discord.Embed(
            title="Your Active Reminders",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        for i, reminder in enumerate(self.reminders[interaction.user.id], 1):
            embed.add_field(
                name=f"Reminder {i}",
                value=f"**Message:** {reminder['message']}\n**Time:** <t:{int(reminder['time'])}:R>\n**Set:** <t:{int(reminder['set_time'])}:R>",
                inline=False
            )
            
        embed.set_footer(text=f"You have {len(self.reminders[interaction.user.id])} active reminder(s)")
        
        view = ReminderListView(self, interaction.user.id)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @utility_group.command(name="weather", description="Get weather information for a location")
    @app_commands.describe(location="The city or location to get weather for")
    async def weather(self, interaction: discord.Interaction, location: str):
        """Get current weather information for a location"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        embed = discord.Embed(
            title=f"Weather for {location}",
            description="⚠️ This is simulated weather data for demonstration purposes.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        import random
        conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Thunderstorms", "Snowy", "Foggy", "Windy"]
        condition = random.choice(conditions)
        temp = random.randint(0, 35)
        humidity = random.randint(30, 90)
        wind_speed = random.randint(0, 30)
        
        condition_emojis = {
            "Sunny": "☀️",
            "Partly Cloudy": "⛅",
            "Cloudy": "☁️",
            "Rainy": "🌧️",
            "Thunderstorms": "⛈️",
            "Snowy": "❄️",
            "Foggy": "🌫️",
            "Windy": "💨"
        }
        
        embed.add_field(name="Condition", value=f"{condition_emojis.get(condition, '')} {condition}", inline=True)
        embed.add_field(name="Temperature", value=f"🌡️ {temp}°C ({round(temp * 9/5 + 32)}°F)", inline=True)
        embed.add_field(name="Humidity", value=f"💧 {humidity}%", inline=True)
        embed.add_field(name="Wind Speed", value=f"💨 {wind_speed} km/h", inline=True)
        
        embed.set_footer(text=f"Requested by {interaction.user.display_name} | Note: This is simulated data")
        
        await interaction.followup.send(embed=embed)
    
    @utility_group.command(name="embed", description="Create a custom embed message")
    @app_commands.describe(
        title="Embed title",
        description="Embed description",
        color="Embed color (hex code like #FF0000)",
        image_url="URL for the embed image (optional)",
        thumbnail_url="URL for the embed thumbnail (optional)"
    )
    @app_commands.default_permissions(manage_messages=True)
    async def embed(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        color: Optional[str] = None,
        image_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None
    ):
        """Create a custom embed message"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            embed_color = discord.Color.blue()
            if color:
                if color.startswith('#'):
                    color = color[1:]
                try:
                    embed_color = discord.Color.from_rgb(
                        int(color[0:2], 16),
                        int(color[2:4], 16),
                        int(color[4:6], 16)
                    )
                except:
                    pass
            
            embed = discord.Embed(
                title=title,
                description=description,
                color=embed_color,
                timestamp=datetime.datetime.now()
            )
            
            if image_url:
                embed.set_image(url=image_url)
                
            if thumbnail_url:
                embed.set_thumbnail(url=thumbnail_url)
                
            await interaction.channel.send(embed=embed)
            
            await interaction.followup.send("Embed message sent successfully!", ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"Error creating embed: {str(e)}", ephemeral=True)
    
    async def reminder_checker(self):
        """Background task to check and send reminders"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            current_time = datetime.datetime.now().timestamp()
            
            for user_id in list(self.reminders.keys()):
                due_reminders = [r for r in self.reminders[user_id] if r["time"] <= current_time]
                
                if due_reminders:
                    self.reminders[user_id] = [r for r in self.reminders[user_id] if r["time"] > current_time]
                    
                    if not self.reminders[user_id]:
                        del self.reminders[user_id]
                
                for reminder in due_reminders:
                    try:
                        user = self.bot.get_user(reminder["user_id"])
                        channel = self.bot.get_channel(reminder["channel_id"])
                        
                        if user and channel:
                            embed = discord.Embed(
                                title="⏰ Reminder",
                                description=reminder["message"],
                                color=discord.Color.blue(),
                                timestamp=datetime.datetime.now()
                            )
                            
                            embed.add_field(name="Set", value=f"<t:{int(reminder['set_time'])}:R>", inline=True)
                            embed.set_footer(text=f"Reminder for {user.display_name}")
                            
                            await channel.send(content=user.mention, embed=embed)
                    except Exception as e:
                        print(f"Error sending reminder: {e}")

            await asyncio.sleep(5)

class UserInfoView(discord.ui.View):
    def __init__(self, invoker, target):
        super().__init__(timeout=60)
        self.invoker = invoker
        self.target = target
        
        if isinstance(invoker, discord.Member) and isinstance(target, discord.Member):
            if invoker.guild_permissions.kick_members and invoker.top_role > target.top_role:
                self.add_item(discord.ui.Button(label="Kick", style=discord.ButtonStyle.danger, custom_id="kick_user"))
                
            if invoker.guild_permissions.ban_members and invoker.top_role > target.top_role:
                self.add_item(discord.ui.Button(label="Ban", style=discord.ButtonStyle.danger, custom_id="ban_user"))
                
            if invoker.guild_permissions.moderate_members and invoker.top_role > target.top_role:
                self.add_item(discord.ui.Button(label="Timeout", style=discord.ButtonStyle.secondary, custom_id="timeout_user"))
                
    async def interaction_check(self, interaction):
        return interaction.user.id == self.invoker.id

class AvatarView(discord.ui.View):
    def __init__(self, avatar_url):
        super().__init__(timeout=60)
        self.avatar_url = avatar_url
        
        self.add_item(discord.ui.Button(label="Open in Browser", style=discord.ButtonStyle.link, url=avatar_url))

class ReminderListView(discord.ui.View):
    def __init__(self, cog, user_id):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        
        self.add_item(discord.ui.Button(label="Cancel All Reminders", style=discord.ButtonStyle.danger, custom_id="cancel_all_reminders"))
        
    async def interaction_check(self, interaction):
        return interaction.user.id == self.user_id
        
    async def on_timeout(self):
        self.clear_items()


async def setup(bot):
    """Add the cog to the bot and register context menu commands"""
    await bot.add_cog(UtilityCommands(bot))
    print("Utility commands module loaded")