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
from daemon import *
import datetime

class NodeCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")

    node_group = app_commands.Group(name="node", description="Node management commands")

    @node_group.command(name="list", description="List all nodes with their status")
    async def node_list(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            data = requests.get(ADDRESS + f"/api/overview?apikey={API_KEY}").json()
            
            if data["status"] == 200:
                daemons = data["data"]["remote"]
                
                embed = discord.Embed(
                    title="Node List",
                    description=f"Total nodes: {len(daemons)}",
                    color=discord.Color.blue()
                )
                
                for daemon in daemons:
                    status_emoji = "🟢" if daemon["available"] else "🔴"
                    
                    instance_count = 0
                    try:
                        instance_data = requests.get(
                            ADDRESS + f"/api/service/remote_service_instances?daemonId={daemon['uuid']}{PAGE_SIZE_PAGE}&status=&instance_name=&apikey={API_KEY}",
                            headers=headers,
                        ).json()
                        
                        if instance_data["status"] == 200:
                            instance_count = len(instance_data["data"]["data"])
                    except:
                        pass
                    
                    embed.add_field(
                        name=f"{status_emoji} {daemon['remarks']}",
                        value=f"IP: {daemon['ip']}:{daemon['port']}\nInstances: {instance_count}\nSystem: {daemon.get('system', 'Unknown')}",
                        inline=True
                    )
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to get node list: {data.get('message', 'Unknown error')}")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @node_group.command(name="detail", description="Get detailed information about a node")
    async def node_detail(self, interaction: discord.Interaction, node_name: str):
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
                    title=f"Node Details: {node_name}",
                    description=f"UUID: {daemon_id}",
                    color=discord.Color.blue()
                )
                
                embed.add_field(name="Status", value="🟢 Online" if node_data["available"] else "🔴 Offline")
                embed.add_field(name="Address", value=f"{node_data['ip']}:{node_data['port']}")
                
                if "system" in node_data:
                    embed.add_field(name="System", value=node_data["system"], inline=False)
                
                try:
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
                except:
                    embed.add_field(name="Instances", value="Unable to fetch instance data")
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to get node details: {data.get('message', 'Unknown error')}")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @node_group.command(name="update", description="Update node configuration")
    @app_commands.describe(
        node_name="Name of the node to update",
        ip="New IP address (optional)",
        port="New port (optional)",
        remarks="New remarks/name (optional)",
        daemon_apikey="New daemon API key (optional)"
    )
    async def update_node(
        self,
        interaction: discord.Interaction,
        node_name: str,
        ip: str = None,
        port: int = None,
        remarks: str = None,
        daemon_apikey: str = None
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            daemon_id = function_nodeNameIdTrans(node_name)
            
            data = requests.get(
                ADDRESS + f"/api/service/remote_service?apikey={API_KEY}&uuid={daemon_id}",
                headers=headers,
            ).json()
            
            if data["status"] == 200:
                node_data = data["data"]
                
                update_data = {
                    "uuid": daemon_id,
                    "ip": ip if ip is not None else node_data["ip"],
                    "port": port if port is not None else node_data["port"],
                    "remarks": remarks if remarks is not None else node_data["remarks"],
                    "apiKey": daemon_apikey if daemon_apikey is not None else node_data["apiKey"],
                    "available": node_data.get("available", False)
                }
                
                response = function_updateDaemon(
                    daemon_id,
                    update_data["ip"],
                    update_data["port"],
                    update_data["remarks"],
                    update_data["apiKey"]
                )
                
                if response["status"] == 200:
                    function_fetchDaemonData()
                    
                    embed = discord.Embed(
                        title="Node Updated",
                        description=f"Successfully updated node: {node_name}",
                        color=discord.Color.green()
                    )
                    
                    changes = []
                    if ip is not None:
                        changes.append(f"IP: {node_data['ip']} → {ip}")
                    if port is not None:
                        changes.append(f"Port: {node_data['port']} → {port}")
                    if remarks is not None:
                        changes.append(f"Name: {node_data['remarks']} → {remarks}")
                    if daemon_apikey is not None:
                        changes.append("API Key: [updated]")
                        
                    embed.add_field(name="Changes", value="\n".join(changes) if changes else "No changes made")
                    
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f"Failed to update node: {response.get('message', 'Unknown error')}")
            else:
                await interaction.followup.send(f"Failed to get node data: {data.get('message', 'Unknown error')}")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @node_group.command(name="status", description="Check the status and health of a node")
    async def node_status(self, interaction: discord.Interaction, node_name: str):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            daemon_id = function_nodeNameIdTrans(node_name)
            
            response = function_tryNode(daemon_id)
            
            overview_data = requests.get(
                ADDRESS + f"/api/overview?apikey={API_KEY}",
                headers=headers
            ).json()
            
            if overview_data["status"] == 200:
                node_data = None
                for daemon in overview_data["data"]["remote"]:
                    if daemon["uuid"] == daemon_id:
                        node_data = daemon
                        break
                
                if node_data:
                    embed = discord.Embed(
                        title=f"Node Status: {node_name}",
                        description="Node health check",
                        color=discord.Color.green() if node_data["available"] else discord.Color.red()
                    )
                    
                    embed.add_field(name="Status", value="🟢 Online" if node_data["available"] else "🔴 Offline")
                    embed.add_field(name="Address", value=f"{node_data['ip']}:{node_data['port']}")
                    embed.add_field(name="Version", value=node_data.get("version", "Unknown"))
                    
                    instance_info = node_data.get("instance", {})
                    embed.add_field(
                        name="Instances", 
                        value=f"Running: {instance_info.get('running', 0)}\nTotal: {instance_info.get('total', 0)}"
                    )
                    
                    system_info = node_data.get("system", {})
                    if system_info:
                        system_details = [
                            f"OS: {system_info.get('type', 'Unknown')} {system_info.get('release', '')}",
                            f"Hostname: {system_info.get('hostname', 'Unknown')}",
                            f"Platform: {system_info.get('platform', 'Unknown')}"
                        ]
                        
                        uptime_seconds = system_info.get("uptime", 0)
                        days, remainder = divmod(int(uptime_seconds), 86400)
                        hours, remainder = divmod(remainder, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
                        system_details.append(f"Uptime: {uptime_str}")
                        
                        embed.add_field(
                            name="System Information",
                            value="\n".join(system_details),
                            inline=False
                        )
                    
                    if system_info:
                        total_mem = system_info.get("totalmem", 0)
                        free_mem = system_info.get("freemem", 0)
                        used_mem = total_mem - free_mem
                        
                        total_mem_gb = total_mem / (1024 * 1024 * 1024)
                        used_mem_gb = used_mem / (1024 * 1024 * 1024)
                        
                        cpu_usage = system_info.get("cpuUsage", 0) * 100
                        
                        mem_usage = system_info.get("memUsage", 0) * 100
                        
                        resource_details = [
                            f"CPU Usage: {cpu_usage:.2f}%",
                            f"Memory: {used_mem_gb:.2f} GB / {total_mem_gb:.2f} GB ({mem_usage:.2f}%)"
                        ]
                        
                        if "loadavg" in system_info:
                            load_avg = system_info["loadavg"]
                            if isinstance(load_avg, list) and len(load_avg) >= 3:
                                resource_details.append(f"Load Average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
                        
                        embed.add_field(
                            name="Resource Usage",
                            value="\n".join(resource_details),
                            inline=False
                        )
                    
                    embed.set_footer(text=f"Last updated: {datetime.datetime.fromtimestamp(overview_data['time']/1000).strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f"Node {node_name} not found in overview data.")
            else:
                await interaction.followup.send(f"Failed to get overview data: {overview_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @node_group.command(name="monitor", description="Monitor all nodes' status")
    async def monitor_nodes(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            data = requests.get(ADDRESS + f"/api/overview?apikey={API_KEY}").json()
            
            if data["status"] == 200:
                daemons = data["data"]["remote"]
                
                embed = discord.Embed(
                    title="Node Monitor",
                    description=f"Status of all nodes ({len(daemons)} total)",
                    color=discord.Color.blue()
                )
                
                online_count = sum(1 for d in daemons if d["available"])
                embed.add_field(name="Summary", value=f"🟢 Online: {online_count}\n🔴 Offline: {len(daemons) - online_count}")
                
                for daemon in daemons:
                    status_emoji = "🟢" if daemon["available"] else "🔴"
                    embed.add_field(
                        name=f"{status_emoji} {daemon['remarks']}",
                        value=f"IP: {daemon['ip']}:{daemon['port']}",
                        inline=True
                    )
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to get node data: {data.get('message', 'Unknown error')}")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(NodeCommands(bot))