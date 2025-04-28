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
import json
import asyncio
from typing import Optional, List, Union

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
        self.config_file = "reaction_roles.json"
        self.config = self.load_config()
        
    def load_config(self):
        """Load reaction roles configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                default_config = {}
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            print(f"Error loading reaction roles config: {e}")
            return {}
            
    def save_config(self):
        """Save reaction roles configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving reaction roles config: {e}")
    
    reaction_group = app_commands.Group(name="reaction", description="Reaction role commands")
    
    @reaction_group.command(name="create", description="Create a reaction role message")
    @app_commands.describe(
        channel="The channel to send the reaction role message to",
        title="The title of the reaction role message",
        description="The description of the reaction role message"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def reaction_create(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        title: str,
        description: str
    ):
        """Create a new reaction role message"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not channel.permissions_for(interaction.guild.me).send_messages:
                await interaction.followup.send("I don't have permission to send messages in that channel.")
                return
                
            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            embed.set_footer(text=f"React to get roles | Created by {interaction.user.display_name}")
            
            message = await channel.send(embed=embed)
            
            guild_id = str(interaction.guild_id)
            message_id = str(message.id)
            
            if guild_id not in self.config:
                self.config[guild_id] = {}
                
            self.config[guild_id][message_id] = {
                "channel_id": channel.id,
                "roles": {}
            }
            
            self.save_config()
            
            confirm_embed = discord.Embed(
                title="Reaction Role Message Created",
                description=f"Reaction role message created in {channel.mention}. Use `/reaction add` to add roles to it.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            
            confirm_embed.add_field(name="Message ID", value=message.id, inline=True)
            confirm_embed.add_field(name="Jump to Message", value=f"[Click Here]({message.jump_url})", inline=True)
            
            await interaction.followup.send(embed=confirm_embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @reaction_group.command(name="add", description="Add a role to a reaction role message")
    @app_commands.describe(
        message_id="The ID of the reaction role message",
        role="The role to add",
        emoji="The emoji to use for this role",
        description="Description of what this role is for (optional)"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def reaction_add(
        self,
        interaction: discord.Interaction,
        message_id: str,
        role: discord.Role,
        emoji: str,
        description: Optional[str] = None
    ):
        """Add a role to an existing reaction role message"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            guild_id = str(interaction.guild_id)
            
            if guild_id not in self.config or message_id not in self.config[guild_id]:
                await interaction.followup.send("That message is not set up for reaction roles. Use `/reaction create` first.")
                return
                
            if not interaction.guild.me.guild_permissions.manage_roles:
                await interaction.followup.send("I don't have permission to manage roles.")
                return
                
            if role.position >= interaction.guild.me.top_role.position:
                await interaction.followup.send("I cannot assign a role that is higher than or equal to my highest role.")
                return
                
            channel_id = self.config[guild_id][message_id]["channel_id"]
            channel = interaction.guild.get_channel(channel_id)
            
            if not channel:
                await interaction.followup.send("The channel for this reaction role message no longer exists.")
                return
                
            try:
                message = await channel.fetch_message(int(message_id))
            except:
                await interaction.followup.send("I couldn't find that message. It may have been deleted.")
                return
                
            for existing_emoji in self.config[guild_id][message_id]["roles"]:
                if existing_emoji == emoji:
                    await interaction.followup.send("This emoji is already used on this message. Please use a different emoji.")
                    return
                    
            try:
                await message.add_reaction(emoji)
            except:
                await interaction.followup.send("I couldn't add that reaction. Make sure it's a valid emoji that I have access to.")
                return
                
            self.config[guild_id][message_id]["roles"][emoji] = {
                "role_id": role.id,
                "description": description
            }
            
            self.save_config()
            
            embed = message.embeds[0] if message.embeds else discord.Embed(
                title="Reaction Roles",
                description="React to get roles",
                color=discord.Color.blue()
            )
            
            roles_text = ""
            for e, role_data in self.config[guild_id][message_id]["roles"].items():
                r = interaction.guild.get_role(role_data["role_id"])
                if r:
                    roles_text += f"{e} - {r.mention}"
                    if role_data.get("description"):
                        roles_text += f" - {role_data['description']}"
                    roles_text += "\n"
                    
            roles_field_index = None
            for i, field in enumerate(embed.fields):
                if field.name == "Available Roles":
                    roles_field_index = i
                    break
                    
            if roles_field_index is not None:
                embed.set_field_at(roles_field_index, name="Available Roles", value=roles_text, inline=False)
            else:
                embed.add_field(name="Available Roles", value=roles_text, inline=False)
                
            await message.edit(embed=embed)
            
            confirm_embed = discord.Embed(
                title="Reaction Role Added",
                description=f"Added {role.mention} with emoji {emoji} to the reaction role message.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            
            if description:
                confirm_embed.add_field(name="Description", value=description, inline=False)
                
            confirm_embed.add_field(name="Jump to Message", value=f"[Click Here]({message.jump_url})", inline=True)
            
            await interaction.followup.send(embed=confirm_embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @reaction_group.command(name="remove", description="Remove a role from a reaction role message")
    @app_commands.describe(
        message_id="The ID of the reaction role message",
        emoji="The emoji of the role to remove"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def reaction_remove(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str
    ):
        """Remove a role from an existing reaction role message"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            guild_id = str(interaction.guild_id)
            
            if guild_id not in self.config or message_id not in self.config[guild_id]:
                await interaction.followup.send("That message is not set up for reaction roles.")
                return
                
            if emoji not in self.config[guild_id][message_id]["roles"]:
                await interaction.followup.send("That emoji is not set up for any role on this message.")
                return
                
            channel_id = self.config[guild_id][message_id]["channel_id"]
            channel = interaction.guild.get_channel(channel_id)
            
            if not channel:
                await interaction.followup.send("The channel for this reaction role message no longer exists.")
                return
                
            try:
                message = await channel.fetch_message(int(message_id))
            except:
                await interaction.followup.send("I couldn't find that message. It may have been deleted.")
                return
                
            role_id = self.config[guild_id][message_id]["roles"][emoji]["role_id"]
            role = interaction.guild.get_role(role_id)
            role_name = role.name if role else "Unknown Role"
                
            try:
                await message.clear_reaction(emoji)
            except:
                pass
                
            del self.config[guild_id][message_id]["roles"][emoji]
            self.save_config()
            
            embed = message.embeds[0] if message.embeds else discord.Embed(
                title="Reaction Roles",
                description="React to get roles",
                color=discord.Color.blue()
            )
            
            roles_text = ""
            for e, role_data in self.config[guild_id][message_id]["roles"].items():
                r = interaction.guild.get_role(role_data["role_id"])
                if r:
                    roles_text += f"{e} - {r.mention}"
                    if role_data.get("description"):
                        roles_text += f" - {role_data['description']}"
                    roles_text += "\n"
                    
            roles_field_index = None
            for i, field in enumerate(embed.fields):
                if field.name == "Available Roles":
                    roles_field_index = i
                    break
                    
            if roles_field_index is not None:
                if roles_text:
                    embed.set_field_at(roles_field_index, name="Available Roles", value=roles_text, inline=False)
                else:
                    embed.remove_field(roles_field_index)
                    
            await message.edit(embed=embed)
            
            confirm_embed = discord.Embed(
                title="Reaction Role Removed",
                description=f"Removed role {role_name} with emoji {emoji} from the reaction role message.",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            )
            
            confirm_embed.add_field(name="Jump to Message", value=f"[Click Here]({message.jump_url})", inline=True)
            
            await interaction.followup.send(embed=confirm_embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @reaction_group.command(name="list", description="List all reaction role messages")
    @app_commands.default_permissions(manage_roles=True)
    async def reaction_list(self, interaction: discord.Interaction):
        """List all reaction role messages in the server"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            guild_id = str(interaction.guild_id)
            
            if guild_id not in self.config or not self.config[guild_id]:
                await interaction.followup.send("There are no reaction role messages set up in this server.")
                return
                
            embed = discord.Embed(
                title="Reaction Role Messages",
                description=f"This server has {len(self.config[guild_id])} reaction role message(s).",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            for message_id, data in self.config[guild_id].items():
                channel = interaction.guild.get_channel(data["channel_id"])
                channel_name = channel.mention if channel else "Unknown Channel"
                
                roles_count = len(data["roles"])
                
                field_value = f"Channel: {channel_name}\nRoles: {roles_count}\n"
                
                if channel:
                    try:
                        message = await channel.fetch_message(int(message_id))
                        field_value += f"[Jump to Message]({message.jump_url})"
                    except:
                        field_value += "Message not found (may have been deleted)"
                
                embed.add_field(name=f"Message ID: {message_id}", value=field_value, inline=False)
                
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @reaction_group.command(name="delete", description="Delete a reaction role message")
    @app_commands.describe(message_id="The ID of the reaction role message to delete")
    @app_commands.default_permissions(manage_roles=True)
    async def reaction_delete(self, interaction: discord.Interaction, message_id: str):
        """Delete a reaction role message and its configuration"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            guild_id = str(interaction.guild_id)
            
            if guild_id not in self.config or message_id not in self.config[guild_id]:
                await interaction.followup.send("That message is not set up for reaction roles.")
                return
                
            channel_id = self.config[guild_id][message_id]["channel_id"]
            channel = interaction.guild.get_channel(channel_id)
            
            if channel:
                try:
                    message = await channel.fetch_message(int(message_id))
                    await message.delete()
                    message_deleted = True
                except:
                    message_deleted = False
            else:
                message_deleted = False
                
            del self.config[guild_id][message_id]
            
            if not self.config[guild_id]:
                del self.config[guild_id]
                
            self.save_config()
            
            embed = discord.Embed(
                title="Reaction Role Message Deleted",
                description=f"Reaction role configuration for message ID {message_id} has been deleted.",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            )
            
            if message_deleted:
                embed.add_field(name="Message Status", value="The message was also deleted from the channel.", inline=False)
            else:
                embed.add_field(name="Message Status", value="The original message could not be deleted (it may have already been deleted or the channel no longer exists).", inline=False)
                
            embed.set_footer(text=f"Deleted by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Event handler for when a reaction is added to a message"""
        if payload.user_id == self.bot.user.id:
            return
            
        try:
            guild_id = str(payload.guild_id)
            message_id = str(payload.message_id)
            
            if guild_id not in self.config or message_id not in self.config[guild_id]:
                return
                
            emoji = payload.emoji.name

            if emoji not in self.config[guild_id][message_id]["roles"]:
                return
                
            role_id = self.config[guild_id][message_id]["roles"][emoji]["role_id"]
            guild = self.bot.get_guild(payload.guild_id)
            
            if not guild:
                return
                
            role = guild.get_role(role_id)
            
            if not role:
                return
                
            member = guild.get_member(payload.user_id)
            
            if not member:
                return
                
            try:
                await member.add_roles(role, reason="Reaction role")
            except:
                pass
                
        except Exception as e:
            print(f"Error in reaction role add: {e}")
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Event handler for when a reaction is removed from a message"""
        if payload.user_id == self.bot.user.id:
            return
            
        try:
            guild_id = str(payload.guild_id)
            message_id = str(payload.message_id)
            
            if guild_id not in self.config or message_id not in self.config[guild_id]:
                return
                
            emoji = payload.emoji.name
            
            if emoji not in self.config[guild_id][message_id]["roles"]:
                return
                
            role_id = self.config[guild_id][message_id]["roles"][emoji]["role_id"]
            guild = self.bot.get_guild(payload.guild_id)
            
            if not guild:
                return
                
            role = guild.get_role(role_id)
            
            if not role:
                return
                
            member = guild.get_member(payload.user_id)
            
            if not member:
                return
                
            try:
                await member.remove_roles(role, reason="Reaction role removed")
            except:
                pass
                
        except Exception as e:
            print(f"Error in reaction role remove: {e}")

async def setup(bot):
    """Add the cog to the bot"""
    await bot.add_cog(ReactionRoles(bot))
    print("Reaction roles module loaded")