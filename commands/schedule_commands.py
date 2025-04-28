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
from shared import *
from utils import *
import datetime
import asyncio
import json
import os

class ScheduleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
        self.scheduled_tasks = {}
        self.schedule_file = "scheduled_tasks.json"
        self.load_schedules()
        self.start_scheduler()

    def cog_unload(self):
        for task_id, task_info in self.scheduled_tasks.items():
            if "task" in task_info and task_info["task"] is not None:
                task_info["task"].cancel()

    schedule_group = app_commands.Group(name="schedule", description="Scheduling and automation commands")

    def load_schedules(self):
        """Load scheduled tasks from file"""
        try:
            if os.path.exists(self.schedule_file):
                with open(self.schedule_file, "r") as f:
                    saved_tasks = json.load(f)
                    
                    for task_id, task_info in saved_tasks.items():
                        self.scheduled_tasks[task_id] = {
                            "type": task_info["type"],
                            "instance_name": task_info.get("instance_name"),
                            "command": task_info.get("command"),
                            "time": task_info.get("time"),
                            "days": task_info.get("days", []),
                            "task": None
                        }
        except Exception as e:
            print(f"Error loading schedules: {str(e)}")

    def save_schedules(self):
        """Save scheduled tasks to file"""
        try:
            tasks_to_save = {}
            for task_id, task_info in self.scheduled_tasks.items():
                tasks_to_save[task_id] = {k: v for k, v in task_info.items() if k != "task"}
                
            with open(self.schedule_file, "w") as f:
                json.dump(tasks_to_save, f, indent=2)
        except Exception as e:
            print(f"Error saving schedules: {str(e)}")

    def start_scheduler(self):
        """Start all scheduled tasks"""
        for task_id, task_info in self.scheduled_tasks.items():
            self.create_task(task_id, task_info)

    def create_task(self, task_id, task_info):
        """Create an asyncio task for a scheduled task"""
        if task_info["type"] == "daily":
            task = asyncio.create_task(self.run_daily_task(task_id, task_info))
            task_info["task"] = task
        elif task_info["type"] == "weekly":
            task = asyncio.create_task(self.run_weekly_task(task_id, task_info))
            task_info["task"] = task

    async def run_daily_task(self, task_id, task_info):
        """Run a daily scheduled task"""
        try:
            while True:
                now = datetime.datetime.now()
                scheduled_time = datetime.datetime.strptime(task_info["time"], "%H:%M").time()
                scheduled_datetime = datetime.datetime.combine(now.date(), scheduled_time)
                
                if scheduled_datetime < now:
                    scheduled_datetime = scheduled_datetime + datetime.timedelta(days=1)
                
                seconds_until_run = (scheduled_datetime - now).total_seconds()
                
                await asyncio.sleep(seconds_until_run)

                await self.execute_task(task_info)
                
                await asyncio.sleep(86400 - (datetime.datetime.now() - scheduled_datetime).total_seconds())
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in daily task {task_id}: {str(e)}")
            await asyncio.sleep(60)
            self.create_task(task_id, task_info)

    async def run_weekly_task(self, task_id, task_info):
        """Run a weekly scheduled task"""
        try:
            while True:
                now = datetime.datetime.now()
                scheduled_time = datetime.datetime.strptime(task_info["time"], "%H:%M").time()
                
                days_ahead = 0
                for i in range(7):
                    future_day = (now.weekday() + i) % 7
                    if future_day in task_info["days"]:
                        days_ahead = i
                        break
                
                scheduled_date = now.date() + datetime.timedelta(days=days_ahead)
                scheduled_datetime = datetime.datetime.combine(scheduled_date, scheduled_time)
                
                if scheduled_datetime < now and days_ahead == 0:
                    for i in range(1, 8):
                        future_day = (now.weekday() + i) % 7
                        if future_day in task_info["days"]:
                            days_ahead = i
                            break
                    
                    scheduled_date = now.date() + datetime.timedelta(days=days_ahead)
                    scheduled_datetime = datetime.datetime.combine(scheduled_date, scheduled_time)
                
                seconds_until_run = (scheduled_datetime - now).total_seconds()
                
                await asyncio.sleep(seconds_until_run)
                
                await self.execute_task(task_info)
                
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in weekly task {task_id}: {str(e)}")
            await asyncio.sleep(60)
            self.create_task(task_id, task_info)

    async def execute_task(self, task_info):
        """Execute a scheduled task"""
        try:
            instance_name = task_info["instance_name"]
            command = task_info["command"]
            
            uuid, daemon_id = function_daemonNameIdTrans(instance_name)
            
            function_sendCommand(uuid, daemon_id, command)
            
            print(f"Executed scheduled command '{command}' for instance '{instance_name}'")
        except Exception as e:
            print(f"Error executing scheduled task: {str(e)}")

    @schedule_group.command(name="daily", description="Schedule a daily command for an instance")
    @app_commands.describe(
        instance_name="Name of the instance",
        command="Command to execute",
        time="Time to run the command (format: HH:MM, 24-hour format)"
    )
    async def schedule_daily(
        self,
        interaction: discord.Interaction,
        instance_name: str,
        command: str,
        time: str
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            try:
                hour, minute = map(int, time.split(':'))
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    raise ValueError("Invalid time format")
            except:
                await interaction.followup.send("Invalid time format. Please use HH:MM (24-hour format).")
                return
            
            task_id = f"daily_{instance_name}_{time}_{len(self.scheduled_tasks)}"
            
            task_info = {
                "type": "daily",
                "instance_name": instance_name,
                "command": command,
                "time": time,
                "task": None
            }
            
            self.scheduled_tasks[task_id] = task_info
            
            self.create_task(task_id, task_info)
            
            self.save_schedules()
            
            embed = discord.Embed(
                title="Daily Schedule Created",
                description=f"Command scheduled for {instance_name}",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Command", value=f"`{command}`")
            embed.add_field(name="Time", value=time)
            embed.add_field(name="Task ID", value=task_id)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @schedule_group.command(name="weekly", description="Schedule a weekly command for an instance")
    @app_commands.describe(
        instance_name="Name of the instance",
        command="Command to execute",
        time="Time to run the command (format: HH:MM, 24-hour format)",
        days="Days of the week (comma-separated, 0=Monday, 6=Sunday)"
    )
    async def schedule_weekly(
        self,
        interaction: discord.Interaction,
        instance_name: str,
        command: str,
        time: str,
        days: str
    ):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            try:
                hour, minute = map(int, time.split(':'))
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    raise ValueError("Invalid time format")
            except:
                await interaction.followup.send("Invalid time format. Please use HH:MM (24-hour format).")
                return
            
            try:
                day_list = [int(day.strip()) for day in days.split(',')]
                for day in day_list:
                    if day < 0 or day > 6:
                        raise ValueError("Invalid day value")
            except:
                await interaction.followup.send("Invalid days format. Please use comma-separated values from 0-6 (0=Monday, 6=Sunday).")
                return
            
            task_id = f"weekly_{instance_name}_{time}_{len(self.scheduled_tasks)}"
            
            task_info = {
                "type": "weekly",
                "instance_name": instance_name,
                "command": command,
                "time": time,
                "days": day_list,
                "task": None
            }
            
            self.scheduled_tasks[task_id] = task_info
            
            self.create_task(task_id, task_info)
            
            self.save_schedules()
            
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            selected_days = [day_names[day] for day in day_list]
            
            embed = discord.Embed(
                title="Weekly Schedule Created",
                description=f"Command scheduled for {instance_name}",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Command", value=f"`{command}`")
            embed.add_field(name="Time", value=time)
            embed.add_field(name="Days", value=", ".join(selected_days))
            embed.add_field(name="Task ID", value=task_id)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @schedule_group.command(name="list", description="List all scheduled tasks")
    async def schedule_list(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if not self.scheduled_tasks:
                await interaction.followup.send("No scheduled tasks found.")
                return
            
            embed = discord.Embed(
                title="Scheduled Tasks",
                description=f"Total tasks: {len(self.scheduled_tasks)}",
                color=discord.Color.blue()
            )
            
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            for task_id, task_info in self.scheduled_tasks.items():
                task_type = task_info["type"].capitalize()
                instance_name = task_info["instance_name"]
                command = task_info["command"]
                time = task_info["time"]
                
                if task_type == "Daily":
                    schedule_text = f"Every day at {time}"
                elif task_type == "Weekly":
                    days = [day_names[day] for day in task_info["days"]]
                    schedule_text = f"Every {', '.join(days)} at {time}"
                else:
                    schedule_text = "Unknown schedule"
                
                embed.add_field(
                    name=f"{task_type}: {instance_name}",
                    value=f"ID: {task_id}\nCommand: `{command}`\nSchedule: {schedule_text}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @schedule_group.command(name="delete", description="Delete a scheduled task")
    @app_commands.describe(task_id="ID of the task to delete")
    async def schedule_delete(self, interaction: discord.Interaction, task_id: str):
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            if task_id not in self.scheduled_tasks:
                await interaction.followup.send(f"Task with ID '{task_id}' not found.")
                return
            
            task_info = self.scheduled_tasks[task_id]
            
            if "task" in task_info and task_info["task"] is not None:
                task_info["task"].cancel()
            
            del self.scheduled_tasks[task_id]
            
            self.save_schedules()
            
            embed = discord.Embed(
                title="Scheduled Task Deleted",
                description=f"Task ID: {task_id}",
                color=discord.Color.red()
            )
            
            embed.add_field(name="Instance", value=task_info["instance_name"])
            embed.add_field(name="Command", value=f"`{task_info['command']}`")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(ScheduleCommands(bot))