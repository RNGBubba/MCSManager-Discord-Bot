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
import json
import datetime
import asyncio
from typing import Optional, Dict, List, Any, Union
from shared import *
from utils import *
from instance import *


AUTO_RESTART_CONFIG_FILE = "auto_restart_config.json"

class AutoRestartScheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
        self.restart_configs = {}
        self.restart_tasks = {}
        
        self.load_configs()
        
        self.bot.loop.create_task(self.start_all_tasks())
    
    def cog_unload(self):
        """Cancel all tasks when the cog is unloaded"""
        for task_name, task in self.restart_tasks.items():
            if task is not None:
                task.cancel()
                print(f"Cancelled auto-restart task for {task_name}")
    
    def load_configs(self):
        """Load auto-restart configurations from file"""
        try:
            if os.path.exists(AUTO_RESTART_CONFIG_FILE):
                with open(AUTO_RESTART_CONFIG_FILE, 'r') as f:
                    self.restart_configs = json.load(f)
                print(f"Loaded auto-restart configurations for {len(self.restart_configs)} guilds")
            else:
                print("No auto-restart configuration file found, starting fresh")
        except Exception as e:
            print(f"Error loading auto-restart configurations: {e}")
            self.restart_configs = {}
    
    def save_configs(self):
        """Save auto-restart configurations to file"""
        try:
            with open(AUTO_RESTART_CONFIG_FILE, 'w') as f:
                json.dump(self.restart_configs, f, indent=4)
            print(f"Saved auto-restart configurations")
        except Exception as e:
            print(f"Error saving auto-restart configurations: {e}")
    
    async def start_all_tasks(self):
        """Start all configured auto-restart tasks"""
        await self.bot.wait_until_ready()
        
        for guild_id, guild_configs in self.restart_configs.items():
            for instance_name, config in guild_configs.items():
                if config.get("enabled", True):
                    await self.start_restart_task(guild_id, instance_name, config)
    
    async def start_restart_task(self, guild_id, instance_name, config):
        """Start an auto-restart task for a specific instance"""
        task_key = f"{guild_id}_{instance_name}"
        if task_key in self.restart_tasks and self.restart_tasks[task_key] is not None:
            self.restart_tasks[task_key].cancel()
        
        task = self.bot.loop.create_task(self.run_restart_schedule(guild_id, instance_name, config))
        self.restart_tasks[task_key] = task
        print(f"Started auto-restart task for {instance_name} in guild {guild_id}")
    
    async def run_restart_schedule(self, guild_id, instance_name, config):
        """Run the auto-restart schedule for an instance"""
        try:
            channel_id = config.get("channel_id")
            if not channel_id:
                print(f"No notification channel configured for {instance_name} in guild {guild_id}")
                return
                
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                print(f"Could not find channel {channel_id} for {instance_name} in guild {guild_id}")
                return
            
            interval_hours = config.get("interval_hours", 4)
            
            while True:
                now = datetime.datetime.now()
                
                hours_since_midnight = now.hour + now.minute / 60
                hours_until_next_interval = interval_hours - (hours_since_midnight % interval_hours)
                
                if hours_until_next_interval < 0.1:
                    hours_until_next_interval += interval_hours
                
                next_restart = now + datetime.timedelta(hours=hours_until_next_interval)
                next_restart = next_restart.replace(minute=0, second=0, microsecond=0)
                
                seconds_until_restart = (next_restart - now).total_seconds()
                
                if seconds_until_restart > 600:
                    await asyncio.sleep(seconds_until_restart - 600)
                
                try:
                    uuid, daemon_id = function_daemonNameIdTrans(instance_name)
                except Exception as e:
                    print(f"Error getting instance info for {instance_name}: {e}")
                    await asyncio.sleep(300)
                    continue
                
                try:
                    await channel.send(f"**⌛ Restarting in 10 Minutes ▶ Get your final stuff done.**")
                    await asyncio.sleep(300)
                    
                    await channel.send(f"**⌛ Restarting in 5 Minutes ▶ Hurry up and get your stuff done.**")
                    await asyncio.sleep(240)
                    
                    await channel.send(f"**⌛ Restarting in 1 Minute ▶ Get to a safe place!**")
                    await asyncio.sleep(30)
                    
                    await channel.send(f"**⌛ Restarting in 30 Seconds ▶ Get to a safe place!**")
                    await asyncio.sleep(20)
                    
                    await channel.send(f"**⌛ Restarting in 10 Seconds ▶ Not much time left!**")
                    await asyncio.sleep(5)
                    
                    await channel.send(f"**⌛ Restarting in 5 Seconds ▶ Don't forget your items on the ground!**")
                    await asyncio.sleep(1)
                    
                    await channel.send(f"**⌛ Restarting in 4 Seconds ▶ Make sure you are in a safe place!**")
                    await asyncio.sleep(1)
                    
                    await channel.send(f"**⌛ Restarting in 3 Seconds ▶ Restart takes about 3-4 Minutes.**")
                    await asyncio.sleep(1)
                    
                    await channel.send(f"**⌛ Restarting in 2 Seconds ▶ Check Discord for live server status!**")
                    await asyncio.sleep(1)
                    
                    await channel.send(f"**⌛ Restarting in 1 Second ▶ Booting Players...**")
                    
                    await channel.send(f"**⌚ Server is now restarting... ⌚**")
                    
                    function_stopInstance(uuid, daemon_id)
                    await asyncio.sleep(15)
                    
                    function_killInstance(uuid, daemon_id)
                    await asyncio.sleep(15)
                    
                    function_startInstance(uuid, daemon_id)
                    
                    
                    await asyncio.sleep(60)
                    
                except Exception as e:
                    print(f"Error during restart sequence for {instance_name}: {e}")
                    await asyncio.sleep(60)
        
        except asyncio.CancelledError:
            print(f"Auto-restart task for {instance_name} in guild {guild_id} was cancelled")
        except Exception as e:
            print(f"Error in auto-restart task for {instance_name} in guild {guild_id}: {e}")
            await asyncio.sleep(300)
            await self.start_restart_task(guild_id, instance_name, config)
    
    restart_group = app_commands.Group(name="autorestart", description="Auto-restart scheduling commands")
    
    @restart_group.command(name="setup", description="Set up automatic server restarts")
    @app_commands.describe(
        instance_name="Name of the instance to restart",
        channel="Channel to send restart notifications",
        interval_hours="Restart interval in hours (default: 4)"
    )
    async def setup_auto_restart(
        self,
        interaction: discord.Interaction,
        instance_name: str,
        channel: discord.TextChannel,
        interval_hours: int = 4
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            try:
                uuid, daemon_id = function_daemonNameIdTrans(instance_name)
            except:
                await interaction.followup.send(f"Error: Instance '{instance_name}' not found.")
                return
            
            if interval_hours < 1 or interval_hours > 24:
                await interaction.followup.send("Error: Interval must be between 1 and 24 hours.")
                return
            
            guild_id = str(interaction.guild.id)
            if guild_id not in self.restart_configs:
                self.restart_configs[guild_id] = {}
            
            config = {
                "channel_id": str(channel.id),
                "interval_hours": interval_hours,
                "enabled": True,
                "created_by": str(interaction.user.id),
                "created_at": datetime.datetime.now().isoformat()
            }
            
            self.restart_configs[guild_id][instance_name] = config
            self.save_configs()
            
            await self.start_restart_task(guild_id, instance_name, config)
            
            now = datetime.datetime.now()
            hours_since_midnight = now.hour + now.minute / 60
            hours_until_next_interval = interval_hours - (hours_since_midnight % interval_hours)
            
            if hours_until_next_interval < 0.1:
                hours_until_next_interval += interval_hours
            
            next_restart = now + datetime.timedelta(hours=hours_until_next_interval)
            next_restart = next_restart.replace(minute=0, second=0, microsecond=0)
            
            embed = discord.Embed(
                title="Auto-Restart Configured",
                description=f"Automatic restarts set up for `{instance_name}`",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Notification Channel", value=channel.mention)
            embed.add_field(name="Interval", value=f"{interval_hours} hours")
            embed.add_field(name="Next Restart", value=f"<t:{int(next_restart.timestamp())}:F> (<t:{int(next_restart.timestamp())}:R>)")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @restart_group.command(name="disable", description="Disable automatic restarts for an instance")
    @app_commands.describe(instance_name="Name of the instance")
    async def disable_auto_restart(self, interaction: discord.Interaction, instance_name: str):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            guild_id = str(interaction.guild.id)
            
            if guild_id not in self.restart_configs or instance_name not in self.restart_configs[guild_id]:
                await interaction.followup.send(f"No auto-restart configuration found for `{instance_name}`.")
                return
            
            self.restart_configs[guild_id][instance_name]["enabled"] = False
            self.save_configs()
            
            task_key = f"{guild_id}_{instance_name}"
            if task_key in self.restart_tasks and self.restart_tasks[task_key] is not None:
                self.restart_tasks[task_key].cancel()
                self.restart_tasks[task_key] = None
            
            embed = discord.Embed(
                title="Auto-Restart Disabled",
                description=f"Automatic restarts disabled for `{instance_name}`",
                color=discord.Color.red()
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @restart_group.command(name="enable", description="Enable automatic restarts for an instance")
    @app_commands.describe(instance_name="Name of the instance")
    async def enable_auto_restart(self, interaction: discord.Interaction, instance_name: str):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            guild_id = str(interaction.guild.id)
            
            if guild_id not in self.restart_configs or instance_name not in self.restart_configs[guild_id]:
                await interaction.followup.send(f"No auto-restart configuration found for `{instance_name}`.")
                return
            
            self.restart_configs[guild_id][instance_name]["enabled"] = True
            self.save_configs()
            
            await self.start_restart_task(guild_id, instance_name, self.restart_configs[guild_id][instance_name])
            
            now = datetime.datetime.now()
            interval_hours = self.restart_configs[guild_id][instance_name]["interval_hours"]
            hours_since_midnight = now.hour + now.minute / 60
            hours_until_next_interval = interval_hours - (hours_since_midnight % interval_hours)
            
            if hours_until_next_interval < 0.1:
                hours_until_next_interval += interval_hours
            
            next_restart = now + datetime.timedelta(hours=hours_until_next_interval)
            next_restart = next_restart.replace(minute=0, second=0, microsecond=0)
            
            embed = discord.Embed(
                title="Auto-Restart Enabled",
                description=f"Automatic restarts enabled for `{instance_name}`",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Next Restart", value=f"<t:{int(next_restart.timestamp())}:F> (<t:{int(next_restart.timestamp())}:R>)")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @restart_group.command(name="list", description="List all configured auto-restarts")
    async def list_auto_restarts(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            guild_id = str(interaction.guild.id)
            
            if guild_id not in self.restart_configs or not self.restart_configs[guild_id]:
                await interaction.followup.send("No auto-restart configurations found for this server.")
                return
            
            embed = discord.Embed(
                title="Auto-Restart Configurations",
                description=f"Total configurations: {len(self.restart_configs[guild_id])}",
                color=discord.Color.blue()
            )
            
            for instance_name, config in self.restart_configs[guild_id].items():
                channel_id = config.get("channel_id")
                channel = self.bot.get_channel(int(channel_id)) if channel_id else None
                channel_text = channel.mention if channel else f"Channel ID: {channel_id}"
                
                now = datetime.datetime.now()
                interval_hours = config.get("interval_hours", 4)
                hours_since_midnight = now.hour + now.minute / 60
                hours_until_next_interval = interval_hours - (hours_since_midnight % interval_hours)
                
                if hours_until_next_interval < 0.1:
                    hours_until_next_interval += interval_hours
                
                next_restart = now + datetime.timedelta(hours=hours_until_next_interval)
                next_restart = next_restart.replace(minute=0, second=0, microsecond=0)
                
                status = "✅ Enabled" if config.get("enabled", True) else "❌ Disabled"
                
                embed.add_field(
                    name=f"{instance_name} ({status})",
                    value=f"Channel: {channel_text}\n" +
                          f"Interval: {interval_hours} hours\n" +
                          f"Next Restart: <t:{int(next_restart.timestamp())}:R>",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @restart_group.command(name="update", description="Update auto-restart configuration")
    @app_commands.describe(
        instance_name="Name of the instance",
        channel="New notification channel",
        interval_hours="New restart interval in hours"
    )
    async def update_auto_restart(
        self,
        interaction: discord.Interaction,
        instance_name: str,
        channel: Optional[discord.TextChannel] = None,
        interval_hours: Optional[int] = None
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            guild_id = str(interaction.guild.id)
            
            if guild_id not in self.restart_configs or instance_name not in self.restart_configs[guild_id]:
                await interaction.followup.send(f"No auto-restart configuration found for `{instance_name}`.")
                return
            
            config = self.restart_configs[guild_id][instance_name]
            
            if channel:
                config["channel_id"] = str(channel.id)
            
            if interval_hours is not None:
                if interval_hours < 1 or interval_hours > 24:
                    await interaction.followup.send("Error: Interval must be between 1 and 24 hours.")
                    return
                config["interval_hours"] = interval_hours
            
            self.restart_configs[guild_id][instance_name] = config
            self.save_configs()
            
            if config.get("enabled", True):
                await self.start_restart_task(guild_id, instance_name, config)
            
            now = datetime.datetime.now()
            interval_hours = config["interval_hours"]
            hours_since_midnight = now.hour + now.minute / 60
            hours_until_next_interval = interval_hours - (hours_since_midnight % interval_hours)
            
            if hours_until_next_interval < 0.1:
                hours_until_next_interval += interval_hours
            
            next_restart = now + datetime.timedelta(hours=hours_until_next_interval)
            next_restart = next_restart.replace(minute=0, second=0, microsecond=0)
            
            channel_id = config["channel_id"]
            channel_obj = self.bot.get_channel(int(channel_id))
            channel_text = channel_obj.mention if channel_obj else f"Channel ID: {channel_id}"
            
            embed = discord.Embed(
                title="Auto-Restart Updated",
                description=f"Configuration updated for `{instance_name}`",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Notification Channel", value=channel_text)
            embed.add_field(name="Interval", value=f"{interval_hours} hours")
            embed.add_field(name="Next Restart", value=f"<t:{int(next_restart.timestamp())}:F> (<t:{int(next_restart.timestamp())}:R>)")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @restart_group.command(name="delete", description="Delete auto-restart configuration")
    @app_commands.describe(instance_name="Name of the instance")
    async def delete_auto_restart(self, interaction: discord.Interaction, instance_name: str):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            guild_id = str(interaction.guild.id)
            
            if guild_id not in self.restart_configs or instance_name not in self.restart_configs[guild_id]:
                await interaction.followup.send(f"No auto-restart configuration found for `{instance_name}`.")
                return
            
            task_key = f"{guild_id}_{instance_name}"
            if task_key in self.restart_tasks and self.restart_tasks[task_key] is not None:
                self.restart_tasks[task_key].cancel()
                self.restart_tasks[task_key] = None
            
            del self.restart_configs[guild_id][instance_name]
            
            if not self.restart_configs[guild_id]:
                del self.restart_configs[guild_id]
            
            self.save_configs()
            
            embed = discord.Embed(
                title="Auto-Restart Deleted",
                description=f"Configuration deleted for `{instance_name}`",
                color=discord.Color.red()
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @restart_group.command(name="now", description="Trigger an immediate restart")
    @app_commands.describe(
        instance_name="Name of the instance to restart",
        countdown="Enable countdown messages (default: True)"
    )
    async def restart_now(
        self,
        interaction: discord.Interaction,
        instance_name: str,
        countdown: bool = True
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            try:
                uuid, daemon_id = function_daemonNameIdTrans(instance_name)
            except:
                await interaction.followup.send(f"Error: Instance '{instance_name}' not found.")
                return
            
            channel = interaction.channel
            guild_id = str(interaction.guild.id)
            
            if guild_id in self.restart_configs and instance_name in self.restart_configs[guild_id]:
                channel_id = self.restart_configs[guild_id][instance_name].get("channel_id")
                if channel_id:
                    config_channel = self.bot.get_channel(int(channel_id))
                    if config_channel:
                        channel = config_channel
            
            embed = discord.Embed(
                title="Manual Restart Triggered",
                description=f"Restarting `{instance_name}`" + (" with countdown" if countdown else " immediately"),
                color=discord.Color.gold()
            )
            
            await interaction.followup.send(embed=embed)
            
            if countdown:
                await channel.send(f"**⌛ Restarting in 10 Seconds ▶ Not much time left!**")
                await asyncio.sleep(5)
                
                await channel.send(f"**⌛ Restarting in 5 Seconds ▶ Don't forget your items on the ground!**")
                await asyncio.sleep(1)
                
                await channel.send(f"**⌛ Restarting in 4 Seconds ▶ Make sure you are in a safe place!**")
                await asyncio.sleep(1)
                
                await channel.send(f"**⌛ Restarting in 3 Seconds ▶ Restart takes about 3-4 Minutes.**")
                await asyncio.sleep(1)
                
                await channel.send(f"**⌛ Restarting in 2 Seconds ▶ Check Discord for live server status!**")
                await asyncio.sleep(1)
                
                await channel.send(f"**⌛ Restarting in 1 Second ▶ Booting Players...**")
            
            await channel.send(f"**⌚ Server is now restarting... ⌚**")
            
            function_stopInstance(uuid, daemon_id)
            await asyncio.sleep(15)
            
            function_killInstance(uuid, daemon_id)
            await asyncio.sleep(15)
            
            function_startInstance(uuid, daemon_id)
            
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(AutoRestartScheduler(bot))