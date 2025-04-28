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
from user import *
import datetime

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")

    user_group = app_commands.Group(name="user", description="User management commands")

    @user_group.command(name="list", description="List all users on the panel")
    async def user_list(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            response = requests.get(
                ADDRESS + "/api/auth/search?apikey=" + API_KEY + "&userName=&role=&" + PAGE_SIZE_PAGE,
                headers=headers,
            ).json()
            
            if response["status"] == 200:
                users = response["data"]["data"]
                
                embed = discord.Embed(
                    title="User List",
                    description=f"Total users: {len(users)}",
                    color=discord.Color.blue()
                )
                
                admins = []
                regular_users = []
                banned_users = []
                
                for user in users:
                    permission = user.get("permission", 0)
                    username = user.get("userName", "Unknown")
                    
                    if permission == 10:
                        admins.append(username)
                    elif permission == 1:
                        regular_users.append(username)
                    elif permission == -1:
                        banned_users.append(username)
                
                if admins:
                    embed.add_field(
                        name="👑 Administrators",
                        value="\n".join(admins),
                        inline=False
                    )
                
                if regular_users:
                    embed.add_field(
                        name="👤 Regular Users",
                        value="\n".join(regular_users),
                        inline=False
                    )
                
                if banned_users:
                    embed.add_field(
                        name="🚫 Banned Users",
                        value="\n".join(banned_users),
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to get user list: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @user_group.command(name="info", description="Get detailed information about a user")
    async def user_info(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            user_data = function_searchUser(username)
            
            if "uuid" in user_data:
                register_time = datetime.datetime.fromtimestamp(user_data["registerTime"]/1000).strftime("%Y-%m-%d %H:%M:%S")
                login_time = datetime.datetime.fromtimestamp(user_data["loginTime"]/1000).strftime("%Y-%m-%d %H:%M:%S")
                
                embed = discord.Embed(
                    title=f"User Info: {username}",
                    description=f"UUID: {user_data['uuid']}",
                    color=discord.Color.blue()
                )
                
                embed.add_field(name="Permission Level", value=user_data["permission"])
                embed.add_field(name="2FA Enabled", value=user_data["2fa"])
                embed.add_field(name="Registered", value=register_time)
                embed.add_field(name="Last Login", value=login_time)
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"User not found: {username}")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @user_group.command(name="create", description="Create a new user")
    @app_commands.describe(
        username="Username for the new user",
        password="Password for the new user",
        permission="Permission level for the new user"
    )
    @app_commands.choices(permission=[
        app_commands.Choice(name="Administrator", value=10),
        app_commands.Choice(name="Regular User", value=1),
        app_commands.Choice(name="Banned", value=-1)
    ])
    async def create_user(
        self,
        interaction: discord.Interaction,
        username: str,
        password: str,
        permission: app_commands.Choice[int]
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            result = function_createUser(username, password, permission.value)
            
            if result["status"] == 200:
                function_fetchUserData()
                
                embed = discord.Embed(
                    title="User Created",
                    description=f"Successfully created user: {username}",
                    color=discord.Color.green()
                )
                
                embed.add_field(name="User UUID", value=result["user_uuid"])
                embed.add_field(name="Permission", value=function_permissionCheck(permission.value))
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to create user: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @user_group.command(name="delete", description="Delete a user")
    async def delete_user(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            user_uuid = function_userNameIdTrans(username)
            
            result = function_deleteUser(user_uuid)
            
            if result["status"] == 200:
                function_fetchUserData()
                
                embed = discord.Embed(
                    title="User Deleted",
                    description=f"Successfully deleted user: {username}",
                    color=discord.Color.green()
                )
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to delete user: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @user_group.command(name="update", description="Update a user's permission level")
    @app_commands.describe(
        username="Username to update",
        permission="New permission level"
    )
    @app_commands.choices(permission=[
        app_commands.Choice(name="Administrator", value=10),
        app_commands.Choice(name="Regular User", value=1),
        app_commands.Choice(name="Banned", value=-1)
    ])
    async def update_user(
        self,
        interaction: discord.Interaction,
        username: str,
        permission: app_commands.Choice[int]
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            user_uuid = function_userNameIdTrans(username)
           
            response = requests.get(
                ADDRESS + f"/api/auth/search?apikey={API_KEY}&userName={username}&role=&{PAGE_SIZE_PAGE}",
                headers=headers
            ).json()
            
            if response["status"] == 200 and response["data"]["data"]:
                user_data = response["data"]["data"][0]
                
                request_body = {
                    "uuid": user_uuid,
                    "config": {
                        "uuid": user_uuid,
                        "userName": username,
                        "loginTime": user_data.get("loginTime", ""),
                        "registerTime": user_data.get("registerTime", ""),
                        "instances": user_data.get("instances", []),
                        "permission": permission.value,
                        "apiKey": user_data.get("apiKey", ""),
                        "isInit": user_data.get("isInit", False),
                        "secret": user_data.get("secret", ""),
                        "open2FA": user_data.get("open2FA", False)
                    }
                }
                
                update_response = requests.put(
                    ADDRESS + f"/api/auth?apikey={API_KEY}",
                    headers=headers,
                    json=request_body
                ).json()
                
                status = function_statusCheck(update_response)
                
                if status is True:
                    function_fetchUserData()
                    
                    embed = discord.Embed(
                        title="User Updated",
                        description=f"Successfully updated user: {username}",
                        color=discord.Color.green()
                    )
                    
                    embed.add_field(
                        name="Permission",
                        value=f"Changed to: {function_permissionCheck(permission.value)}",
                        inline=False
                    )
                    
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f"Failed to update user: {status.get('message', 'Unknown error')}")
            else:
                await interaction.followup.send(f"Failed to get user data for {username}")
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @user_group.command(name="reset_password", description="Reset a user's password")
    @app_commands.describe(
        username="Username to reset password for",
        new_password="New password"
    )
    async def reset_password(
        self,
        interaction: discord.Interaction,
        username: str,
        new_password: str
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            user_uuid = function_userNameIdTrans(username)
            
            response = requests.get(
                ADDRESS + f"/api/auth/search?apikey={API_KEY}&userName={username}&role=&{PAGE_SIZE_PAGE}",
                headers=headers
            ).json()
            
            if response["status"] == 200 and response["data"]["data"]:
                user_data = response["data"]["data"][0]
                
                request_body = {
                    "uuid": user_uuid,
                    "config": {
                        "uuid": user_uuid,
                        "userName": username,
                        "passWord": new_password,
                        "loginTime": user_data.get("loginTime", ""),
                        "registerTime": user_data.get("registerTime", ""),
                        "instances": user_data.get("instances", []),
                        "permission": user_data.get("permission", 1),
                        "apiKey": user_data.get("apiKey", ""),
                        "isInit": user_data.get("isInit", False),
                        "secret": user_data.get("secret", ""),
                        "open2FA": user_data.get("open2FA", False)
                    }
                }
                
                update_response = requests.put(
                    ADDRESS + f"/api/auth?apikey={API_KEY}",
                    headers=headers,
                    json=request_body
                ).json()
                
                status = function_statusCheck(update_response)
                
                if status is True:
                    embed = discord.Embed(
                        title="Password Reset",
                        description=f"Successfully reset password for user: {username}",
                        color=discord.Color.green()
                    )
                    
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f"Failed to reset password: {status.get('message', 'Unknown error')}")
            else:
                await interaction.followup.send(f"Failed to get user data for {username}")
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
            
    @user_group.command(name="assign_instance", description="Assign an instance to a user")
    @app_commands.describe(
        username="Username to assign instance to",
        instance_name="Name of the instance to assign"
    )
    async def assign_instance(
        self,
        interaction: discord.Interaction,
        username: str,
        instance_name: str
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            user_uuid = function_userNameIdTrans(username)
            instance_uuid, daemon_id = function_daemonNameIdTrans(instance_name)
            
            response = requests.get(
                ADDRESS + f"/api/auth/search?apikey={API_KEY}&userName={username}&role=&{PAGE_SIZE_PAGE}",
                headers=headers
            ).json()
            
            if response["status"] == 200 and response["data"]["data"]:
                user_data = response["data"]["data"][0]
                
                instances = user_data.get("instances", [])
                
                for instance in instances:
                    if instance.get("instanceUuid") == instance_uuid and instance.get("daemonId") == daemon_id:
                        await interaction.followup.send(f"Instance '{instance_name}' is already assigned to user '{username}'")
                        return
                
                instances.append({
                    "instanceUuid": instance_uuid,
                    "daemonId": daemon_id
                })
                
                request_body = {
                    "uuid": user_uuid,
                    "config": {
                        "uuid": user_uuid,
                        "userName": username,
                        "loginTime": user_data.get("loginTime", ""),
                        "registerTime": user_data.get("registerTime", ""),
                        "instances": instances,
                        "permission": user_data.get("permission", 1),
                        "apiKey": user_data.get("apiKey", ""),
                        "isInit": user_data.get("isInit", False),
                        "secret": user_data.get("secret", ""),
                        "open2FA": user_data.get("open2FA", False)
                    }
                }
                
                update_response = requests.put(
                    ADDRESS + f"/api/auth?apikey={API_KEY}",
                    headers=headers,
                    json=request_body
                ).json()
                
                status = function_statusCheck(update_response)
                
                if status is True:
                    embed = discord.Embed(
                        title="Instance Assigned",
                        description=f"Successfully assigned instance '{instance_name}' to user '{username}'",
                        color=discord.Color.green()
                    )
                    
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f"Failed to assign instance: {status.get('message', 'Unknown error')}")
            else:
                await interaction.followup.send(f"Failed to get user data for {username}")
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(UserCommands(bot))