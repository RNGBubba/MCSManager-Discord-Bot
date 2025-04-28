import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from user import *
from utils import *
from daemon import *
from instance import *
from commands.loader import load_commands, register_commands_path

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
MESSAGE: bool = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

BOT_VERSION = '0.2.0'
BOT_BUILD_TYPE = 'BETA'

@client.event
async def on_ready():
    try:
        print("Bot is starting up...")
        print(f"Bot Version: {BOT_VERSION} ({BOT_BUILD_TYPE})")
        register_commands_path()
        
        print("Loading command modules...")
        await load_commands(client)
        
        print("Fetching daemon and user data...")
        function_fetchDaemonData()
        function_fetchUserData()
        print("Syncing commands with Discord...")
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        
        slash_commands = [cmd for cmd in synced if cmd.type == discord.AppCommandType.chat_input]
        user_commands = [cmd for cmd in synced if cmd.type == discord.AppCommandType.user]
        message_commands = [cmd for cmd in synced if cmd.type == discord.AppCommandType.message]
        
        print(f"- Slash Commands: {len(slash_commands)}")
        print(f"- User Context Menu Commands: {len(user_commands)}")
        print(f"- Message Context Menu Commands: {len(message_commands)}")
        
        print('Bot is ready for use!')
    except Exception as e:
        print(f"Error during startup: {e}")

client.run(DISCORD_TOKEN)
