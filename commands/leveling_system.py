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
import json
import os
import random
import datetime
import asyncio
import math
from typing import Optional, List
from PIL import Image, ImageDraw, ImageFont
import io

class LevelingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
        self.levels_file = "levels.json"
        self.levels = {}
        self.xp_cooldown = {}
        self.xp_per_message = (15, 25)
        self.load_levels()
        
    def load_levels(self):
        if os.path.exists(self.levels_file):
            try:
                with open(self.levels_file, 'r') as f:
                    self.levels = json.load(f)
            except:
                self.levels = {}
                
    def save_levels(self):
        with open(self.levels_file, 'w') as f:
            json.dump(self.levels, f, indent=4)
            
    def get_level_xp(self, level):
        return 5 * (level ** 2) + 50 * level + 100
        
    def get_level_from_xp(self, xp):
        level = 0
        while self.get_level_xp(level) <= xp:
            level += 1
        return level - 1
        
    def format_xp(self, xp):
        if xp >= 1000000:
            return f"{xp/1000000:.1f}M"
        elif xp >= 1000:
            return f"{xp/1000:.1f}K"
        else:
            return str(xp)
            
    async def create_rank_card(self, user, guild_id):
        user_id = str(user.id)
        guild_id = str(guild_id)
        
        if guild_id not in self.levels:
            self.levels[guild_id] = {}
            
        if user_id not in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0, "last_message": 0}
            
        user_data = self.levels[guild_id][user_id]
        current_level = user_data["level"]
        current_xp = user_data["xp"]
        
        level_xp = self.get_level_xp(current_level)
        next_level_xp = self.get_level_xp(current_level + 1)
        
        xp_needed = next_level_xp - level_xp
        xp_have = current_xp - level_xp
        
        percentage = min(xp_have / xp_needed, 1.0)
        
        img = Image.new('RGBA', (800, 250), color=(44, 47, 51, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            font_big = ImageFont.truetype("arial.ttf", 36)
            font_medium = ImageFont.truetype("arial.ttf", 28)
            font_small = ImageFont.truetype("arial.ttf", 20)
        except:
            font_big = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
            
        try:
            avatar_asset = user.display_avatar.with_size(128)
            avatar_data = io.BytesIO(await avatar_asset.read())
            avatar = Image.open(avatar_data).convert('RGBA')
            avatar = avatar.resize((180, 180))
            
            mask = Image.new("L", avatar.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 180, 180), fill=255)
            
            img.paste(avatar, (30, 35), mask)
        except:
            draw.ellipse((30, 35, 210, 215), fill=(128, 128, 128, 255))
            
        draw.text((240, 40), user.display_name, fill=(255, 255, 255, 255), font=font_big)
        draw.text((240, 90), f"Level: {current_level}", fill=(255, 255, 255, 255), font=font_medium)
        
        xp_text = f"XP: {self.format_xp(xp_have)}/{self.format_xp(xp_needed)}"
        draw.text((240, 130), xp_text, fill=(255, 255, 255, 255), font=font_medium)
        
        rank = 1
        sorted_users = sorted(self.levels[guild_id].items(), key=lambda x: x[1]["xp"], reverse=True)
        for i, (id, _) in enumerate(sorted_users):
            if id == user_id:
                rank = i + 1
                break
                
        draw.text((240, 170), f"Rank: #{rank}", fill=(255, 255, 255, 255), font=font_medium)
        
        draw.rectangle((240, 210, 740, 230), fill=(80, 80, 80, 255))
        draw.rectangle((240, 210, 240 + 500 * percentage, 230), fill=(114, 137, 218, 255))
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return discord.File(buffer, filename="rank.png")
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
            
        if not message.guild:
            return
            
        user_id = str(message.author.id)
        guild_id = str(message.guild.id)
        
        current_time = datetime.datetime.now().timestamp()
        
        if guild_id not in self.levels:
            self.levels[guild_id] = {}
            
        if user_id not in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0, "last_message": 0}
            
        user_data = self.levels[guild_id][user_id]
        
        cooldown_key = f"{guild_id}-{user_id}"
        if cooldown_key in self.xp_cooldown:
            if current_time - self.xp_cooldown[cooldown_key] < 60:
                return
                
        self.xp_cooldown[cooldown_key] = current_time
        
        xp_gained = random.randint(self.xp_per_message[0], self.xp_per_message[1])
        user_data["xp"] += xp_gained
        user_data["last_message"] = current_time
        
        new_level = self.get_level_from_xp(user_data["xp"])
        
        if new_level > user_data["level"]:
            user_data["level"] = new_level
            
            level_up_channel = message.channel
            
            embed = discord.Embed(
                title="Level Up!",
                description=f"{message.author.mention} has reached level **{new_level}**!",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            
            embed.set_thumbnail(url=message.author.display_avatar.url)
            
            await level_up_channel.send(embed=embed)
            
        self.save_levels()
        
    leveling_group = app_commands.Group(name="level", description="Leveling system commands")
    
    @leveling_group.command(name="rank", description="Show your or another user's rank")
    @app_commands.describe(user="The user to check rank for (defaults to yourself)")
    async def rank(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        user = user or interaction.user
        guild_id = str(interaction.guild.id)
        
        if guild_id not in self.levels:
            self.levels[guild_id] = {}
            
        if str(user.id) not in self.levels[guild_id]:
            self.levels[guild_id][str(user.id)] = {"xp": 0, "level": 0, "last_message": 0}
            
        rank_card = await self.create_rank_card(user, guild_id)
        
        await interaction.followup.send(file=rank_card)
        
    @leveling_group.command(name="leaderboard", description="Show the server's XP leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        guild_id = str(interaction.guild.id)
        
        if guild_id not in self.levels:
            self.levels[guild_id] = {}
            
        if not self.levels[guild_id]:
            await interaction.followup.send("No one has earned XP yet!")
            return
            
        sorted_users = sorted(self.levels[guild_id].items(), key=lambda x: x[1]["xp"], reverse=True)
        
        embed = discord.Embed(
            title=f"{interaction.guild.name} Leaderboard",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        for i, (user_id, data) in enumerate(sorted_users[:10], 1):
            user = interaction.guild.get_member(int(user_id))
            username = user.display_name if user else f"Unknown User ({user_id})"
            
            current_level = data["level"]
            current_xp = data["xp"]
            
            embed.add_field(
                name=f"{i}. {username}",
                value=f"Level: {current_level} | XP: {self.format_xp(current_xp)}",
                inline=False
            )
            
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)
        
    @leveling_group.command(name="set_xp", description="Set a user's XP (Admin only)")
    @app_commands.describe(
        user="The user to modify",
        xp="The amount of XP to set"
    )
    @app_commands.default_permissions(administrator=True)
    async def set_xp(self, interaction: discord.Interaction, user: discord.Member, xp: int):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You don't have permission to use this command.")
            return
            
        guild_id = str(interaction.guild.id)
        user_id = str(user.id)
        
        if guild_id not in self.levels:
            self.levels[guild_id] = {}
            
        if user_id not in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0, "last_message": 0}
            
        self.levels[guild_id][user_id]["xp"] = max(0, xp)
        self.levels[guild_id][user_id]["level"] = self.get_level_from_xp(xp)
        
        self.save_levels()
        
        embed = discord.Embed(
            title="XP Updated",
            description=f"Set {user.mention}'s XP to **{xp}** (Level {self.levels[guild_id][user_id]['level']})",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        
        embed.set_footer(text=f"Modified by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)
        
    @leveling_group.command(name="add_xp", description="Add XP to a user (Admin only)")
    @app_commands.describe(
        user="The user to modify",
        xp="The amount of XP to add"
    )
    @app_commands.default_permissions(administrator=True)
    async def add_xp(self, interaction: discord.Interaction, user: discord.Member, xp: int):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You don't have permission to use this command.")
            return
            
        guild_id = str(interaction.guild.id)
        user_id = str(user.id)
        
        if guild_id not in self.levels:
            self.levels[guild_id] = {}
            
        if user_id not in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0, "last_message": 0}
            
        old_level = self.levels[guild_id][user_id]["level"]
        self.levels[guild_id][user_id]["xp"] += xp
        self.levels[guild_id][user_id]["level"] = self.get_level_from_xp(self.levels[guild_id][user_id]["xp"])
        
        new_level = self.levels[guild_id][user_id]["level"]
        level_change = ""
        
        if new_level > old_level:
            level_change = f" (Leveled up to {new_level}!)"
            
        self.save_levels()
        
        embed = discord.Embed(
            title="XP Added",
            description=f"Added **{xp}** XP to {user.mention}{level_change}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        
        embed.set_footer(text=f"Modified by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)
        
    @leveling_group.command(name="reset", description="Reset a user's XP and level (Admin only)")
    @app_commands.describe(user="The user to reset")
    @app_commands.default_permissions(administrator=True)
    async def reset(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You don't have permission to use this command.")
            return
            
        guild_id = str(interaction.guild.id)
        user_id = str(user.id)
        
        if guild_id not in self.levels:
            self.levels[guild_id] = {}
            
        if user_id in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0, "last_message": 0}
            self.save_levels()
            
        embed = discord.Embed(
            title="XP Reset",
            description=f"Reset {user.mention}'s XP and level to 0",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        
        embed.set_footer(text=f"Reset by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)
        
    @leveling_group.command(name="reset_all", description="Reset all users' XP and levels (Admin only)")
    @app_commands.default_permissions(administrator=True)
    async def reset_all(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You don't have permission to use this command.")
            return
            
        confirm_view = ConfirmView(interaction.user)
        
        embed = discord.Embed(
            title="⚠️ Confirm Reset All",
            description="Are you sure you want to reset **ALL** users' XP and levels? This cannot be undone!",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        
        message = await interaction.followup.send(embed=embed, view=confirm_view)
        
        await confirm_view.wait()
        
        if confirm_view.value:
            guild_id = str(interaction.guild.id)
            
            if guild_id in self.levels:
                self.levels[guild_id] = {}
                self.save_levels()
                
            result_embed = discord.Embed(
                title="XP System Reset",
                description="All users' XP and levels have been reset to 0",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            
            result_embed.set_footer(text=f"Reset by {interaction.user.display_name}")
            
            await message.edit(embed=result_embed, view=None)
        else:
            cancel_embed = discord.Embed(
                title="Reset Cancelled",
                description="The reset operation has been cancelled.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            
            await message.edit(embed=cancel_embed, view=None)

class ConfirmView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user
        self.value = None
        
    async def interaction_check(self, interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("This confirmation is not for you.", ephemeral=True)
            return False
        return True
        
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        await interaction.response.defer()
        self.stop()
        
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        await interaction.response.defer()
        self.stop()

async def setup(bot):
    await bot.add_cog(LevelingSystem(bot))