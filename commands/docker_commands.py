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
import os
import datetime
import requests
import json

class DockerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")

    docker_group = app_commands.Group(name="docker", description="Docker management commands")

    @docker_group.command(name="images", description="List Docker images on a node")
    @app_commands.describe(
        node_name="Name of the node"
    )
    async def docker_images(
        self,
        interaction: discord.Interaction,
        node_name: str
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            daemon_id = function_nodeNameIdTrans(node_name)
            
            response = requests.get(
                f"{ADDRESS}/api/environment/image?daemonId={daemon_id}&apikey={API_KEY}",
                headers=headers
            ).json()
            
            status = function_statusCheck(response)
            
            if status is True:
                images = response["data"]
                
                embed = discord.Embed(
                    title=f"Docker Images: {node_name}",
                    description=f"Total images: {len(images)}",
                    color=discord.Color.blue()
                )
                
                image_groups = {}
                for image in images:
                    repo_tags = image.get("RepoTags", [])
                    if not repo_tags or repo_tags[0] == "<none>:<none>":
                        repo = "<none>"
                        tags = ["<none>"]
                    else:
                        for tag in repo_tags:
                            if ":" in tag:
                                repo, tag_version = tag.split(":", 1)
                                if repo not in image_groups:
                                    image_groups[repo] = []
                                image_groups[repo].append(tag_version)
                
                for repo, tags in image_groups.items():
                    tags_str = ", ".join(tags[:5])
                    if len(tags) > 5:
                        tags_str += f" and {len(tags) - 5} more"
                    
                    embed.add_field(
                        name=f"📦 {repo}",
                        value=f"Tags: {tags_str}",
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to get Docker images: {status.get('message', 'Unknown error')}")
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @docker_group.command(name="containers", description="List Docker containers on a node")
    @app_commands.describe(
        node_name="Name of the node"
    )
    async def docker_containers(
        self,
        interaction: discord.Interaction,
        node_name: str
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            daemon_id = function_nodeNameIdTrans(node_name)
            
            response = requests.get(
                f"{ADDRESS}/api/environment/containers?daemonId={daemon_id}&apikey={API_KEY}",
                headers=headers
            ).json()
            
            status = function_statusCheck(response)
            
            if status is True:
                containers = response["data"]
                
                embed = discord.Embed(
                    title=f"Docker Containers: {node_name}",
                    description=f"Total containers: {len(containers)}",
                    color=discord.Color.blue()
                )
                
                status_counts = {"running": 0, "exited": 0, "other": 0}
                for container in containers:
                    state = container.get("State", "").lower()
                    if state == "running":
                        status_counts["running"] += 1
                    elif state == "exited":
                        status_counts["exited"] += 1
                    else:
                        status_counts["other"] += 1
                
                embed.add_field(
                    name="Status Summary",
                    value=f"🟢 Running: {status_counts['running']}\n🔴 Exited: {status_counts['exited']}\n⚪ Other: {status_counts['other']}",
                    inline=False
                )
                
                for container in containers[:10]:
                    container_name = container.get("Names", ["Unknown"])[0].lstrip("/")
                    container_image = container.get("Image", "Unknown")
                    container_status = container.get("Status", "Unknown")
                    container_state = container.get("State", "Unknown")
                    
                    status_emoji = "🟢" if container_state.lower() == "running" else "🔴"
                    
                    embed.add_field(
                        name=f"{status_emoji} {container_name}",
                        value=f"Image: {container_image}\nStatus: {container_status}",
                        inline=True
                    )
                
                if len(containers) > 10:
                    embed.add_field(
                        name="Note",
                        value=f"Showing 10 of {len(containers)} containers",
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to get Docker containers: {status.get('message', 'Unknown error')}")
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @docker_group.command(name="networks", description="List Docker networks on a node")
    @app_commands.describe(
        node_name="Name of the node"
    )
    async def docker_networks(
        self,
        interaction: discord.Interaction,
        node_name: str
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            daemon_id = function_nodeNameIdTrans(node_name)
            
            response = requests.get(
                f"{ADDRESS}/api/environment/network?daemonId={daemon_id}&apikey={API_KEY}",
                headers=headers
            ).json()
            
            status = function_statusCheck(response)
            
            if status is True:
                networks = response["data"]
                
                embed = discord.Embed(
                    title=f"Docker Networks: {node_name}",
                    description=f"Total networks: {len(networks)}",
                    color=discord.Color.blue()
                )
                
                for network in networks:
                    network_name = network.get("Name", "Unknown")
                    network_driver = network.get("Driver", "Unknown")
                    network_scope = network.get("Scope", "Unknown")
                    
                    embed.add_field(
                        name=f"🌐 {network_name}",
                        value=f"Driver: {network_driver}\nScope: {network_scope}",
                        inline=True
                    )
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to get Docker networks: {status.get('message', 'Unknown error')}")
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @docker_group.command(name="build", description="Build a Docker image from a Dockerfile")
    @app_commands.describe(
        node_name="Name of the node",
        image_name="Name for the new image",
        tag="Tag for the new image (default: latest)",
        dockerfile="Dockerfile content"
    )
    async def docker_build(
        self,
        interaction: discord.Interaction,
        node_name: str,
        image_name: str,
        tag: str = "latest",
        dockerfile: str = None
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            daemon_id = function_nodeNameIdTrans(node_name)
            
            if not dockerfile:
                dockerfile = """FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    git \\
    nano \\
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
CMD ["/bin/bash"]
"""
            
            request_body = {
                "dockerFile": dockerfile,
                "name": image_name,
                "tag": tag
            }
            
            response = requests.post(
                f"{ADDRESS}/api/environment/image?daemonId={daemon_id}&apikey={API_KEY}",
                headers=headers,
                json=request_body
            ).json()
            
            status = function_statusCheck(response)
            
            if status is True:
                embed = discord.Embed(
                    title="Docker Image Build Started",
                    description=f"Building image: {image_name}:{tag}",
                    color=discord.Color.green()
                )
                
                embed.add_field(
                    name="Node",
                    value=node_name,
                    inline=False
                )
                
                embed.add_field(
                    name="Status",
                    value="Build process has been started. Use `/docker progress` to check the build status.",
                    inline=False
                )
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to start Docker build: {status.get('message', 'Unknown error')}")
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @docker_group.command(name="progress", description="Check Docker image build progress")
    @app_commands.describe(
        node_name="Name of the node"
    )
    async def docker_progress(
        self,
        interaction: discord.Interaction,
        node_name: str
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            daemon_id = function_nodeNameIdTrans(node_name)
            
            response = requests.get(
                f"{ADDRESS}/api/environment/progress?daemonId={daemon_id}&apikey={API_KEY}",
                headers=headers
            ).json()
            
            status = function_statusCheck(response)
            
            if status is True:
                progress_data = response["data"]
                
                embed = discord.Embed(
                    title=f"Docker Build Progress: {node_name}",
                    description="Current build status for Docker images",
                    color=discord.Color.blue()
                )
                
                if not progress_data:
                    embed.add_field(
                        name="Status",
                        value="No active builds found",
                        inline=False
                    )
                else:
                    for image_name, status_code in progress_data.items():
                        status_text = "Failed ❌" if status_code == -1 else "Building 🔄" if status_code == 1 else "Complete ✅" if status_code == 2 else "Unknown"
                        
                        embed.add_field(
                            name=f"Image: {image_name}",
                            value=f"Status: {status_text}",
                            inline=False
                        )
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to get build progress: {status.get('message', 'Unknown error')}")
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(DockerCommands(bot))