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
from typing import Optional, Union, List

class ModerationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")

    mod_group = app_commands.Group(name="mod", description="Discord moderation commands")

    @mod_group.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(
        member="The member to kick",
        reason="Reason for kicking the member"
    )
    @app_commands.default_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.kick_members:
                await interaction.followup.send("I don't have permission to kick members.")
                return
                
            if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
                await interaction.followup.send("You cannot kick someone with a higher or equal role.")
                return
            if member.top_role >= interaction.guild.me.top_role:
                await interaction.followup.send("I cannot kick this user due to role hierarchy.")
                return
                
            embed = discord.Embed(
                title="Member Kicked",
                description=f"{member.mention} has been kicked from the server.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=interaction.user.mention)
            embed.set_thumbnail(url=member.display_avatar.url)
            
            try:
                dm_embed = discord.Embed(
                    title=f"You've been kicked from {interaction.guild.name}",
                    description=f"Reason: {reason}",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                await member.send(embed=dm_embed)
            except:
                pass
                
            await member.kick(reason=f"{interaction.user} - {reason}")
            
            await interaction.followup.send(embed=embed)
            
            await self.log_moderation_action(
                guild=interaction.guild,
                action="Kick",
                target=member,
                moderator=interaction.user,
                reason=reason
            )
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @mod_group.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(
        member="The member to ban",
        delete_days="Number of days of messages to delete (0-7)",
        reason="Reason for banning the member"
    )
    @app_commands.default_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        delete_days: int = 1,
        reason: str = "No reason provided"
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.ban_members:
                await interaction.followup.send("I don't have permission to ban members.")
                return
                
            if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
                await interaction.followup.send("You cannot ban someone with a higher or equal role.")
                return
                
            if member.top_role >= interaction.guild.me.top_role:
                await interaction.followup.send("I cannot ban this user due to role hierarchy.")
                return
                
            delete_days = max(0, min(7, delete_days))
                
            embed = discord.Embed(
                title="Member Banned",
                description=f"{member.mention} has been banned from the server.",
                color=discord.Color.dark_red(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=interaction.user.mention)
            embed.add_field(name="Message Deletion", value=f"{delete_days} days")
            embed.set_thumbnail(url=member.display_avatar.url)
            
            try:
                dm_embed = discord.Embed(
                    title=f"You've been banned from {interaction.guild.name}",
                    description=f"Reason: {reason}",
                    color=discord.Color.dark_red(),
                    timestamp=datetime.datetime.now()
                )
                await member.send(embed=dm_embed)
            except:
                pass
                
            await member.ban(delete_message_days=delete_days, reason=f"{interaction.user} - {reason}")
            
            await interaction.followup.send(embed=embed)
            
            await self.log_moderation_action(
                guild=interaction.guild,
                action="Ban",
                target=member,
                moderator=interaction.user,
                reason=reason
            )
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @mod_group.command(name="unban", description="Unban a user from the server")
    @app_commands.describe(
        user_id="The ID of the user to unban",
        reason="Reason for unbanning the user"
    )
    @app_commands.default_permissions(ban_members=True)
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str,
        reason: str = "No reason provided"
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.ban_members:
                await interaction.followup.send("I don't have permission to unban users.")
                return
                
            try:
                user_id = int(user_id)
            except ValueError:
                await interaction.followup.send("Invalid user ID. Please provide a valid user ID.")
                return
                
            bans = [ban_entry async for ban_entry in interaction.guild.bans()]
            banned_user = discord.utils.get(bans, user__id=user_id)
            
            if not banned_user:
                await interaction.followup.send("This user is not banned.")
                return

            embed = discord.Embed(
                title="User Unbanned",
                description=f"{banned_user.user} has been unbanned from the server.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=interaction.user.mention)
            embed.set_thumbnail(url=banned_user.user.display_avatar.url)
            
            await interaction.guild.unban(banned_user.user, reason=f"{interaction.user} - {reason}")
            
            await interaction.followup.send(embed=embed)
            
            await self.log_moderation_action(
                guild=interaction.guild,
                action="Unban",
                target=banned_user.user,
                moderator=interaction.user,
                reason=reason
            )
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @mod_group.command(name="timeout", description="Timeout (mute) a member")
    @app_commands.describe(
        member="The member to timeout",
        duration="Duration in minutes (max 40320 = 28 days)",
        reason="Reason for the timeout"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        duration: int,
        reason: str = "No reason provided"
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.moderate_members:
                await interaction.followup.send("I don't have permission to timeout members.")
                return
                
            if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
                await interaction.followup.send("You cannot timeout someone with a higher or equal role.")
                return
                
            if member.top_role >= interaction.guild.me.top_role:
                await interaction.followup.send("I cannot timeout this user due to role hierarchy.")
                return
                
            duration = min(40320, max(1, duration))
            
            until = datetime.datetime.now() + datetime.timedelta(minutes=duration)
            
            if duration < 60:
                duration_text = f"{duration} minute(s)"
            elif duration < 1440:
                hours = duration // 60
                minutes = duration % 60
                duration_text = f"{hours} hour(s)"
                if minutes > 0:
                    duration_text += f" and {minutes} minute(s)"
            else:
                days = duration // 1440
                remaining = duration % 1440
                hours = remaining // 60
                minutes = remaining % 60
                duration_text = f"{days} day(s)"
                if hours > 0:
                    duration_text += f" and {hours} hour(s)"
                
            embed = discord.Embed(
                title="Member Timed Out",
                description=f"{member.mention} has been timed out.",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Duration", value=duration_text)
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=interaction.user.mention)
            embed.set_thumbnail(url=member.display_avatar.url)
            
            try:
                dm_embed = discord.Embed(
                    title=f"You've been timed out in {interaction.guild.name}",
                    description=f"Duration: {duration_text}\nReason: {reason}",
                    color=discord.Color.orange(),
                    timestamp=datetime.datetime.now()
                )
                await member.send(embed=dm_embed)
            except:
                pass
                
            await member.timeout(until=until, reason=f"{interaction.user} - {reason}")

            await interaction.followup.send(embed=embed)

            await self.log_moderation_action(
                guild=interaction.guild,
                action="Timeout",
                target=member,
                moderator=interaction.user,
                reason=f"{reason} (Duration: {duration_text})"
            )
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @mod_group.command(name="remove_timeout", description="Remove timeout from a member")
    @app_commands.describe(
        member="The member to remove timeout from",
        reason="Reason for removing the timeout"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def remove_timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.moderate_members:
                await interaction.followup.send("I don't have permission to manage timeouts.")
                return
                
            if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
                await interaction.followup.send("You cannot modify timeout for someone with a higher or equal role.")
                return
                
            if not member.is_timed_out():
                await interaction.followup.send(f"{member.mention} is not currently timed out.")
                return
                
            embed = discord.Embed(
                title="Timeout Removed",
                description=f"Timeout has been removed from {member.mention}.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=interaction.user.mention)
            embed.set_thumbnail(url=member.display_avatar.url)
            
            await member.timeout(until=None, reason=f"{interaction.user} - {reason}")
            
            await interaction.followup.send(embed=embed)
            
            await self.log_moderation_action(
                guild=interaction.guild,
                action="Timeout Removed",
                target=member,
                moderator=interaction.user,
                reason=reason
            )
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @mod_group.command(name="purge", description="Delete a specified number of messages")
    @app_commands.describe(
        amount="Number of messages to delete (1-100)",
        user="Only delete messages from this user (optional)",
        contains="Only delete messages containing this text (optional)"
    )
    @app_commands.default_permissions(manage_messages=True)
    async def purge(
        self,
        interaction: discord.Interaction,
        amount: int,
        user: Optional[discord.Member] = None,
        contains: Optional[str] = None
    ):
        await interaction.response.defer(ephemeral=True)
        
        try:
            if not interaction.guild.me.guild_permissions.manage_messages:
                await interaction.followup.send("I don't have permission to delete messages.")
                return
                
            amount = min(100, max(1, amount))
            
            def check(message):
                result = True
                if user is not None:
                    result = result and message.author.id == user.id
                if contains is not None:
                    result = result and contains.lower() in message.content.lower()
                return result
            
            deleted = await interaction.channel.purge(
                limit=amount,
                check=check,
                before=interaction.created_at,
                reason=f"Purge command used by {interaction.user}"
            )
            
            embed = discord.Embed(
                title="Messages Purged",
                description=f"Deleted {len(deleted)} message(s).",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            if user:
                embed.add_field(name="User Filter", value=user.mention)
            if contains:
                embed.add_field(name="Content Filter", value=f"`{contains}`")
            
            await interaction.followup.send(embed=embed)
            
            await self.log_moderation_action(
                guild=interaction.guild,
                action="Purge",
                target=f"{len(deleted)} messages in #{interaction.channel.name}",
                moderator=interaction.user,
                reason=f"Amount: {amount}, User: {user.name if user else 'Any'}, Contains: {contains if contains else 'Any'}"
            )
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @mod_group.command(name="slowmode", description="Set slowmode for the current channel")
    @app_commands.describe(
        seconds="Slowmode delay in seconds (0 to disable, max 21600 = 6 hours)",
        reason="Reason for changing slowmode"
    )
    @app_commands.default_permissions(manage_channels=True)
    async def slowmode(
        self,
        interaction: discord.Interaction,
        seconds: int,
        reason: str = "No reason provided"
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.manage_channels:
                await interaction.followup.send("I don't have permission to manage channels.")
                return
                
            seconds = min(21600, max(0, seconds))
            
            await interaction.channel.edit(slowmode_delay=seconds, reason=f"{interaction.user} - {reason}")
            
            if seconds == 0:
                embed = discord.Embed(
                    title="Slowmode Disabled",
                    description=f"Slowmode has been disabled in {interaction.channel.mention}.",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now()
                )
            else:
                if seconds < 60:
                    duration_text = f"{seconds} second(s)"
                elif seconds < 3600:
                    minutes = seconds // 60
                    secs = seconds % 60
                    duration_text = f"{minutes} minute(s)"
                    if secs > 0:
                        duration_text += f" and {secs} second(s)"
                else:
                    hours = seconds // 3600
                    remaining = seconds % 3600
                    minutes = remaining // 60
                    secs = remaining % 60
                    duration_text = f"{hours} hour(s)"
                    if minutes > 0:
                        duration_text += f" and {minutes} minute(s)"
                
                embed = discord.Embed(
                    title="Slowmode Enabled",
                    description=f"Slowmode set to {duration_text} in {interaction.channel.mention}.",
                    color=discord.Color.orange(),
                    timestamp=datetime.datetime.now()
                )
            
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=interaction.user.mention)

            await interaction.followup.send(embed=embed)
            
            await self.log_moderation_action(
                guild=interaction.guild,
                action="Slowmode" if seconds > 0 else "Slowmode Disabled",
                target=f"#{interaction.channel.name}",
                moderator=interaction.user,
                reason=f"{reason} ({duration_text if seconds > 0 else 'Disabled'})"
            )
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @mod_group.command(name="warn", description="Warn a member")
    @app_commands.describe(
        member="The member to warn",
        reason="Reason for the warning"
    )
    @app_commands.default_permissions(kick_members=True)
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            embed = discord.Embed(
                title="Member Warned",
                description=f"{member.mention} has been warned.",
                color=discord.Color.yellow(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=interaction.user.mention)
            embed.set_thumbnail(url=member.display_avatar.url)
            
            try:
                dm_embed = discord.Embed(
                    title=f"Warning from {interaction.guild.name}",
                    description=f"You have received a warning from the moderators.",
                    color=discord.Color.yellow(),
                    timestamp=datetime.datetime.now()
                )
                dm_embed.add_field(name="Reason", value=reason)
                await member.send(embed=dm_embed)
                embed.add_field(name="DM", value="Warning sent to user's DMs", inline=False)
            except:
                embed.add_field(name="DM", value="Could not send warning to user's DMs", inline=False)
            
            await interaction.followup.send(embed=embed)
            
            await self.log_moderation_action(
                guild=interaction.guild,
                action="Warning",
                target=member,
                moderator=interaction.user,
                reason=reason
            )
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @mod_group.command(name="lock", description="Lock a channel")
    @app_commands.describe(
        channel="The channel to lock (defaults to current channel)",
        reason="Reason for locking the channel"
    )
    @app_commands.default_permissions(manage_channels=True)
    async def lock(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
        reason: str = "No reason provided"
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if channel is None:
                channel = interaction.channel
                
            if not interaction.guild.me.guild_permissions.manage_channels:
                await interaction.followup.send("I don't have permission to manage channels.")
                return
                
            default_role = interaction.guild.default_role
            
            await channel.set_permissions(
                default_role,
                send_messages=False,
                reason=f"{interaction.user} - {reason}"
            )
            
            embed = discord.Embed(
                title="Channel Locked",
                description=f"{channel.mention} has been locked.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=interaction.user.mention)
            
            await interaction.followup.send(embed=embed)
            
            channel_embed = discord.Embed(
                title="🔒 Channel Locked",
                description="This channel has been locked by a moderator.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            channel_embed.add_field(name="Reason", value=reason)
            
            await channel.send(embed=channel_embed)
            
            await self.log_moderation_action(
                guild=interaction.guild,
                action="Channel Lock",
                target=f"#{channel.name}",
                moderator=interaction.user,
                reason=reason
            )
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @mod_group.command(name="unlock", description="Unlock a channel")
    @app_commands.describe(
        channel="The channel to unlock (defaults to current channel)",
        reason="Reason for unlocking the channel"
    )
    @app_commands.default_permissions(manage_channels=True)
    async def unlock(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
        reason: str = "No reason provided"
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if channel is None:
                channel = interaction.channel
                
            if not interaction.guild.me.guild_permissions.manage_channels:
                await interaction.followup.send("I don't have permission to manage channels.")
                return
                
            default_role = interaction.guild.default_role
            
            await channel.set_permissions(
                default_role,
                send_messages=None,
                reason=f"{interaction.user} - {reason}"
            )
            
            embed = discord.Embed(
                title="Channel Unlocked",
                description=f"{channel.mention} has been unlocked.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=interaction.user.mention)
            
            await interaction.followup.send(embed=embed)
            
            channel_embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description="This channel has been unlocked by a moderator.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            channel_embed.add_field(name="Reason", value=reason)
            
            await channel.send(embed=channel_embed)
            
            await self.log_moderation_action(
                guild=interaction.guild,
                action="Channel Unlock",
                target=f"#{channel.name}",
                moderator=interaction.user,
                reason=reason
            )
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    async def log_moderation_action(self, guild, action, target, moderator, reason):
        """Log a moderation action to the configured log channel"""
        log_channel_id = os.getenv(f"LOG_CHANNEL_{guild.id}")
        
        if not log_channel_id:
            return
            
        try:
            log_channel = guild.get_channel(int(log_channel_id))
            if not log_channel:
                return
                
            embed = discord.Embed(
                title=f"Moderation Action: {action}",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            if isinstance(target, discord.Member) or isinstance(target, discord.User):
                embed.add_field(name="User", value=f"{target.mention} ({target.name}#{target.discriminator})")
                embed.add_field(name="User ID", value=target.id)
                embed.set_thumbnail(url=target.display_avatar.url)
            else:
                embed.add_field(name="Target", value=str(target))
            
            embed.add_field(name="Moderator", value=f"{moderator.mention} ({moderator.name}#{moderator.discriminator})")
            
            embed.add_field(name="Reason", value=reason, inline=False)
            
            action_id = f"{int(datetime.datetime.now().timestamp())}"
            embed.set_footer(text=f"Action ID: {action_id}")
            
            await log_channel.send(embed=embed)
            
        except Exception as e:
            print(f"Failed to log moderation action: {e}")

async def setup(bot):
    cog = ModerationCommands(bot)
    await bot.add_cog(cog)
    
    await register_context_menus(bot)

async def register_context_menus(bot):
    """Register all context menu commands"""
    bot.tree.add_command(kick_user_context)
    bot.tree.add_command(ban_user_context)
    bot.tree.add_command(timeout_user_context)
    bot.tree.add_command(warn_user_context)
    bot.tree.add_command(user_info_context)
    
    bot.tree.add_command(delete_message_context)
    bot.tree.add_command(warn_for_message_context)
    
    print("Registered moderation context menu commands")


@app_commands.context_menu(name="Kick User")
@app_commands.default_permissions(kick_members=True)
async def kick_user_context(interaction: discord.Interaction, member: discord.Member):
    """Context menu command to kick a user"""
    MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
    
    class KickModal(discord.ui.Modal, title="Kick User"):
        reason = discord.ui.TextInput(
            label="Reason",
            placeholder="Enter reason for kick...",
            default="No reason provided",
            required=False,
            max_length=1000
        )
        
        async def on_submit(self, modal_interaction: discord.Interaction):
            await modal_interaction.response.defer(ephemeral=MESSAGE)
            
            try:
                if not modal_interaction.guild.me.guild_permissions.kick_members:
                    await modal_interaction.followup.send("I don't have permission to kick members.")
                    return
                    
                if member.top_role >= modal_interaction.user.top_role and modal_interaction.user.id != modal_interaction.guild.owner_id:
                    await modal_interaction.followup.send("You cannot kick someone with a higher or equal role.")
                    return
                    
                if member.top_role >= modal_interaction.guild.me.top_role:
                    await modal_interaction.followup.send("I cannot kick this user due to role hierarchy.")
                    return
                    
                embed = discord.Embed(
                    title="Member Kicked",
                    description=f"{member.mention} has been kicked from the server.",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                
                embed.add_field(name="Reason", value=self.reason.value)
                embed.add_field(name="Moderator", value=modal_interaction.user.mention)
                embed.set_thumbnail(url=member.display_avatar.url)
                
                try:
                    dm_embed = discord.Embed(
                        title=f"You've been kicked from {modal_interaction.guild.name}",
                        description=f"Reason: {self.reason.value}",
                        color=discord.Color.red(),
                        timestamp=datetime.datetime.now()
                    )
                    await member.send(embed=dm_embed)
                except:
                    pass
                    
                await member.kick(reason=f"{modal_interaction.user} - {self.reason.value}")
                
                await modal_interaction.followup.send(embed=embed)
                
                try:
                    mod_cog = modal_interaction.client.get_cog("ModerationCommands")
                    if mod_cog:
                        await mod_cog.log_moderation_action(
                            guild=modal_interaction.guild,
                            action="Kick",
                            target=member,
                            moderator=modal_interaction.user,
                            reason=self.reason.value
                        )
                except Exception as log_error:
                    print(f"Failed to log moderation action: {log_error}")
                
            except Exception as e:
                await modal_interaction.followup.send(f"Error: {str(e)}")
    
    await interaction.response.send_modal(KickModal())

@app_commands.context_menu(name="Ban User")
@app_commands.default_permissions(ban_members=True)
async def ban_user_context(interaction: discord.Interaction, member: discord.Member):
    """Context menu command to ban a user"""
    MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
    
    class BanModal(discord.ui.Modal, title="Ban User"):
        reason = discord.ui.TextInput(
            label="Reason",
            placeholder="Enter reason for ban...",
            default="No reason provided",
            required=False,
            max_length=1000
        )
        
        delete_days = discord.ui.TextInput(
            label="Delete Message Days (0-7)",
            placeholder="Enter number of days of messages to delete",
            default="1",
            required=True,
            max_length=1
        )
        
        async def on_submit(self, modal_interaction: discord.Interaction):
            await modal_interaction.response.defer(ephemeral=MESSAGE)
            
            try:
                delete_days_value = int(self.delete_days.value)
                if delete_days_value < 0 or delete_days_value > 7:
                    await modal_interaction.followup.send("Delete message days must be between 0 and 7.")
                    return
            except ValueError:
                await modal_interaction.followup.send("Delete message days must be a number between 0 and 7.")
                return
            
            try:
                if not modal_interaction.guild.me.guild_permissions.ban_members:
                    await modal_interaction.followup.send("I don't have permission to ban members.")
                    return
                    
                if member.top_role >= modal_interaction.user.top_role and modal_interaction.user.id != modal_interaction.guild.owner_id:
                    await modal_interaction.followup.send("You cannot ban someone with a higher or equal role.")
                    return

                if member.top_role >= modal_interaction.guild.me.top_role:
                    await modal_interaction.followup.send("I cannot ban this user due to role hierarchy.")
                    return
                    
                embed = discord.Embed(
                    title="Member Banned",
                    description=f"{member.mention} has been banned from the server.",
                    color=discord.Color.dark_red(),
                    timestamp=datetime.datetime.now()
                )
                
                embed.add_field(name="Reason", value=self.reason.value)
                embed.add_field(name="Moderator", value=modal_interaction.user.mention)
                embed.add_field(name="Message Deletion", value=f"{delete_days_value} days")
                embed.set_thumbnail(url=member.display_avatar.url)
                
                try:
                    dm_embed = discord.Embed(
                        title=f"You've been banned from {modal_interaction.guild.name}",
                        description=f"Reason: {self.reason.value}",
                        color=discord.Color.dark_red(),
                        timestamp=datetime.datetime.now()
                    )
                    await member.send(embed=dm_embed)
                except:
                    pass
                    
                await member.ban(delete_message_days=delete_days_value, reason=f"{modal_interaction.user} - {self.reason.value}")
                
                await modal_interaction.followup.send(embed=embed)
                
                try:
                    mod_cog = modal_interaction.client.get_cog("ModerationCommands")
                    if mod_cog:
                        await mod_cog.log_moderation_action(
                            guild=modal_interaction.guild,
                            action="Ban",
                            target=member,
                            moderator=modal_interaction.user,
                            reason=self.reason.value
                        )
                except Exception as log_error:
                    print(f"Failed to log moderation action: {log_error}")
                
            except Exception as e:
                await modal_interaction.followup.send(f"Error: {str(e)}")
    
    await interaction.response.send_modal(BanModal())

@app_commands.context_menu(name="Timeout User")
@app_commands.default_permissions(moderate_members=True)
async def timeout_user_context(interaction: discord.Interaction, member: discord.Member):
    """Context menu command to timeout a user"""
    MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
    
    class TimeoutModal(discord.ui.Modal, title="Timeout User"):
        reason = discord.ui.TextInput(
            label="Reason",
            placeholder="Enter reason for timeout...",
            default="No reason provided",
            required=False,
            max_length=1000
        )
        
        duration = discord.ui.TextInput(
            label="Duration in Minutes",
            placeholder="Enter timeout duration in minutes",
            default="60",
            required=True,
            max_length=5
        )
        
        async def on_submit(self, modal_interaction: discord.Interaction):
            await modal_interaction.response.defer(ephemeral=MESSAGE)
            
            try:
                duration_value = int(self.duration.value)
                if duration_value <= 0:
                    await modal_interaction.followup.send("Duration must be a positive number.")
                    return
                if duration_value > 40320:
                    await modal_interaction.followup.send("Duration cannot exceed 28 days (40320 minutes).")
                    return
            except ValueError:
                await modal_interaction.followup.send("Duration must be a valid number.")
                return
            
            try:
                if not modal_interaction.guild.me.guild_permissions.moderate_members:
                    await modal_interaction.followup.send("I don't have permission to timeout members.")
                    return
                    
                if member.top_role >= modal_interaction.user.top_role and modal_interaction.user.id != modal_interaction.guild.owner_id:
                    await modal_interaction.followup.send("You cannot timeout someone with a higher or equal role.")
                    return
                    
                if member.top_role >= modal_interaction.guild.me.top_role:
                    await modal_interaction.followup.send("I cannot timeout this user due to role hierarchy.")
                    return
                    
                until = datetime.datetime.now() + datetime.timedelta(minutes=duration_value)
                
                if duration_value < 60:
                    duration_text = f"{duration_value} minute(s)"
                elif duration_value < 1440:
                    hours = duration_value // 60
                    minutes = duration_value % 60
                    duration_text = f"{hours} hour(s)"
                    if minutes > 0:
                        duration_text += f" and {minutes} minute(s)"
                else:
                    days = duration_value // 1440
                    remaining = duration_value % 1440
                    hours = remaining // 60
                    minutes = remaining % 60
                    duration_text = f"{days} day(s)"
                    if hours > 0:
                        duration_text += f" and {hours} hour(s)"
                
                embed = discord.Embed(
                    title="Member Timed Out",
                    description=f"{member.mention} has been timed out.",
                    color=discord.Color.orange(),
                    timestamp=datetime.datetime.now()
                )
                
                embed.add_field(name="Duration", value=duration_text)
                embed.add_field(name="Reason", value=self.reason.value)
                embed.add_field(name="Moderator", value=modal_interaction.user.mention)
                embed.set_thumbnail(url=member.display_avatar.url)

                try:
                    dm_embed = discord.Embed(
                        title=f"You've been timed out in {modal_interaction.guild.name}",
                        description=f"Duration: {duration_text}\nReason: {self.reason.value}",
                        color=discord.Color.orange(),
                        timestamp=datetime.datetime.now()
                    )
                    await member.send(embed=dm_embed)
                except:
                    pass
                    
                await member.timeout(until=until, reason=f"{modal_interaction.user} - {self.reason.value}")
                
                await modal_interaction.followup.send(embed=embed)
                
                try:
                    mod_cog = modal_interaction.client.get_cog("ModerationCommands")
                    if mod_cog:
                        await mod_cog.log_moderation_action(
                            guild=modal_interaction.guild,
                            action="Timeout",
                            target=member,
                            moderator=modal_interaction.user,
                            reason=f"{self.reason.value} (Duration: {duration_text})"
                        )
                except Exception as log_error:
                    print(f"Failed to log moderation action: {log_error}")
                
            except Exception as e:
                await modal_interaction.followup.send(f"Error: {str(e)}")
    
    await interaction.response.send_modal(TimeoutModal())

@app_commands.context_menu(name="Warn User")
@app_commands.default_permissions(moderate_members=True)
async def warn_user_context(interaction: discord.Interaction, member: discord.Member):
    """Context menu command to warn a user"""
    MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")

    class WarnModal(discord.ui.Modal, title="Warn User"):
        reason = discord.ui.TextInput(
            label="Reason",
            placeholder="Enter reason for warning...",
            required=True,
            max_length=1000
        )
        
        async def on_submit(self, modal_interaction: discord.Interaction):
            await modal_interaction.response.defer(ephemeral=MESSAGE)
            
            if member.top_role >= modal_interaction.user.top_role and modal_interaction.user.id != modal_interaction.guild.owner_id:
                await modal_interaction.followup.send("You cannot warn someone with a higher or equal role.")
                return
            
            try:
                try:
                    dm_embed = discord.Embed(
                        title=f"You've been warned in {modal_interaction.guild.name}",
                        description=f"Reason: {self.reason.value}",
                        color=discord.Color.yellow(),
                        timestamp=datetime.datetime.now()
                    )
                    await member.send(embed=dm_embed)
                except:
                    pass
                
                embed = discord.Embed(
                    title="Member Warned",
                    description=f"{member.mention} has been warned.",
                    color=discord.Color.yellow(),
                    timestamp=datetime.datetime.now()
                )
                
                embed.add_field(name="Reason", value=self.reason.value)
                embed.add_field(name="Moderator", value=modal_interaction.user.mention)
                embed.set_thumbnail(url=member.display_avatar.url)
                
                await modal_interaction.followup.send(embed=embed)
                
                try:
                    mod_cog = modal_interaction.client.get_cog("ModerationCommands")
                    if mod_cog:
                        await mod_cog.log_moderation_action(
                            guild=modal_interaction.guild,
                            action="Warn",
                            target=member,
                            moderator=modal_interaction.user,
                            reason=self.reason.value
                        )
                except Exception as log_error:
                    print(f"Failed to log moderation action: {log_error}")
                
            except Exception as e:
                await modal_interaction.followup.send(f"Error: {str(e)}")
    
    await interaction.response.send_modal(WarnModal())

@app_commands.context_menu(name="User Info")
async def user_info_context(interaction: discord.Interaction, member: discord.Member):
    """Context menu command to show user information"""
    MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
    
    await interaction.response.defer(ephemeral=MESSAGE)
    
    try:
        embed = discord.Embed(
            title="User Information",
            description=f"Information about {member.mention}",
            color=member.color,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Username", value=f"{member.name}#{member.discriminator}")
        embed.add_field(name="User ID", value=member.id)
        embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:F>")
        
        embed.add_field(name="Joined Server", value=f"<t:{int(member.joined_at.timestamp())}:F>" if member.joined_at else "Unknown")
        embed.add_field(name="Nickname", value=member.nick or "None")
        
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        if roles:
            embed.add_field(name=f"Roles [{len(roles)}]", value=" ".join(roles), inline=False)
        else:
            embed.add_field(name="Roles", value="None", inline=False)
        
        key_permissions = []
        if member.guild_permissions.administrator:
            key_permissions.append("Administrator")
        if member.guild_permissions.ban_members:
            key_permissions.append("Ban Members")
        if member.guild_permissions.kick_members:
            key_permissions.append("Kick Members")
        if member.guild_permissions.manage_guild:
            key_permissions.append("Manage Server")
        if member.guild_permissions.manage_channels:
            key_permissions.append("Manage Channels")
        if member.guild_permissions.manage_messages:
            key_permissions.append("Manage Messages")
        if member.guild_permissions.mention_everyone:
            key_permissions.append("Mention Everyone")
        if member.guild_permissions.manage_nicknames:
            key_permissions.append("Manage Nicknames")
        if member.guild_permissions.manage_roles:
            key_permissions.append("Manage Roles")
        if member.guild_permissions.manage_webhooks:
            key_permissions.append("Manage Webhooks")
        if member.guild_permissions.manage_emojis:
            key_permissions.append("Manage Emojis")
        
        if key_permissions:
            embed.add_field(name="Key Permissions", value=", ".join(key_permissions), inline=False)
        
        status_map = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🟡 Idle",
            discord.Status.dnd: "🔴 Do Not Disturb",
            discord.Status.offline: "⚫ Offline"
        }
        embed.add_field(name="Status", value=status_map.get(member.status, "Unknown"))
        
        if member.activity:
            activity_type = str(member.activity.type).split('.')[-1].title()
            activity_name = member.activity.name
            embed.add_field(name="Activity", value=f"{activity_type} {activity_name}")
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.set_footer(text=f"Requested by {interaction.user.name}#{interaction.user.discriminator}")
        
        view = None
        if interaction.user.guild_permissions.kick_members or interaction.user.guild_permissions.ban_members or interaction.user.guild_permissions.moderate_members:
            view = discord.ui.View(timeout=60)
            
            if interaction.user.guild_permissions.kick_members:
                kick_button = discord.ui.Button(label="Kick", style=discord.ButtonStyle.danger, custom_id="kick")
                
                async def kick_callback(i):
                    await i.response.defer(ephemeral=True)
                    await kick_user_context(i, member)
                
                kick_button.callback = kick_callback
                view.add_item(kick_button)
            
            if interaction.user.guild_permissions.ban_members:
                ban_button = discord.ui.Button(label="Ban", style=discord.ButtonStyle.danger, custom_id="ban")
                
                async def ban_callback(i):
                    await i.response.defer(ephemeral=True)
                    await ban_user_context(i, member)
                
                ban_button.callback = ban_callback
                view.add_item(ban_button)
            
            if interaction.user.guild_permissions.moderate_members:
                timeout_button = discord.ui.Button(label="Timeout", style=discord.ButtonStyle.secondary, custom_id="timeout")
                
                async def timeout_callback(i):
                    await i.response.defer(ephemeral=True)
                    await timeout_user_context(i, member)
                
                timeout_button.callback = timeout_callback
                view.add_item(timeout_button)
                
                warn_button = discord.ui.Button(label="Warn", style=discord.ButtonStyle.secondary, custom_id="warn")
                
                async def warn_callback(i):
                    await i.response.defer(ephemeral=True)
                    await warn_user_context(i, member)
                
                warn_button.callback = warn_callback
                view.add_item(warn_button)
        
        await interaction.followup.send(embed=embed, view=view)
        
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}")


@app_commands.context_menu(name="Delete Message")
@app_commands.default_permissions(manage_messages=True)
async def delete_message_context(interaction: discord.Interaction, message: discord.Message):
    """Context menu command to delete a message"""
    MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
    
    await interaction.response.defer(ephemeral=MESSAGE)
    
    try:
        if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
            await interaction.followup.send("I don't have permission to delete messages in this channel.")
            return
        
        if not interaction.channel.permissions_for(interaction.user).manage_messages:
            if message.author.id != interaction.user.id:
                await interaction.followup.send("You don't have permission to delete other users' messages.")
                return
        
        embed = discord.Embed(
            title="Message Deleted",
            description=f"Message from {message.author.mention} deleted in {message.channel.mention}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        
        if message.content:
            content = message.content
            if len(content) > 1024:
                content = content[:1021] + "..."
            embed.add_field(name="Content", value=content, inline=False)
        
        if message.attachments:
            attachment_info = "\n".join([f"[{a.filename}]({a.url})" for a in message.attachments])
            if len(attachment_info) > 1024:
                attachment_info = attachment_info[:1021] + "..."
            embed.add_field(name="Attachments", value=attachment_info, inline=False)
        
        embed.add_field(name="Deleted by", value=interaction.user.mention)
        
        embed.add_field(name="Message ID", value=message.id)
        embed.add_field(name="Created", value=f"<t:{int(message.created_at.timestamp())}:F>")
        
        embed.set_author(name=f"{message.author.name}#{message.author.discriminator}", icon_url=message.author.display_avatar.url)
        
        await message.delete()
        
        await interaction.followup.send(embed=embed)
        
        try:
            mod_cog = interaction.client.get_cog("ModerationCommands")
            if mod_cog:
                await mod_cog.log_moderation_action(
                    guild=interaction.guild,
                    action="Message Delete",
                    target=message.author,
                    moderator=interaction.user,
                    reason=f"Message content: {content if message.content else 'No text content'}"
                )
        except Exception as log_error:
            print(f"Failed to log moderation action: {log_error}")
        
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}")

@app_commands.context_menu(name="Warn for Message")
@app_commands.default_permissions(moderate_members=True)
async def warn_for_message_context(interaction: discord.Interaction, message: discord.Message):
    """Context menu command to warn a user for a message"""
    MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
    
    class WarnForMessageModal(discord.ui.Modal, title="Warn User for Message"):
        reason = discord.ui.TextInput(
            label="Reason",
            placeholder="Enter reason for warning...",
            default="Inappropriate message",
            required=True,
            max_length=1000
        )
        
        async def on_submit(self, modal_interaction: discord.Interaction):
            await modal_interaction.response.defer(ephemeral=MESSAGE)
            
            member = message.author
            
            if not isinstance(member, discord.Member):
                await modal_interaction.followup.send("Cannot warn a user who is not a member of this server.")
                return
            
            if member.top_role >= modal_interaction.user.top_role and modal_interaction.user.id != modal_interaction.guild.owner_id:
                await modal_interaction.followup.send("You cannot warn someone with a higher or equal role.")
                return
            
            try:
                full_reason = f"{self.reason.value}\n\nMessage Content: {message.content}"
                if len(full_reason) > 1900:
                    full_reason = full_reason[:1900] + "..."
                
                try:
                    dm_embed = discord.Embed(
                        title=f"You've been warned in {modal_interaction.guild.name}",
                        description=f"Reason: {self.reason.value}",
                        color=discord.Color.yellow(),
                        timestamp=datetime.datetime.now()
                    )
                    
                    if message.content:
                        content = message.content
                        if len(content) > 1024:
                            content = content[:1021] + "..."
                        dm_embed.add_field(name="Message Content", value=content, inline=False)
                    
                    dm_embed.add_field(name="Message Link", value=f"[Jump to Message]({message.jump_url})")
                    
                    await member.send(embed=dm_embed)
                except:
                    pass
                
                embed = discord.Embed(
                    title="Member Warned for Message",
                    description=f"{member.mention} has been warned.",
                    color=discord.Color.yellow(),
                    timestamp=datetime.datetime.now()
                )
                
                embed.add_field(name="Reason", value=self.reason.value)
                embed.add_field(name="Moderator", value=modal_interaction.user.mention)
                
                if message.content:
                    content = message.content
                    if len(content) > 1024:
                        content = content[:1021] + "..."
                    embed.add_field(name="Message Content", value=content, inline=False)
                
                embed.add_field(name="Message Link", value=f"[Jump to Message]({message.jump_url})")
                
                embed.set_thumbnail(url=member.display_avatar.url)
                
                await modal_interaction.followup.send(embed=embed)
                
                try:
                    mod_cog = modal_interaction.client.get_cog("ModerationCommands")
                    if mod_cog:
                        await mod_cog.log_moderation_action(
                            guild=modal_interaction.guild,
                            action="Warn for Message",
                            target=member,
                            moderator=modal_interaction.user,
                            reason=full_reason
                        )
                except Exception as log_error:
                    print(f"Failed to log moderation action: {log_error}")
                
            except Exception as e:
                await modal_interaction.followup.send(f"Error: {str(e)}")
    
    await interaction.response.send_modal(WarnForMessageModal())