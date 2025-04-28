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
from discord.ui import Button, View, Select

INVITE_DATA_FILE = "invite_data.json"

class InviteLeaderboardView(View):
    def __init__(self, cog, guild_id: int, page: int = 1, entries_per_page: int = 10):
        super().__init__(timeout=180)
        self.cog = cog
        self.guild_id = guild_id
        self.page = page
        self.entries_per_page = entries_per_page
        self.max_pages = 1
        
        self.add_item(Button(label="◀️ Previous", custom_id="prev_page", style=discord.ButtonStyle.gray, disabled=(page <= 1)))
        self.add_item(Button(label="▶️ Next", custom_id="next_page", style=discord.ButtonStyle.gray, disabled=(page >= self.max_pages)))
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data["custom_id"] == "prev_page" and self.page > 1:
            self.page -= 1
            await self.cog.show_leaderboard(interaction, self.guild_id, self.page, self.entries_per_page, interaction.message)
            return False
        elif interaction.data["custom_id"] == "next_page" and self.page < self.max_pages:
            self.page += 1
            await self.cog.show_leaderboard(interaction, self.guild_id, self.page, self.entries_per_page, interaction.message)
            return False
        return True

class InviteDetailsView(View):
    def __init__(self, inviter_id: int):
        super().__init__(timeout=180)
        self.add_item(Button(label="View Profile", url=f"discord://-/users/{inviter_id}", style=discord.ButtonStyle.link))

class InviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites: Dict[int, Dict[str, Any]] = {}
        self.invite_data: Dict[int, Dict[str, Any]] = {}
        
        self.load_invite_data()
        
        self.bot.loop.create_task(self.populate_invite_cache())
        
    def load_invite_data(self):
        """Load invite data from file"""
        try:
            if os.path.exists(INVITE_DATA_FILE):
                with open(INVITE_DATA_FILE, 'r') as f:
                    data = json.load(f)
                    self.invite_data = {
                        int(guild_id): {
                            int(user_id): user_data 
                            for user_id, user_data in guild_data.items()
                        } 
                        for guild_id, guild_data in data.items()
                    }
                print(f"Loaded invite data for {len(self.invite_data)} guilds")
            else:
                print("No invite data file found, starting fresh")
        except Exception as e:
            print(f"Error loading invite data: {e}")
            self.invite_data = {}
    
    def save_invite_data(self):
        """Save invite data to file"""
        try:
            with open(INVITE_DATA_FILE, 'w') as f:
                json.dump(self.invite_data, f, indent=4)
            print(f"Saved invite data for {len(self.invite_data)} guilds")
        except Exception as e:
            print(f"Error saving invite data: {e}")
    
    async def populate_invite_cache(self):
        """Populate the invite cache for all guilds"""
        await self.bot.wait_until_ready()
        
        for guild in self.bot.guilds:
            try:
                if not guild.me.guild_permissions.manage_guild:
                    print(f"Missing manage_guild permission in {guild.name}, can't track invites")
                    continue
                
                if guild.id not in self.invite_data:
                    self.invite_data[guild.id] = {}
                
                guild_invites = await guild.invites()
                
                self.invites[guild.id] = {
                    invite.code: {
                        'uses': invite.uses,
                        'inviter_id': invite.inviter.id if invite.inviter else None,
                        'created_at': invite.created_at.isoformat(),
                        'max_uses': invite.max_uses,
                        'max_age': invite.max_age,
                        'temporary': invite.temporary,
                        'channel_id': invite.channel.id
                    } for invite in guild_invites
                }
                
                print(f"Cached {len(guild_invites)} invites for {guild.name}")
            except Exception as e:
                print(f"Error caching invites for {guild.name}: {e}")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Initialize invite tracking when the bot joins a new guild"""
        if not guild.me.guild_permissions.manage_guild:
            print(f"Missing manage_guild permission in {guild.name}, can't track invites")
            return
            
        try:
            self.invite_data[guild.id] = {}
            
            guild_invites = await guild.invites()
            self.invites[guild.id] = {
                invite.code: {
                    'uses': invite.uses,
                    'inviter_id': invite.inviter.id if invite.inviter else None,
                    'created_at': invite.created_at.isoformat(),
                    'max_uses': invite.max_uses,
                    'max_age': invite.max_age,
                    'temporary': invite.temporary,
                    'channel_id': invite.channel.id
                } for invite in guild_invites
            }
            
            print(f"Initialized invite tracking for {guild.name} with {len(guild_invites)} invites")
        except Exception as e:
            print(f"Error initializing invite tracking for {guild.name}: {e}")
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Clean up invite data when the bot leaves a guild"""
        if guild.id in self.invites:
            del self.invites[guild.id]
        
        if guild.id in self.invite_data:
            del self.invite_data[guild.id]
            self.save_invite_data()
            
        print(f"Removed invite data for {guild.name}")
    
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        """Track new invites"""
        guild_id = invite.guild.id
        
        if guild_id not in self.invites:
            self.invites[guild_id] = {}
        
        self.invites[guild_id][invite.code] = {
            'uses': invite.uses,
            'inviter_id': invite.inviter.id if invite.inviter else None,
            'created_at': invite.created_at.isoformat(),
            'max_uses': invite.max_uses,
            'max_age': invite.max_age,
            'temporary': invite.temporary,
            'channel_id': invite.channel.id
        }
        
        print(f"New invite created in {invite.guild.name}: {invite.code}")
    
    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        """Handle deleted invites"""
        guild_id = invite.guild.id
        
        if guild_id in self.invites and invite.code in self.invites[guild_id]:
            del self.invites[guild_id][invite.code]
            print(f"Invite deleted in {invite.guild.name}: {invite.code}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Track which invite was used when a member joins"""
        guild = member.guild
        
        if not guild.me.guild_permissions.manage_guild:
            print(f"Missing manage_guild permission in {guild.name}, can't track invites")
            return
            
        if member.bot:
            return
            
        try:
            await asyncio.sleep(1)
            
            current_invites = await guild.invites()
            
            current_invites_dict = {
                invite.code: {
                    'uses': invite.uses,
                    'inviter_id': invite.inviter.id if invite.inviter else None
                } for invite in current_invites
            }
            
            used_invite = None
            used_invite_code = None
            
            if guild.id in self.invites:
                for invite_code, invite_data in current_invites_dict.items():
                    if invite_code not in self.invites[guild.id]:
                        continue
                        
                    cached_uses = self.invites[guild.id][invite_code]['uses']
                    current_uses = invite_data['uses']
                    
                    if current_uses > cached_uses:
                        used_invite_code = invite_code
                        used_invite = next((inv for inv in current_invites if inv.code == invite_code), None)
                        break
            
            self.invites[guild.id] = {
                invite.code: {
                    'uses': invite.uses,
                    'inviter_id': invite.inviter.id if invite.inviter else None,
                    'created_at': invite.created_at.isoformat(),
                    'max_uses': invite.max_uses,
                    'max_age': invite.max_age,
                    'temporary': invite.temporary,
                    'channel_id': invite.channel.id
                } for invite in current_invites
            }
            
            if used_invite and used_invite.inviter:
                inviter_id = used_invite.inviter.id
                
                if guild.id not in self.invite_data:
                    self.invite_data[guild.id] = {}
                
                if inviter_id not in self.invite_data[guild.id]:
                    self.invite_data[guild.id][inviter_id] = {
                        'total_invites': 0,
                        'active_invites': 0,
                        'left_invites': 0,
                        'fake_invites': 0,
                        'invited_users': []
                    }
                
                self.invite_data[guild.id][inviter_id]['total_invites'] += 1
                self.invite_data[guild.id][inviter_id]['active_invites'] += 1
                
                invited_user_data = {
                    'user_id': member.id,
                    'username': f"{member.name}#{member.discriminator}",
                    'joined_at': datetime.datetime.utcnow().isoformat(),
                    'invite_code': used_invite_code
                }
                self.invite_data[guild.id][inviter_id]['invited_users'].append(invited_user_data)
                
                self.save_invite_data()
                
                print(f"Member {member.name} joined {guild.name} using invite {used_invite_code} from {used_invite.inviter.name}")
            else:
                print(f"Couldn't determine which invite was used for {member.name} in {guild.name}")
                
        except Exception as e:
            print(f"Error tracking invite for {member.name} in {guild.name}: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Update stats when a member leaves"""
        guild = member.guild
        
        if member.bot:
            return
            
        try:
            if guild.id in self.invite_data:
                for inviter_id, inviter_data in self.invite_data[guild.id].items():
                    for invited_user in inviter_data['invited_users']:
                        if invited_user['user_id'] == member.id:
                            self.invite_data[guild.id][inviter_id]['active_invites'] -= 1
                            self.invite_data[guild.id][inviter_id]['left_invites'] += 1
                            
                            invited_user['left_at'] = datetime.datetime.utcnow().isoformat()
                            
                            self.save_invite_data()
                            
                            print(f"Updated stats for inviter {inviter_id} after {member.name} left {guild.name}")
                            break
        except Exception as e:
            print(f"Error updating invite stats for {member.name} in {guild.name}: {e}")
    
    invite_group = app_commands.Group(name="invites", description="Invite tracking commands")
    
    @invite_group.command(name="stats", description="Show your invite statistics")
    async def invite_stats(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Show invite statistics for a user"""
        await interaction.response.defer()
        
        target_user = user or interaction.user
        guild = interaction.guild
        
        if guild.id not in self.invite_data:
            await interaction.followup.send("No invite data available for this server yet.")
            return
            
        if target_user.id not in self.invite_data[guild.id]:
            if target_user == interaction.user:
                await interaction.followup.send("You haven't invited anyone to this server yet.")
            else:
                await interaction.followup.send(f"{target_user.mention} hasn't invited anyone to this server yet.")
            return
            
        user_data = self.invite_data[guild.id][target_user.id]
        
        embed = discord.Embed(
            title=f"Invite Statistics for {target_user.display_name}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        embed.add_field(name="Total Invites", value=user_data['total_invites'], inline=True)
        embed.add_field(name="Active Members", value=user_data['active_invites'], inline=True)
        embed.add_field(name="Left Members", value=user_data['left_invites'], inline=True)
        embed.add_field(name="Fake Invites", value=user_data['fake_invites'], inline=True)
        
        recent_invites = sorted(user_data['invited_users'], key=lambda x: x['joined_at'], reverse=True)[:10]
        
        if recent_invites:
            recent_list = []
            for i, invite_data in enumerate(recent_invites, 1):
                user_id = invite_data['user_id']
                username = invite_data['username']
                joined_at = datetime.datetime.fromisoformat(invite_data['joined_at'])
                
                member = guild.get_member(user_id)
                status = "Active" if member else "Left"
                
                joined_str = f"<t:{int(joined_at.timestamp())}:R>"
                
                recent_list.append(f"{i}. <@{user_id}> ({status}) - Joined {joined_str}")
            
            embed.add_field(name="Recent Invites", value="\n".join(recent_list), inline=False)
        
        view = InviteDetailsView(target_user.id)
        
        await interaction.followup.send(embed=embed, view=view)
    
    @invite_group.command(name="leaderboard", description="Show the invite leaderboard")
    async def invite_leaderboard(self, interaction: discord.Interaction, page: int = 1):
        """Show the invite leaderboard for the server"""
        await interaction.response.defer()
        await self.show_leaderboard(interaction, interaction.guild.id, page)
    
    async def show_leaderboard(self, interaction: discord.Interaction, guild_id: int, page: int = 1, entries_per_page: int = 10, message: Optional[discord.Message] = None):
        """Show the invite leaderboard for a guild"""
        guild = self.bot.get_guild(guild_id)
        
        if not guild:
            await interaction.followup.send("Guild not found.")
            return
            
        if guild_id not in self.invite_data:
            await interaction.followup.send("No invite data available for this server yet.")
            return
            
        sorted_inviters = sorted(
            self.invite_data[guild_id].items(),
            key=lambda x: (x[1]['total_invites'], x[1]['active_invites']),
            reverse=True
        )
        
        total_entries = len(sorted_inviters)
        max_pages = (total_entries + entries_per_page - 1) // entries_per_page
        
        if page < 1:
            page = 1
        elif page > max_pages:
            page = max_pages
            
        start_idx = (page - 1) * entries_per_page
        end_idx = min(start_idx + entries_per_page, total_entries)
        page_entries = sorted_inviters[start_idx:end_idx]
        
        embed = discord.Embed(
            title=f"Invite Leaderboard for {guild.name}",
            description=f"Showing top inviters (Page {page}/{max_pages})",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        leaderboard_text = []
        
        for i, (inviter_id, inviter_data) in enumerate(page_entries, start_idx + 1):
            member = guild.get_member(int(inviter_id))
            name = member.mention if member else f"User ID: {inviter_id}"
            
            leaderboard_text.append(
                f"{i}. {name} - **{inviter_data['total_invites']}** invites " +
                f"({inviter_data['active_invites']} active, {inviter_data['left_invites']} left)"
            )
        
        if leaderboard_text:
            embed.description += "\n\n" + "\n".join(leaderboard_text)
        else:
            embed.description += "\n\nNo invite data available."
        
        view = InviteLeaderboardView(self, guild_id, page, entries_per_page)
        view.max_pages = max_pages
        
        if message:
            await message.edit(embed=embed, view=view)
        else:
            await interaction.followup.send(embed=embed, view=view)
    
    @invite_group.command(name="lookup", description="Look up who invited a user")
    async def invite_lookup(self, interaction: discord.Interaction, user: discord.Member):
        """Look up who invited a specific user"""
        await interaction.response.defer()
        
        guild = interaction.guild
        
        if guild.id not in self.invite_data:
            await interaction.followup.send("No invite data available for this server yet.")
            return
            
        inviter_found = False
        
        for inviter_id, inviter_data in self.invite_data[guild.id].items():
            for invited_user in inviter_data['invited_users']:
                if invited_user['user_id'] == user.id:
                    inviter = guild.get_member(int(inviter_id))
                    inviter_name = inviter.mention if inviter else f"User ID: {inviter_id}"
                    
                    invite_code = invited_user.get('invite_code', 'Unknown')
                    joined_at = datetime.datetime.fromisoformat(invited_user['joined_at'])
                    joined_str = f"<t:{int(joined_at.timestamp())}:F>"
                    
                    embed = discord.Embed(
                        title=f"Invite Lookup for {user.display_name}",
                        description=f"{user.mention} was invited by {inviter_name}",
                        color=discord.Color.green(),
                        timestamp=datetime.datetime.now()
                    )
                    
                    embed.set_thumbnail(url=user.display_avatar.url)
                    
                    embed.add_field(name="Joined At", value=joined_str, inline=True)
                    embed.add_field(name="Invite Code", value=invite_code, inline=True)
                    
                    if 'left_at' in invited_user:
                        left_at = datetime.datetime.fromisoformat(invited_user['left_at'])
                        left_str = f"<t:{int(left_at.timestamp())}:F>"
                        embed.add_field(name="Left At", value=left_str, inline=True)
                    
                    view = View(timeout=180)
                    view.add_item(Button(label="User Profile", url=f"discord://-/users/{user.id}", style=discord.ButtonStyle.link))
                    
                    if inviter:
                        view.add_item(Button(label="Inviter Profile", url=f"discord://-/users/{inviter_id}", style=discord.ButtonStyle.link))
                    
                    await interaction.followup.send(embed=embed, view=view)
                    inviter_found = True
                    break
            
            if inviter_found:
                break
        
        if not inviter_found:
            await interaction.followup.send(f"No invite information found for {user.mention}. They may have joined via a server discovery, public link, or before the bot was added.")
    
    @invite_group.command(name="reset", description="Reset invite tracking data")
    @app_commands.default_permissions(administrator=True)
    async def invite_reset(self, interaction: discord.Interaction, confirm: bool = False):
        """Reset all invite tracking data for this server (admin only)"""
        await interaction.response.defer(ephemeral=True)
        
        if not confirm:
            await interaction.followup.send(
                "⚠️ This will reset ALL invite tracking data for this server. " +
                "To confirm, run the command again with `confirm: True`.",
                ephemeral=True
            )
            return
            
        guild_id = interaction.guild.id
        
        if guild_id in self.invite_data:
            del self.invite_data[guild_id]
            self.save_invite_data()
            
            try:
                guild_invites = await interaction.guild.invites()
                self.invites[guild_id] = {
                    invite.code: {
                        'uses': invite.uses,
                        'inviter_id': invite.inviter.id if invite.inviter else None,
                        'created_at': invite.created_at.isoformat(),
                        'max_uses': invite.max_uses,
                        'max_age': invite.max_age,
                        'temporary': invite.temporary,
                        'channel_id': invite.channel.id
                    } for invite in guild_invites
                }
            except Exception as e:
                print(f"Error re-caching invites after reset: {e}")
            
            await interaction.followup.send("✅ Invite tracking data has been reset for this server.", ephemeral=True)
        else:
            await interaction.followup.send("No invite data found for this server.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(InviteTracker(bot))