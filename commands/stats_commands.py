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
from instance import *
import datetime
import asyncio

class StatsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
        self.active_monitors = {}

    stats_group = app_commands.Group(name="stats", description="Statistics and monitoring commands")

    @stats_group.command(name="overview", description="Get an overview of all instances and their status")
    async def stats_overview(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            data = requests.get(ADDRESS + f"/api/overview?apikey={API_KEY}").json()
            
            if data["status"] == 200:
                daemons = data["data"]["remote"]
                
                embed = discord.Embed(
                    title="Instance Statistics",
                    description="Overview of all instances across all nodes",
                    color=discord.Color.blue()
                )
                
                total_instances = 0
                running_instances = 0
                stopped_instances = 0
                
                for daemon in daemons:
                    daemon_id = daemon["uuid"]
                    
                    instance_data = requests.get(
                        ADDRESS + f"/api/service/remote_service_instances?daemonId={daemon_id}{PAGE_SIZE_PAGE}&status=&instance_name=&apikey={API_KEY}",
                        headers=headers,
                    ).json()
                    
                    if instance_data["status"] == 200:
                        instances = instance_data["data"]["data"]
                        total_instances += len(instances)
                        
                        for instance in instances:
                            status = instance["status"]
                            if status == 3:
                                running_instances += 1
                            elif status == 0:
                                stopped_instances += 1
                
                embed.add_field(name="Total Instances", value=str(total_instances))
                embed.add_field(name="Running", value=f"🟢 {running_instances}")
                embed.add_field(name="Stopped", value=f"🔴 {stopped_instances}")
                
                embed.set_footer(text=f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to get overview data: {data.get('message', 'Unknown error')}")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @stats_group.command(name="instance", description="Get detailed statistics for a specific instance")
    async def stats_instance(self, interaction: discord.Interaction, instance_name: str):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            uuid, daemon_id = function_daemonNameIdTrans(instance_name)
            
            instance_data = function_instanceDetail(uuid, daemon_id)
            
            if instance_data["status"] == 200:
                embed = discord.Embed(
                    title=f"Instance Statistics: {instance_name}",
                    description=f"Detailed statistics for {instance_name}",
                    color=discord.Color.blue()
                )
                
                embed.add_field(name="Status", value=instance_data["instance_status"])
                embed.add_field(name="Auto Start", value=instance_data["autoStart"])
                embed.add_field(name="Auto Restart", value=instance_data["autoRestart"])
                
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

    @stats_group.command(name="node", description="Get statistics for a specific node")
    async def stats_node(self, interaction: discord.Interaction, node_name: str):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            daemon_id = function_nodeNameIdTrans(node_name)
            
            data = requests.get(
                ADDRESS + f"/api/service/remote_service?apikey={API_KEY}&uuid={daemon_id}",
                headers=headers,
            ).json()
            
            if data["status"] == 200:
                node_data = data["data"]
                
                embed = discord.Embed(
                    title=f"Node Statistics: {node_name}",
                    description=f"Detailed statistics for node {node_name}",
                    color=discord.Color.blue()
                )
                
                embed.add_field(name="Status", value="🟢 Online" if node_data["available"] else "🔴 Offline")
                embed.add_field(name="Address", value=f"{node_data['ip']}:{node_data['port']}")
                
                instance_data = requests.get(
                    ADDRESS + f"/api/service/remote_service_instances?daemonId={daemon_id}{PAGE_SIZE_PAGE}&status=&instance_name=&apikey={API_KEY}",
                    headers=headers,
                ).json()
                
                if instance_data["status"] == 200:
                    instances = instance_data["data"]["data"]
                    running_count = sum(1 for i in instances if i["status"] == 3)
                    
                    embed.add_field(
                        name="Instances", 
                        value=f"Total: {len(instances)}\nRunning: {running_count}\nStopped: {len(instances) - running_count}"
                    )
                
                if "system" in node_data:
                    system_info = node_data.get("system", {})
                    cpu_usage = system_info.get("cpuUsage", 0) * 100
                    mem_usage = system_info.get("memUsage", 0) * 100
                    total_mem = system_info.get("totalmem", 0)
                    free_mem = system_info.get("freemem", 0)
                    
                    total_mem_gb = total_mem / (1024 * 1024 * 1024)
                    free_mem_gb = free_mem / (1024 * 1024 * 1024)
                    
                    embed.add_field(
                        name="Resource Usage",
                        value=f"CPU: {cpu_usage:.2f}%\nMemory: {mem_usage:.2f}%\nFree Memory: {free_mem_gb:.2f} GB / {total_mem_gb:.2f} GB",
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
                await interaction.followup.send(f"Failed to get node details: {data.get('message', 'Unknown error')}")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @stats_group.command(name="monitor", description="Start or stop monitoring an instance")
    @app_commands.describe(
        action="Action to perform",
        instance_name="Name of the instance to monitor",
        interval="Update interval in seconds (default: 60)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Start", value="start"),
        app_commands.Choice(name="Stop", value="stop")
    ])
    async def stats_monitor(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        instance_name: str,
        interval: int = 60
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if action.value == "start":
                if instance_name in self.active_monitors:
                    await interaction.followup.send(f"Already monitoring {instance_name}. Stop it first before starting a new monitor.")
                    return
                
                monitor_message = await interaction.followup.send(f"Starting monitoring for {instance_name}...")
                
                async def monitor_task():
                    try:
                        while True:
                            uuid, daemon_id = function_daemonNameIdTrans(instance_name)
                            instance_data = function_instanceDetail(uuid, daemon_id)
                            
                            if instance_data["status"] == 200:
                                embed = discord.Embed(
                                    title=f"Instance Monitor: {instance_name}",
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
                                
                                embed.set_footer(text=f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                
                                await monitor_message.edit(content=None, embed=embed)
                            else:
                                await monitor_message.edit(content=f"Failed to get instance details: {instance_data.get('message', 'Unknown error')}")
                                break
                                
                            await asyncio.sleep(interval)
                    except Exception as e:
                        await monitor_message.edit(content=f"Monitoring stopped due to an error: {str(e)}")
                        if instance_name in self.active_monitors:
                            del self.active_monitors[instance_name]
                
                task = asyncio.create_task(monitor_task())
                self.active_monitors[instance_name] = {"task": task, "message": monitor_message}
                
            elif action.value == "stop":
                if instance_name not in self.active_monitors:
                    await interaction.followup.send(f"Not monitoring {instance_name}.")
                    return
                
                self.active_monitors[instance_name]["task"].cancel()
                
                await self.active_monitors[instance_name]["message"].edit(content=f"Monitoring stopped for {instance_name}.")
                
                del self.active_monitors[instance_name]
                
                await interaction.followup.send(f"Stopped monitoring {instance_name}.")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(StatsCommands(bot))