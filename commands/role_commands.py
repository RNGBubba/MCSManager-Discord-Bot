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
from typing import Optional, List

class RoleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
        
    role_group = app_commands.Group(name="role", description="Role management commands")
    
    @role_group.command(name="add", description="Add a role to a user")
    @app_commands.describe(
        user="The user to add the role to",
        role="The role to add"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def role_add(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        role: discord.Role
    ):
        """Add a role to a user"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.manage_roles:
                await interaction.followup.send("I don't have permission to manage roles.")
                return
                
            if role.position >= interaction.guild.me.top_role.position:
                await interaction.followup.send("I cannot assign a role that is higher than or equal to my highest role.")
                return
                
            if role.position >= interaction.user.top_role.position and interaction.user.id != interaction.guild.owner_id:
                await interaction.followup.send("You cannot assign a role that is higher than or equal to your highest role.")
                return
                
            if role in user.roles:
                await interaction.followup.send(f"{user.mention} already has the {role.mention} role.")
                return
                
            await user.add_roles(role, reason=f"Role added by {interaction.user}")
            
            embed = discord.Embed(
                title="Role Added",
                description=f"Added {role.mention} to {user.mention}",
                color=role.color,
                timestamp=datetime.datetime.now()
            )
            
            embed.set_footer(text=f"Action by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @role_group.command(name="remove", description="Remove a role from a user")
    @app_commands.describe(
        user="The user to remove the role from",
        role="The role to remove"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def role_remove(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        role: discord.Role
    ):
        """Remove a role from a user"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.manage_roles:
                await interaction.followup.send("I don't have permission to manage roles.")
                return
                
            if role.position >= interaction.guild.me.top_role.position:
                await interaction.followup.send("I cannot remove a role that is higher than or equal to my highest role.")
                return
                
            if role.position >= interaction.user.top_role.position and interaction.user.id != interaction.guild.owner_id:
                await interaction.followup.send("You cannot remove a role that is higher than or equal to your highest role.")
                return
                
            if role not in user.roles:
                await interaction.followup.send(f"{user.mention} doesn't have the {role.mention} role.")
                return
                
            await user.remove_roles(role, reason=f"Role removed by {interaction.user}")
            
            embed = discord.Embed(
                title="Role Removed",
                description=f"Removed {role.mention} from {user.mention}",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            )
            
            embed.set_footer(text=f"Action by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @role_group.command(name="info", description="Get information about a role")
    @app_commands.describe(role="The role to get information about")
    async def role_info(self, interaction: discord.Interaction, role: discord.Role):
        """Get detailed information about a role"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            member_count = len(role.members)
            
            embed = discord.Embed(
                title=f"Role Information: {role.name}",
                color=role.color,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Role ID", value=role.id, inline=True)
            embed.add_field(name="Color", value=f"#{role.color.value:06x}" if role.color.value else "Default", inline=True)
            embed.add_field(name="Position", value=f"{role.position} of {len(interaction.guild.roles)}", inline=True)
            
            embed.add_field(name="Created On", value=f"<t:{int(role.created_at.timestamp())}:F>\n(<t:{int(role.created_at.timestamp())}:R>)", inline=True)
            
            embed.add_field(name="Members", value=member_count, inline=True)
            
            embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
            
            embed.add_field(name="Hoisted", value="Yes" if role.hoist else "No", inline=True)
            
            embed.add_field(name="Managed", value="Yes" if role.managed else "No", inline=True)
            
            is_default = role.is_default()
            embed.add_field(name="Default Role", value="Yes" if is_default else "No", inline=True)
            
            permissions = []
            
            if role.permissions.administrator:
                permissions.append("Administrator")
            else:
                if role.permissions.manage_guild:
                    permissions.append("Manage Server")
                if role.permissions.ban_members:
                    permissions.append("Ban Members")
                if role.permissions.kick_members:
                    permissions.append("Kick Members")
                if role.permissions.manage_channels:
                    permissions.append("Manage Channels")
                if role.permissions.manage_messages:
                    permissions.append("Manage Messages")
                if role.permissions.manage_roles:
                    permissions.append("Manage Roles")
                if role.permissions.mention_everyone:
                    permissions.append("Mention Everyone")
                if role.permissions.manage_webhooks:
                    permissions.append("Manage Webhooks")
                if role.permissions.manage_emojis:
                    permissions.append("Manage Emojis")
                if role.permissions.view_audit_log:
                    permissions.append("View Audit Log")
                if role.permissions.moderate_members:
                    permissions.append("Timeout Members")
            
            if permissions:
                embed.add_field(name="Key Permissions", value=", ".join(permissions), inline=False)
            else:
                embed.add_field(name="Key Permissions", value="None", inline=False)
                
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @role_group.command(name="list", description="List all roles in the server")
    async def role_list(self, interaction: discord.Interaction):
        """List all roles in the server"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            roles = sorted(interaction.guild.roles, key=lambda r: r.position, reverse=True)
            
            embed = discord.Embed(
                title=f"Roles in {interaction.guild.name}",
                description=f"Total: {len(roles)} roles",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            role_chunks = []
            current_chunk = ""
            
            for role in roles:
                role_text = f"{role.mention} ({len(role.members)} members)\n"
                
                if len(current_chunk) + len(role_text) > 1024:
                    role_chunks.append(current_chunk)
                    current_chunk = role_text
                else:
                    current_chunk += role_text
            
            if current_chunk:
                role_chunks.append(current_chunk)
            
            for i, chunk in enumerate(role_chunks, 1):
                embed.add_field(name=f"Roles (Part {i})", value=chunk, inline=False)
                
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @role_group.command(name="create", description="Create a new role")
    @app_commands.describe(
        name="The name of the new role",
        color="The color of the role (hex code like #FF0000)",
        mentionable="Whether the role can be mentioned by everyone",
        hoisted="Whether the role is displayed separately in the member list"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def role_create(
        self,
        interaction: discord.Interaction,
        name: str,
        color: Optional[str] = None,
        mentionable: Optional[bool] = False,
        hoisted: Optional[bool] = False
    ):
        """Create a new role"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.manage_roles:
                await interaction.followup.send("I don't have permission to manage roles.")
                return
            
            role_color = discord.Color.default()
            if color:
                if color.startswith('#'):
                    color = color[1:]
                try:
                    role_color = discord.Color.from_rgb(
                        int(color[0:2], 16),
                        int(color[2:4], 16),
                        int(color[4:6], 16)
                    )
                except:
                    await interaction.followup.send("Invalid color format. Using default color instead.")
            
            new_role = await interaction.guild.create_role(
                name=name,
                color=role_color,
                hoist=hoisted,
                mentionable=mentionable,
                reason=f"Role created by {interaction.user}"
            )
            
            embed = discord.Embed(
                title="Role Created",
                description=f"Created new role: {new_role.mention}",
                color=new_role.color,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Name", value=new_role.name, inline=True)
            embed.add_field(name="Color", value=f"#{new_role.color.value:06x}" if new_role.color.value else "Default", inline=True)
            embed.add_field(name="Mentionable", value="Yes" if mentionable else "No", inline=True)
            embed.add_field(name="Hoisted", value="Yes" if hoisted else "No", inline=True)
            
            embed.set_footer(text=f"Created by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @role_group.command(name="delete", description="Delete a role")
    @app_commands.describe(role="The role to delete")
    @app_commands.default_permissions(manage_roles=True)
    async def role_delete(self, interaction: discord.Interaction, role: discord.Role):
        """Delete a role"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.manage_roles:
                await interaction.followup.send("I don't have permission to manage roles.")
                return
                
            if role.position >= interaction.guild.me.top_role.position:
                await interaction.followup.send("I cannot delete a role that is higher than or equal to my highest role.")
                return
                
            if role.position >= interaction.user.top_role.position and interaction.user.id != interaction.guild.owner_id:
                await interaction.followup.send("You cannot delete a role that is higher than or equal to your highest role.")
                return
                
            if role.is_default():
                await interaction.followup.send("You cannot delete the @everyone role.")
                return
                
            role_name = role.name
            role_color = role.color
            member_count = len(role.members)
            
            await role.delete(reason=f"Role deleted by {interaction.user}")
            
            embed = discord.Embed(
                title="Role Deleted",
                description=f"Deleted role: **{role_name}**",
                color=role_color,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Members Affected", value=str(member_count), inline=True)
            embed.set_footer(text=f"Deleted by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @role_group.command(name="color", description="Change a role's color")
    @app_commands.describe(
        role="The role to change the color of",
        color="The new color (hex code like #FF0000)"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def role_color(self, interaction: discord.Interaction, role: discord.Role, color: str):
        """Change a role's color"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.manage_roles:
                await interaction.followup.send("I don't have permission to manage roles.")
                return
                
            if role.position >= interaction.guild.me.top_role.position:
                await interaction.followup.send("I cannot modify a role that is higher than or equal to my highest role.")
                return
                
            if role.position >= interaction.user.top_role.position and interaction.user.id != interaction.guild.owner_id:
                await interaction.followup.send("You cannot modify a role that is higher than or equal to your highest role.")
                return
                
            if color.startswith('#'):
                color = color[1:]
                
            try:
                role_color = discord.Color.from_rgb(
                    int(color[0:2], 16),
                    int(color[2:4], 16),
                    int(color[4:6], 16)
                )
            except:
                await interaction.followup.send("Invalid color format. Please use a hex color code like #FF0000.")
                return
                
            old_color = role.color
            
            await role.edit(color=role_color, reason=f"Color changed by {interaction.user}")
            
            embed = discord.Embed(
                title="Role Color Changed",
                description=f"Changed color of {role.mention}",
                color=role_color,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Old Color", value=f"#{old_color.value:06x}" if old_color.value else "Default", inline=True)
            embed.add_field(name="New Color", value=f"#{role_color.value:06x}", inline=True)
            
            embed.set_footer(text=f"Changed by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @role_group.command(name="members", description="List members with a specific role")
    @app_commands.describe(role="The role to list members for")
    async def role_members(self, interaction: discord.Interaction, role: discord.Role):
        """List all members with a specific role"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            members = role.members
            
            if not members:
                await interaction.followup.send(f"No members have the {role.mention} role.")
                return
                
            embed = discord.Embed(
                title=f"Members with {role.name}",
                description=f"Total: {len(members)} members",
                color=role.color,
                timestamp=datetime.datetime.now()
            )
            
            member_chunks = []
            current_chunk = ""
            
            members.sort(key=lambda m: m.display_name.lower())
            
            for member in members:
                member_text = f"{member.mention}\n"
                
                if len(current_chunk) + len(member_text) > 1024:
                    member_chunks.append(current_chunk)
                    current_chunk = member_text
                else:
                    current_chunk += member_text
            
            if current_chunk:
                member_chunks.append(current_chunk)
            
            for i, chunk in enumerate(member_chunks, 1):
                embed.add_field(name=f"Members (Part {i})", value=chunk, inline=False)
                
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @role_group.command(name="massadd", description="Add a role to multiple members")
    @app_commands.describe(
        role="The role to add",
        target_role="Add the role to all members with this role (optional)"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def role_massadd(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        target_role: Optional[discord.Role] = None
    ):
        """Add a role to multiple members"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not interaction.guild.me.guild_permissions.manage_roles:
                await interaction.followup.send("I don't have permission to manage roles.")
                return
                
            if role.position >= interaction.guild.me.top_role.position:
                await interaction.followup.send("I cannot assign a role that is higher than or equal to my highest role.")
                return
                
            if role.position >= interaction.user.top_role.position and interaction.user.id != interaction.guild.owner_id:
                await interaction.followup.send("You cannot assign a role that is higher than or equal to your highest role.")
                return
                
            if target_role:
                members = [m for m in target_role.members if role not in m.roles]
                action_description = f"Adding {role.mention} to all members with {target_role.mention}"
            else:
                members = [m for m in interaction.guild.members if role not in m.roles]
                action_description = f"Adding {role.mention} to all members"
                
            if not members:
                await interaction.followup.send("No members need this role added.")
                return
                
            progress_message = await interaction.followup.send(
                f"{action_description}\nProcessing 0/{len(members)} members..."
            )
            
            batch_size = 10
            success_count = 0
            
            for i in range(0, len(members), batch_size):
                batch = members[i:i+batch_size]
                
                await progress_message.edit(
                    content=f"{action_description}\nProcessing {i}/{len(members)} members..."
                )
                
                for member in batch:
                    try:
                        await member.add_roles(role, reason=f"Mass role add by {interaction.user}")
                        success_count += 1
                    except:
                        pass
                        
                await asyncio.sleep(1)
            
            embed = discord.Embed(
                title="Mass Role Add Complete",
                description=f"Added {role.mention} to {success_count} members",
                color=role.color,
                timestamp=datetime.datetime.now()
            )
            
            if target_role:
                embed.add_field(name="Target Role", value=target_role.mention, inline=True)
                
            embed.add_field(name="Success Rate", value=f"{success_count}/{len(members)} ({success_count/len(members)*100:.1f}%)", inline=True)
            embed.set_footer(text=f"Action by {interaction.user.display_name}")
            
            await progress_message.edit(content=None, embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

async def setup(bot):
    """Add the cog to the bot and register context menu commands"""
    await bot.add_cog(RoleCommands(bot))
    print("Role commands module loaded")