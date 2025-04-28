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
import asyncio
from typing import Optional, List, Union

class ChannelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
        
    channel_group = app_commands.Group(name="channel", description="Channel management commands")
    
    @channel_group.command(name="info", description="Get information about a channel")
    @app_commands.describe(channel="The channel to get information about")
    async def channel_info(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.abc.GuildChannel] = None
    ):
        """Get detailed information about a channel"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            channel = channel or interaction.channel
            
            embed = discord.Embed(
                title=f"Channel Information: {channel.name}",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Channel ID", value=channel.id, inline=True)
            embed.add_field(name="Type", value=str(channel.type).replace('_', ' ').title(), inline=True)
            
            if hasattr(channel, 'category') and channel.category:
                embed.add_field(name="Category", value=channel.category.name, inline=True)
            
            embed.add_field(name="Created On", value=f"<t:{int(channel.created_at.timestamp())}:F>\n(<t:{int(channel.created_at.timestamp())}:R>)", inline=True)
            
            if isinstance(channel, discord.TextChannel):
                embed.add_field(name="Slowmode", value=f"{channel.slowmode_delay} seconds" if channel.slowmode_delay else "Off", inline=True)
                embed.add_field(name="NSFW", value="Yes" if channel.is_nsfw() else "No", inline=True)
                embed.add_field(name="News Channel", value="Yes" if channel.is_news() else "No", inline=True)
                
                if channel.topic:
                    embed.add_field(name="Topic", value=channel.topic[:1024], inline=False)
                    
            elif isinstance(channel, discord.VoiceChannel):
                embed.add_field(name="Bitrate", value=f"{channel.bitrate // 1000} kbps", inline=True)
                embed.add_field(name="User Limit", value=channel.user_limit if channel.user_limit else "Unlimited", inline=True)
                embed.add_field(name="Connected Users", value=len(channel.members), inline=True)
                
            elif isinstance(channel, discord.CategoryChannel):
                embed.add_field(name="Channels", value=len(channel.channels), inline=True)
                
            embed.add_field(name="Position", value=channel.position, inline=True)
            
            if hasattr(channel, 'overwrites') and channel.overwrites:
                overwrite_text = ""
                for target, overwrite in list(channel.overwrites.items())[:5]:
                    if isinstance(target, discord.Role):
                        overwrite_text += f"Role: {target.name}\n"
                    else:
                        overwrite_text += f"Member: {target.display_name}\n"
                        
                if len(channel.overwrites) > 5:
                    overwrite_text += f"And {len(channel.overwrites) - 5} more..."
                    
                if overwrite_text:
                    embed.add_field(name="Permission Overwrites", value=overwrite_text, inline=False)
                    
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @channel_group.command(name="create", description="Create a new channel")
    @app_commands.describe(
        name="The name of the new channel",
        type="The type of channel to create",
        category="The category to place the channel in (optional)",
        topic="The topic for the channel (text channels only)",
        nsfw="Whether the channel is NSFW (text channels only)",
        slowmode="Slowmode delay in seconds (text channels only)",
        user_limit="User limit (voice channels only)",
        bitrate="Bitrate in kbps (voice channels only)"
    )
    @app_commands.choices(type=[
        app_commands.Choice(name="Text Channel", value="text"),
        app_commands.Choice(name="Voice Channel", value="voice"),
        app_commands.Choice(name="Category", value="category"),
        app_commands.Choice(name="News Channel", value="news"),
        app_commands.Choice(name="Stage Channel", value="stage")
    ])
    @app_commands.default_permissions(manage_channels=True)
    async def channel_create(
        self,
        interaction: discord.Interaction,
        name: str,
        type: str,
        category: Optional[discord.CategoryChannel] = None,
        topic: Optional[str] = None,
        nsfw: Optional[bool] = False,
        slowmode: Optional[int] = 0,
        user_limit: Optional[int] = 0,
        bitrate: Optional[int] = 64
    ):
        """Create a new channel"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.manage_channels:
                await interaction.followup.send("I don't have permission to manage channels.")
                return
                
            if type == "text":
                channel = await interaction.guild.create_text_channel(
                    name=name,
                    category=category,
                    topic=topic,
                    nsfw=nsfw,
                    slowmode_delay=slowmode,
                    reason=f"Channel created by {interaction.user}"
                )
                
            elif type == "voice":
                channel = await interaction.guild.create_voice_channel(
                    name=name,
                    category=category,
                    user_limit=user_limit if user_limit > 0 else None,
                    bitrate=bitrate * 1000,
                    reason=f"Channel created by {interaction.user}"
                )
                
            elif type == "category":
                channel = await interaction.guild.create_category(
                    name=name,
                    reason=f"Category created by {interaction.user}"
                )
                
            elif type == "news":
                channel = await interaction.guild.create_text_channel(
                    name=name,
                    category=category,
                    topic=topic,
                    nsfw=nsfw,
                    news=True,
                    reason=f"News channel created by {interaction.user}"
                )
                
            elif type == "stage":
                channel = await interaction.guild.create_stage_channel(
                    name=name,
                    category=category,
                    topic=topic,
                    reason=f"Stage channel created by {interaction.user}"
                )
                
            else:
                await interaction.followup.send("Invalid channel type.")
                return
                
            embed = discord.Embed(
                title="Channel Created",
                description=f"Created new channel: {channel.mention}",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Name", value=channel.name, inline=True)
            embed.add_field(name="Type", value=str(channel.type).replace('_', ' ').title(), inline=True)
            
            if category:
                embed.add_field(name="Category", value=category.name, inline=True)
                
            if isinstance(channel, discord.TextChannel):
                if topic:
                    embed.add_field(name="Topic", value=topic[:1024], inline=False)
                if nsfw:
                    embed.add_field(name="NSFW", value="Yes", inline=True)
                if slowmode > 0:
                    embed.add_field(name="Slowmode", value=f"{slowmode} seconds", inline=True)
                    
            elif isinstance(channel, discord.VoiceChannel):
                if user_limit > 0:
                    embed.add_field(name="User Limit", value=str(user_limit), inline=True)
                embed.add_field(name="Bitrate", value=f"{bitrate} kbps", inline=True)
                
            embed.set_footer(text=f"Created by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @channel_group.command(name="delete", description="Delete a channel")
    @app_commands.describe(channel="The channel to delete")
    @app_commands.default_permissions(manage_channels=True)
    async def channel_delete(
        self,
        interaction: discord.Interaction,
        channel: discord.abc.GuildChannel
    ):
        """Delete a channel"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.manage_channels:
                await interaction.followup.send("I don't have permission to manage channels.")
                return
                
            channel_name = channel.name
            channel_type = str(channel.type).replace('_', ' ').title()
            
            await channel.delete(reason=f"Channel deleted by {interaction.user}")
            
            embed = discord.Embed(
                title="Channel Deleted",
                description=f"Deleted channel: **{channel_name}**",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Type", value=channel_type, inline=True)
            embed.set_footer(text=f"Deleted by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @channel_group.command(name="lock", description="Lock a channel for @everyone")
    @app_commands.describe(
        channel="The channel to lock (defaults to current channel)",
        reason="Reason for locking the channel"
    )
    @app_commands.default_permissions(manage_channels=True)
    async def channel_lock(
        self,
        interaction: discord.Interaction,
        channel: Optional[Union[discord.TextChannel, discord.VoiceChannel]] = None,
        reason: Optional[str] = "No reason provided"
    ):
        """Lock a channel, preventing @everyone from sending messages"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            channel = channel or interaction.channel
            
            if not interaction.guild.me.guild_permissions.manage_channels:
                await interaction.followup.send("I don't have permission to manage channels.")
                return
                
            everyone_role = interaction.guild.default_role
            
            await channel.set_permissions(
                everyone_role,
                send_messages=False,
                connect=False if isinstance(channel, discord.VoiceChannel) else None,
                reason=f"Channel locked by {interaction.user}: {reason}"
            )
            
            embed = discord.Embed(
                title="Channel Locked",
                description=f"{channel.mention} has been locked for @everyone.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            
            await interaction.followup.send(embed=embed)
            
            if channel.id != interaction.channel_id:
                try:
                    await channel.send(embed=embed)
                except:
                    pass
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @channel_group.command(name="unlock", description="Unlock a channel for @everyone")
    @app_commands.describe(
        channel="The channel to unlock (defaults to current channel)",
        reason="Reason for unlocking the channel"
    )
    @app_commands.default_permissions(manage_channels=True)
    async def channel_unlock(
        self,
        interaction: discord.Interaction,
        channel: Optional[Union[discord.TextChannel, discord.VoiceChannel]] = None,
        reason: Optional[str] = "No reason provided"
    ):
        """Unlock a channel, allowing @everyone to send messages again"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            channel = channel or interaction.channel
            
            if not interaction.guild.me.guild_permissions.manage_channels:
                await interaction.followup.send("I don't have permission to manage channels.")
                return
                
            everyone_role = interaction.guild.default_role
            
            await channel.set_permissions(
                everyone_role,
                send_messages=None,
                connect=None,
                reason=f"Channel unlocked by {interaction.user}: {reason}"
            )
            
            embed = discord.Embed(
                title="Channel Unlocked",
                description=f"{channel.mention} has been unlocked for @everyone.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            
            await interaction.followup.send(embed=embed)
            
            if channel.id != interaction.channel_id:
                try:
                    await channel.send(embed=embed)
                except:
                    pass
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @channel_group.command(name="slowmode", description="Set slowmode for a channel")
    @app_commands.describe(
        seconds="Slowmode delay in seconds (0 to disable)",
        channel="The channel to set slowmode for (defaults to current channel)"
    )
    @app_commands.default_permissions(manage_channels=True)
    async def channel_slowmode(
        self,
        interaction: discord.Interaction,
        seconds: int,
        channel: Optional[discord.TextChannel] = None
    ):
        """Set slowmode delay for a text channel"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            channel = channel or interaction.channel
            
            if not isinstance(channel, discord.TextChannel):
                await interaction.followup.send("Slowmode can only be set for text channels.")
                return
                
            if not interaction.guild.me.guild_permissions.manage_channels:
                await interaction.followup.send("I don't have permission to manage channels.")
                return
                
            seconds = max(0, min(21600, seconds))
            
            await channel.edit(slowmode_delay=seconds, reason=f"Slowmode set by {interaction.user}")
            
            if seconds == 0:
                embed = discord.Embed(
                    title="Slowmode Disabled",
                    description=f"Slowmode has been disabled in {channel.mention}.",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now()
                )
            else:
                if seconds < 60:
                    time_str = f"{seconds} second{'s' if seconds != 1 else ''}"
                elif seconds < 3600:
                    minutes = seconds // 60
                    time_str = f"{minutes} minute{'s' if minutes != 1 else ''}"
                else:
                    hours = seconds // 3600
                    minutes = (seconds % 3600) // 60
                    time_str = f"{hours} hour{'s' if hours != 1 else ''}"
                    if minutes > 0:
                        time_str += f" and {minutes} minute{'s' if minutes != 1 else ''}"
                
                embed = discord.Embed(
                    title="Slowmode Enabled",
                    description=f"Slowmode has been set to {time_str} in {channel.mention}.",
                    color=discord.Color.blue(),
                    timestamp=datetime.datetime.now()
                )
                
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            
            await interaction.followup.send(embed=embed)
            
            if channel.id != interaction.channel_id:
                try:
                    await channel.send(embed=embed)
                except:
                    pass
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @channel_group.command(name="clone", description="Clone a channel")
    @app_commands.describe(
        channel="The channel to clone",
        name="New name for the cloned channel (optional)"
    )
    @app_commands.default_permissions(manage_channels=True)
    async def channel_clone(
        self,
        interaction: discord.Interaction,
        channel: discord.abc.GuildChannel,
        name: Optional[str] = None
    ):
        """Clone a channel with all its permissions"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.manage_channels:
                await interaction.followup.send("I don't have permission to manage channels.")
                return
                
            cloned_channel = await channel.clone(
                name=name or channel.name,
                reason=f"Channel cloned by {interaction.user}"
            )
            
            embed = discord.Embed(
                title="Channel Cloned",
                description=f"Cloned {channel.mention} to {cloned_channel.mention}",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Name", value=cloned_channel.name, inline=True)
            embed.add_field(name="Type", value=str(cloned_channel.type).replace('_', ' ').title(), inline=True)
            
            if hasattr(cloned_channel, 'category') and cloned_channel.category:
                embed.add_field(name="Category", value=cloned_channel.category.name, inline=True)
                
            embed.set_footer(text=f"Cloned by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @channel_group.command(name="topic", description="Set a channel's topic")
    @app_commands.describe(
        channel="The channel to set the topic for (defaults to current channel)",
        topic="The new topic for the channel"
    )
    @app_commands.default_permissions(manage_channels=True)
    async def channel_topic(
        self,
        interaction: discord.Interaction,
        topic: str,
        channel: Optional[discord.TextChannel] = None
    ):
        """Set a new topic for a text channel"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            channel = channel or interaction.channel
            
            if not isinstance(channel, discord.TextChannel):
                await interaction.followup.send("Topics can only be set for text channels.")
                return
                
            if not interaction.guild.me.guild_permissions.manage_channels:
                await interaction.followup.send("I don't have permission to manage channels.")
                return
                
            old_topic = channel.topic or "No topic"
            
            await channel.edit(topic=topic, reason=f"Topic changed by {interaction.user}")
            
            embed = discord.Embed(
                title="Channel Topic Changed",
                description=f"Changed topic for {channel.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Old Topic", value=old_topic[:1024], inline=False)
            embed.add_field(name="New Topic", value=topic[:1024], inline=False)
            embed.set_footer(text=f"Changed by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

@app_commands.context_menu(name="Pin Message")
@app_commands.default_permissions(manage_messages=True)
async def pin_message_context(interaction: discord.Interaction, message: discord.Message):
    """Context menu command to pin a message"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
            await interaction.followup.send("I don't have permission to pin messages in this channel.", ephemeral=True)
            return
            
        if message.pinned:
            await interaction.followup.send("This message is already pinned.", ephemeral=True)
            return
            
        await message.pin(reason=f"Pinned by {interaction.user}")
        
        embed = discord.Embed(
            title="Message Pinned",
            description=f"Message has been pinned in {message.channel.mention}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Content", value=message.content[:1024] if message.content else "[No text content]", inline=False)
        embed.add_field(name="Author", value=message.author.mention, inline=True)
        embed.add_field(name="Jump to Message", value=f"[Click Here]({message.jump_url})", inline=True)
        
        embed.set_footer(text=f"Pinned by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}", ephemeral=True)

@app_commands.context_menu(name="Unpin Message")
@app_commands.default_permissions(manage_messages=True)
async def unpin_message_context(interaction: discord.Interaction, message: discord.Message):
    """Context menu command to unpin a message"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
            await interaction.followup.send("I don't have permission to unpin messages in this channel.", ephemeral=True)
            return
            
        if not message.pinned:
            await interaction.followup.send("This message is not pinned.", ephemeral=True)
            return
            
        await message.unpin(reason=f"Unpinned by {interaction.user}")
        
        embed = discord.Embed(
            title="Message Unpinned",
            description=f"Message has been unpinned in {message.channel.mention}",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Content", value=message.content[:1024] if message.content else "[No text content]", inline=False)
        embed.add_field(name="Author", value=message.author.mention, inline=True)
        embed.add_field(name="Jump to Message", value=f"[Click Here]({message.jump_url})", inline=True)
        
        embed.set_footer(text=f"Unpinned by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}", ephemeral=True)

async def register_context_menus(bot):
    """Register all channel context menu commands"""
    bot.tree.add_command(pin_message_context)
    bot.tree.add_command(unpin_message_context)
    
    print("Registered channel context menu commands")

async def setup(bot):
    """Add the cog to the bot and register context menu commands"""
    await bot.add_cog(ChannelCommands(bot))
    await register_context_menus(bot)
    print("Channel commands module loaded")