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
import sys
import os
from shared import *
from utils import *
import platform
import datetime
import psutil
import os

class SystemCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
        self.start_time = datetime.datetime.now()

    system_group = app_commands.Group(name="system", description="System management commands")

    @system_group.command(name="status", description="Get system status of the panel and bot")
    async def system_status(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            panel_data = function_getOverview()
            
            embed = discord.Embed(
                title="System Status",
                description="Status of the MCSManager panel and bot",
                color=discord.Color.blue()
            )
            
            if panel_data["status"] == 200:
                embed.add_field(
                    name="Panel",
                    value=f"Version: {panel_data['panel_version']}\nDaemons: {panel_data['remote_available']}/{panel_data['remote_total']}",
                    inline=True
                )
            else:
                embed.add_field(
                    name="Panel",
                    value="Unable to connect to panel",
                    inline=True
                )
            
            uptime = datetime.datetime.now() - self.start_time
            days, remainder = divmod(int(uptime.total_seconds()), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
            
            embed.add_field(
                name="Bot",
                value=f"Version: {os.getenv('BOT_VERSION', 'Unknown')}\nUptime: {uptime_str}",
                inline=True
            )
            
            try:
                cpu_usage = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                memory_usage = memory.percent
                
                embed.add_field(
                    name="Host System",
                    value=f"CPU: {cpu_usage}%\nMemory: {memory_usage}%\nPlatform: {platform.system()} {platform.release()}",
                    inline=False
                )
            except:
                embed.add_field(
                    name="Host System",
                    value=f"Platform: {platform.system()} {platform.release()}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")


    @commands.command(name="reload", description="Reload the bot's commands")
    @commands.is_owner()
    async def reload(self, ctx):
        """Reload all command modules (owner only)"""
        try:
            for extension in list(self.bot.extensions):
                await self.bot.reload_extension(extension)
            
            await ctx.send("All command modules reloaded successfully!")
        except Exception as e:
            await ctx.send(f"Error reloading modules: {str(e)}")

async def setup(bot):
    await bot.add_cog(SystemCommands(bot))