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
import sys
from shared import *
from utils import *
from instance import *
import asyncio
import datetime

class InstanceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")

    instance_group = app_commands.Group(name="instance", description="Instance management commands")

    @instance_group.command(name="list", description="List all instances on a specific node or all nodes")
    @app_commands.describe(node_name="Optional: Specify a node name to filter instances")
    async def instance_list(self, interaction: discord.Interaction, node_name: str = None):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if node_name:
                daemon_id = function_nodeNameIdTrans(node_name)
                instances = []
                
                data = requests.get(
                    ADDRESS + f"/api/service/remote_service_instances?daemonId={daemon_id}{PAGE_SIZE_PAGE}&status=&instance_name=&apikey={API_KEY}",
                    headers=headers,
                ).json()
                
                if data["status"] == 200:
                    instances_data = data["data"]["data"]
                    
                    embed = discord.Embed(
                        title=f"Instances on {node_name}",
                        description=f"Total instances: {len(instances_data)}",
                        color=discord.Color.blue()
                    )
                    
                    for instance in instances_data:
                        status = function_instanceStatusCheck(instance["status"])
                        status_emoji = "🟢" if status == "Running" else "🔴" if status == "Stopped" else "🟠"
                        embed.add_field(
                            name=f"{status_emoji} {instance['config']['nickname']}",
                            value=f"Type: {instance['config']['type']}\nStatus: {status}",
                            inline=True
                        )
                    
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f"Failed to get instances: {data.get('message', 'Unknown error')}")
            
            else:
                embed = discord.Embed(
                    title="All Instances",
                    description="Instances across all nodes",
                    color=discord.Color.blue()
                )
                
                for node_name, daemon_id in daemonData.items():
                    data = requests.get(
                        ADDRESS + f"/api/service/remote_service_instances?daemonId={daemon_id}{PAGE_SIZE_PAGE}&status=&instance_name=&apikey={API_KEY}",
                        headers=headers,
                    ).json()
                    
                    if data["status"] == 200:
                        instances_data = data["data"]["data"]
                        
                        if not instances_data:
                            continue
                            
                        instances_list = []
                        for instance in instances_data:
                            status = function_instanceStatusCheck(instance["status"])
                            status_emoji = "🟢" if status == "Running" else "🔴" if status == "Stopped" else "🟠"
                            instances_list.append(f"{status_emoji} {instance['config']['nickname']}")
                        
                        if len(instances_list) > 10:
                            instance_text = "\n".join(instances_list[:10]) + f"\n... and {len(instances_list) - 10} more"
                        else:
                            instance_text = "\n".join(instances_list)
                            
                        embed.add_field(
                            name=f"Node: {node_name} ({len(instances_data)})",
                            value=instance_text or "No instances",
                            inline=False
                        )
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @instance_group.command(name="create", description="Create a new instance")
    @app_commands.describe(
        node_name="Node where the instance will be created",
        instance_name="Name for the new instance",
        instance_type="Type of instance to create",
        memory="Memory allocation in MB (default: 1024)",
        process_type="Process type (default: general)"
    )
    @app_commands.choices(instance_type=[
        app_commands.Choice(name="Minecraft Java", value="minecraft_java"),
        app_commands.Choice(name="Minecraft Bedrock", value="minecraft_bedrock"),
        app_commands.Choice(name="Bungeecord", value="bungeecord"),
        app_commands.Choice(name="Waterfall", value="waterfall"),
        app_commands.Choice(name="Velocity", value="velocity"),
        app_commands.Choice(name="Custom", value="custom")
    ])
    @app_commands.choices(process_type=[
        app_commands.Choice(name="General Process", value="general"),
        app_commands.Choice(name="Docker Container", value="docker")
    ])
    async def create_instance(
        self, 
        interaction: discord.Interaction, 
        node_name: str, 
        instance_name: str, 
        instance_type: app_commands.Choice[str],
        memory: int = 1024,
        process_type: app_commands.Choice[str] = None
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            daemon_id = function_nodeNameIdTrans(node_name)

            if process_type is None:
                process_type = app_commands.Choice(name="General Process", value="general")
            
            request_body = {
                "config": {
                    "nickname": instance_name,
                    "type": instance_type.value,
                    "startCommand": "",
                    "stopCommand": "stop",
                    "cwd": "./",
                    "ie": "utf-8",
                    "oe": "utf-8",
                    "createDatetime": int(datetime.datetime.now().timestamp() * 1000),
                    "lastDatetime": int(datetime.datetime.now().timestamp() * 1000),
                    "processType": process_type.value,
                    "terminalOption": {
                        "haveColor": True,
                        "pty": True
                    },
                    "eventTask": {
                        "autoStart": False,
                        "autoRestart": False,
                        "ignore": False
                    }
                }
            }
            
            if instance_type.value == "minecraft_java":
                request_body["config"]["startCommand"] = f"java -Xmx{memory}M -Xms{memory}M -jar server.jar nogui"
            elif instance_type.value == "minecraft_bedrock":
                request_body["config"]["startCommand"] = "bedrock_server.exe"
            elif instance_type.value in ["bungeecord", "waterfall", "velocity"]:
                request_body["config"]["startCommand"] = f"java -Xmx{memory}M -Xms{memory}M -jar server.jar"
            
            if process_type.value == "docker":
                request_body["config"]["docker"] = {
                    "containerName": "",
                    "image": "mcsm-ubuntu:22.04",
                    "memory": memory,
                    "ports": ["25565:25565/tcp"],
                    "extraVolumes": [],
                    "maxSpace": None,
                    "network": None,
                    "io": None,
                    "networkMode": "bridge",
                    "networkAliases": [],
                    "cpusetCpus": "",
                    "cpuUsage": 100,
                    "workingDir": "",
                    "env": []
                }
            
            response = requests.post(
                ADDRESS + "/api/instance?apikey=" + API_KEY + "&daemonId=" + daemon_id,
                headers=headers,
                json=request_body
            ).json()
            
            status = function_statusCheck(response)
            
            if status is True:
                function_fetchDaemonData()
                
                embed = discord.Embed(
                    title="Instance Created",
                    description=f"Successfully created instance: {instance_name}",
                    color=discord.Color.green()
                )
                embed.add_field(name="Instance UUID", value=response["data"]["instanceUuid"])
                embed.add_field(name="Node", value=node_name)
                embed.add_field(name="Type", value=instance_type.value)
                embed.add_field(name="Process Type", value=process_type.value)
                embed.add_field(name="Memory", value=f"{memory} MB")
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to create instance: {status.get('message', 'Unknown error')}")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @instance_group.command(name="monitor", description="Monitor an instance's resource usage")
    async def monitor_instance(self, interaction: discord.Interaction, instance_name: str):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            uuid, daemon_id = function_daemonNameIdTrans(instance_name)
            
            instance_data = function_instanceDetail(uuid, daemon_id)
            
            if instance_data["status"] == 200:
                embed = discord.Embed(
                    title=f"Resource Monitor: {instance_name}",
                    description=f"Status: {instance_data['instance_status']}",
                    color=discord.Color.green() if instance_data["instance_status"] == "Running" else discord.Color.red()
                )
                
                if "processInfo" in instance_data:
                    process_info = instance_data.get("processInfo", {})
                    cpu_usage = process_info.get("cpu", 0)
                    memory_usage = process_info.get("memory", 0)
                    
                    memory_mb = memory_usage / (1024 * 1024)
                    
                    embed.add_field(
                        name="Resource Usage",
                        value=f"CPU: {cpu_usage:.2f}%\nMemory: {memory_mb:.2f} MB",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="Resource Usage",
                        value="Resource information not available",
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to get instance details: {instance_data.get('message', 'Unknown error')}")
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(InstanceCommands(bot))