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
from discord.ext import commands, tasks
import json
import os
import asyncio
import datetime
import random
import re
from typing import Optional, List

class GiveawaySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
        self.giveaways_file = "giveaways.json"
        self.giveaways = {}
        self.load_giveaways()
        self.check_giveaways.start()
        
    def cog_unload(self):
        self.check_giveaways.cancel()
        
    def load_giveaways(self):
        if os.path.exists(self.giveaways_file):
            try:
                with open(self.giveaways_file, 'r') as f:
                    self.giveaways = json.load(f)
            except:
                self.giveaways = {}
                
    def save_giveaways(self):
        with open(self.giveaways_file, 'w') as f:
            json.dump(self.giveaways, f, indent=4)
            
    def parse_time(self, time_str):
        total_seconds = 0
        pattern = re.compile(r'(\d+)([dhms])')
        matches = pattern.findall(time_str.lower())
        
        if not matches:
            return None
            
        for value, unit in matches:
            value = int(value)
            if unit == 'd':
                total_seconds += value * 86400
            elif unit == 'h':
                total_seconds += value * 3600
            elif unit == 'm':
                total_seconds += value * 60
            elif unit == 's':
                total_seconds += value
                
        return total_seconds
        
    def format_time(self, seconds):
        if seconds < 60:
            return f"{seconds} seconds"
            
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        
        time_parts = []
        
        if days > 0:
            time_parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            time_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            time_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0:
            time_parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
            
        return ", ".join(time_parts)
        
    async def create_giveaway_embed(self, giveaway_data, ended=False):
        guild = self.bot.get_guild(int(giveaway_data["guild_id"]))
        
        if not guild:
            return None
            
        host = guild.get_member(int(giveaway_data["host_id"]))
        host_name = host.display_name if host else "Unknown User"
        
        time_remaining = int(giveaway_data["end_time"]) - int(datetime.datetime.now().timestamp())
        
        if ended:
            title = "🎉 Giveaway Ended!"
            color = discord.Color.red()
            footer = f"Ended at"
        else:
            title = "🎉 Giveaway!"
            color = discord.Color.green()
            footer = f"Ends at"
            
        embed = discord.Embed(
            title=title,
            description=f"**{giveaway_data['prize']}**",
            color=color,
            timestamp=datetime.datetime.fromtimestamp(int(giveaway_data["end_time"]))
        )
        
        embed.add_field(name="Hosted by", value=f"{host.mention if host else host_name}", inline=True)
        
        if giveaway_data.get("winners", 1) > 1:
            embed.add_field(name="Winners", value=str(giveaway_data["winners"]), inline=True)
            
        entries = len(giveaway_data.get("entries", []))
        embed.add_field(name="Entries", value=str(entries), inline=True)
        
        if not ended and time_remaining > 0:
            embed.add_field(name="Time Remaining", value=f"<t:{int(giveaway_data['end_time'])}:R>", inline=True)
        elif ended:
            if entries > 0:
                winner_ids = giveaway_data.get("winner_ids", [])
                if winner_ids:
                    winner_mentions = []
                    for winner_id in winner_ids:
                        winner = guild.get_member(int(winner_id))
                        if winner:
                            winner_mentions.append(winner.mention)
                        else:
                            winner_mentions.append(f"<@{winner_id}>")
                            
                    embed.add_field(name="Winner(s)", value="\n".join(winner_mentions), inline=False)
                else:
                    embed.add_field(name="Winner(s)", value="Could not determine a winner", inline=False)
            else:
                embed.add_field(name="Winner(s)", value="No one entered the giveaway", inline=False)
                
        embed.set_footer(text=f"{footer} • Giveaway ID: {giveaway_data['id']}")
        
        return embed
        
    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        current_time = datetime.datetime.now().timestamp()
        ended_giveaways = []
        
        for giveaway_id, giveaway in self.giveaways.items():
            if not giveaway.get("ended", False) and int(giveaway["end_time"]) <= current_time:
                ended_giveaways.append(giveaway_id)
                
        for giveaway_id in ended_giveaways:
            await self.end_giveaway(giveaway_id)
            
    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()
        
    async def end_giveaway(self, giveaway_id):
        if giveaway_id not in self.giveaways:
            return
            
        giveaway = self.giveaways[giveaway_id]
        
        if giveaway.get("ended", False):
            return
            
        giveaway["ended"] = True
        
        guild = self.bot.get_guild(int(giveaway["guild_id"]))
        
        if not guild:
            self.save_giveaways()
            return
            
        channel = guild.get_channel(int(giveaway["channel_id"]))
        
        if not channel:
            self.save_giveaways()
            return
            
        try:
            message = await channel.fetch_message(int(giveaway["message_id"]))
        except:
            self.save_giveaways()
            return
            
        entries = giveaway.get("entries", [])
        winners_count = min(giveaway.get("winners", 1), len(entries))
        
        if entries and winners_count > 0:
            winner_ids = random.sample(entries, winners_count)
            giveaway["winner_ids"] = winner_ids
            
            winner_mentions = []
            for winner_id in winner_ids:
                winner = guild.get_member(int(winner_id))
                if winner:
                    winner_mentions.append(winner.mention)
                else:
                    winner_mentions.append(f"<@{winner_id}>")
                    
            winners_text = " ".join(winner_mentions)
            
            announcement = f"🎉 Congratulations {winners_text}! You won **{giveaway['prize']}**!"
        else:
            announcement = f"No one entered the giveaway for **{giveaway['prize']}**."
            
        embed = await self.create_giveaway_embed(giveaway, ended=True)
        
        if embed:
            try:
                await message.edit(embed=embed, view=None)
                await channel.send(announcement)
            except:
                pass
                
        self.save_giveaways()
        
    giveaway_group = app_commands.Group(name="giveaway", description="Giveaway system commands")
    
    @giveaway_group.command(name="start", description="Start a new giveaway")
    @app_commands.describe(
        prize="The prize for the giveaway",
        time="Duration of the giveaway (e.g., 1d, 12h, 30m)",
        winners="Number of winners (default: 1)",
        channel="Channel to host the giveaway in (default: current channel)"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def start(
        self,
        interaction: discord.Interaction,
        prize: str,
        time: str,
        winners: int = 1,
        channel: Optional[discord.TextChannel] = None
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.followup.send("You need the Manage Server permission to start giveaways.")
            return
            
        duration = self.parse_time(time)
        
        if not duration:
            await interaction.followup.send("Invalid time format. Use a combination of d (days), h (hours), m (minutes), s (seconds). Example: 1d12h")
            return
            
        if duration < 10:
            await interaction.followup.send("Giveaway duration must be at least 10 seconds.")
            return
            
        if duration > 2592000:
            await interaction.followup.send("Giveaway duration cannot exceed 30 days.")
            return
            
        if winners < 1:
            await interaction.followup.send("Number of winners must be at least 1.")
            return
            
        if winners > 20:
            await interaction.followup.send("Number of winners cannot exceed 20.")
            return
            
        target_channel = channel or interaction.channel
        
        if not target_channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.followup.send(f"I don't have permission to send messages in {target_channel.mention}.")
            return
            
        if not target_channel.permissions_for(interaction.guild.me).embed_links:
            await interaction.followup.send(f"I don't have permission to embed links in {target_channel.mention}.")
            return
            
        end_time = int((datetime.datetime.now() + datetime.timedelta(seconds=duration)).timestamp())
        
        giveaway_id = str(int(datetime.datetime.now().timestamp()))
        
        giveaway_data = {
            "id": giveaway_id,
            "prize": prize,
            "winners": winners,
            "end_time": end_time,
            "channel_id": str(target_channel.id),
            "guild_id": str(interaction.guild.id),
            "host_id": str(interaction.user.id),
            "entries": [],
            "ended": False
        }
        
        embed = await self.create_giveaway_embed(giveaway_data)
        
        view = GiveawayView(self, giveaway_id)
        
        giveaway_message = await target_channel.send(embed=embed, view=view)
        
        giveaway_data["message_id"] = str(giveaway_message.id)
        self.giveaways[giveaway_id] = giveaway_data
        self.save_giveaways()
        
        formatted_duration = self.format_time(duration)
        
        await interaction.followup.send(f"Giveaway for **{prize}** started in {target_channel.mention}! It will end in {formatted_duration}.")
        
    @giveaway_group.command(name="end", description="End a giveaway early")
    @app_commands.describe(giveaway_id="The ID of the giveaway to end")
    @app_commands.default_permissions(manage_guild=True)
    async def end(self, interaction: discord.Interaction, giveaway_id: str):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.followup.send("You need the Manage Server permission to end giveaways.")
            return
            
        if giveaway_id not in self.giveaways:
            await interaction.followup.send("Giveaway not found. Please check the ID and try again.")
            return
            
        giveaway = self.giveaways[giveaway_id]
        
        if giveaway.get("ended", False):
            await interaction.followup.send("This giveaway has already ended.")
            return
            
        if str(giveaway["guild_id"]) != str(interaction.guild.id):
            await interaction.followup.send("This giveaway is not from this server.")
            return
            
        await self.end_giveaway(giveaway_id)
        
        await interaction.followup.send("Giveaway ended successfully!")
        
    @giveaway_group.command(name="reroll", description="Reroll the winners of a giveaway")
    @app_commands.describe(
        giveaway_id="The ID of the giveaway to reroll",
        winners="Number of winners to reroll (default: all)"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def reroll(self, interaction: discord.Interaction, giveaway_id: str, winners: Optional[int] = None):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.followup.send("You need the Manage Server permission to reroll giveaways.")
            return
            
        if giveaway_id not in self.giveaways:
            await interaction.followup.send("Giveaway not found. Please check the ID and try again.")
            return
            
        giveaway = self.giveaways[giveaway_id]
        
        if not giveaway.get("ended", False):
            await interaction.followup.send("This giveaway hasn't ended yet.")
            return
            
        if str(giveaway["guild_id"]) != str(interaction.guild.id):
            await interaction.followup.send("This giveaway is not from this server.")
            return
            
        entries = giveaway.get("entries", [])
        
        if not entries:
            await interaction.followup.send("No one entered this giveaway, so I can't reroll it.")
            return
            
        previous_winners = giveaway.get("winner_ids", [])
        
        if not previous_winners:
            await interaction.followup.send("This giveaway doesn't have any winners to reroll.")
            return
            
        reroll_count = winners if winners else len(previous_winners)
        reroll_count = min(reroll_count, len(previous_winners), len(entries))
        
        new_winners = []
        available_entries = [entry for entry in entries if entry not in previous_winners]
        
        if len(available_entries) < reroll_count:
            available_entries = entries
            
        if available_entries:
            new_winners = random.sample(available_entries, reroll_count)
            
        if not new_winners:
            await interaction.followup.send("Couldn't find new winners to reroll.")
            return
            
        guild = self.bot.get_guild(int(giveaway["guild_id"]))
        
        if not guild:
            await interaction.followup.send("I couldn't find the server for this giveaway.")
            return
            
        channel = guild.get_channel(int(giveaway["channel_id"]))
        
        if not channel:
            await interaction.followup.send("I couldn't find the channel for this giveaway.")
            return
            
        winner_mentions = []
        for winner_id in new_winners:
            winner = guild.get_member(int(winner_id))
            if winner:
                winner_mentions.append(winner.mention)
            else:
                winner_mentions.append(f"<@{winner_id}>")
                
        winners_text = " ".join(winner_mentions)
        
        for i, new_winner in enumerate(new_winners):
            if i < len(previous_winners):
                previous_winners[i] = new_winner
            else:
                previous_winners.append(new_winner)
                
        giveaway["winner_ids"] = previous_winners[:reroll_count]
        self.save_giveaways()
        
        announcement = f"🎉 Rerolled! Congratulations {winners_text}! You won **{giveaway['prize']}**!"
        
        try:
            await channel.send(announcement)
            await interaction.followup.send(f"Successfully rerolled {reroll_count} winner(s)!")
        except:
            await interaction.followup.send("I couldn't send the reroll announcement to the channel.")
            
    @giveaway_group.command(name="list", description="List all active giveaways")
    async def list(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        guild_id = str(interaction.guild.id)
        
        active_giveaways = [g for g in self.giveaways.values() if 
                           str(g["guild_id"]) == guild_id and not g.get("ended", False)]
        
        if not active_giveaways:
            await interaction.followup.send("There are no active giveaways in this server.")
            return
            
        embed = discord.Embed(
            title="Active Giveaways",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        for giveaway in active_giveaways:
            channel = interaction.guild.get_channel(int(giveaway["channel_id"]))
            channel_name = channel.mention if channel else "Unknown Channel"
            
            time_remaining = int(giveaway["end_time"]) - int(datetime.datetime.now().timestamp())
            
            if time_remaining > 0:
                embed.add_field(
                    name=f"{giveaway['prize']}",
                    value=f"ID: `{giveaway['id']}`\nChannel: {channel_name}\nEnds: <t:{int(giveaway['end_time'])}:R>\nEntries: {len(giveaway.get('entries', []))}\nWinners: {giveaway.get('winners', 1)}",
                    inline=False
                )
                
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)
        
    @giveaway_group.command(name="info", description="Get information about a giveaway")
    @app_commands.describe(giveaway_id="The ID of the giveaway")
    async def info(self, interaction: discord.Interaction, giveaway_id: str):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        if giveaway_id not in self.giveaways:
            await interaction.followup.send("Giveaway not found. Please check the ID and try again.")
            return
            
        giveaway = self.giveaways[giveaway_id]
        
        if str(giveaway["guild_id"]) != str(interaction.guild.id):
            await interaction.followup.send("This giveaway is not from this server.")
            return
            
        guild = self.bot.get_guild(int(giveaway["guild_id"]))
        
        if not guild:
            await interaction.followup.send("I couldn't find the server for this giveaway.")
            return
            
        channel = guild.get_channel(int(giveaway["channel_id"]))
        channel_name = channel.mention if channel else "Unknown Channel"
        
        host = guild.get_member(int(giveaway["host_id"]))
        host_name = host.mention if host else "Unknown User"
        
        embed = discord.Embed(
            title=f"Giveaway Info: {giveaway['prize']}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="ID", value=giveaway_id, inline=True)
        embed.add_field(name="Channel", value=channel_name, inline=True)
        embed.add_field(name="Host", value=host_name, inline=True)
        
        embed.add_field(name="Winners", value=str(giveaway.get("winners", 1)), inline=True)
        embed.add_field(name="Entries", value=str(len(giveaway.get("entries", []))), inline=True)
        
        if giveaway.get("ended", False):
            embed.add_field(name="Status", value="Ended", inline=True)
            embed.add_field(name="Ended At", value=f"<t:{int(giveaway['end_time'])}:F>", inline=True)
            
            winner_ids = giveaway.get("winner_ids", [])
            if winner_ids:
                winner_mentions = []
                for winner_id in winner_ids:
                    winner = guild.get_member(int(winner_id))
                    if winner:
                        winner_mentions.append(winner.mention)
                    else:
                        winner_mentions.append(f"<@{winner_id}>")
                        
                embed.add_field(name="Winner(s)", value="\n".join(winner_mentions), inline=False)
            else:
                embed.add_field(name="Winner(s)", value="No winners determined", inline=False)
        else:
            embed.add_field(name="Status", value="Active", inline=True)
            embed.add_field(name="Ends At", value=f"<t:{int(giveaway['end_time'])}:F>\n(<t:{int(giveaway['end_time'])}:R>)", inline=True)
            
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)

class GiveawayView(discord.ui.View):
    def __init__(self, cog, giveaway_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.giveaway_id = giveaway_id
        
    @discord.ui.button(label="Enter Giveaway", style=discord.ButtonStyle.primary, emoji="🎉", custom_id="enter_giveaway")
    async def enter_giveaway(self, interaction: discord.Interaction, button: discord.ui.Button):
        giveaway = self.cog.giveaways.get(self.giveaway_id)
        
        if not giveaway:
            await interaction.response.send_message("This giveaway no longer exists.", ephemeral=True)
            return
            
        if giveaway.get("ended", False):
            await interaction.response.send_message("This giveaway has already ended.", ephemeral=True)
            return
            
        user_id = str(interaction.user.id)
        
        if user_id in giveaway.get("entries", []):
            giveaway["entries"].remove(user_id)
            self.cog.save_giveaways()
            
            embed = await self.cog.create_giveaway_embed(giveaway)
            
            try:
                message = await interaction.channel.fetch_message(int(giveaway["message_id"]))
                await message.edit(embed=embed)
            except:
                pass
                
            await interaction.response.send_message("You have left the giveaway.", ephemeral=True)
        else:
            if "entries" not in giveaway:
                giveaway["entries"] = []
                
            giveaway["entries"].append(user_id)
            self.cog.save_giveaways()
            
            embed = await self.cog.create_giveaway_embed(giveaway)
            
            try:
                message = await interaction.channel.fetch_message(int(giveaway["message_id"]))
                await message.edit(embed=embed)
            except:
                pass
                
            await interaction.response.send_message("You have entered the giveaway!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(GiveawaySystem(bot))