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
from discord.ext import commands
import os
import importlib
import inspect
import sys


async def load_commands(bot):
    """Load all command modules from the commands directory"""
    print("Loading command modules...")
    
    commands_dir = os.path.dirname(os.path.abspath(__file__))
    
    command_files = [f[:-3] for f in os.listdir(commands_dir) 
                    if f.endswith('.py') and f != '__init__.py' and f != 'loader.py']
    
    for module_name in command_files:
        try:
            module = importlib.import_module(f"commands.{module_name}")
            
            if hasattr(module, 'setup') and inspect.iscoroutinefunction(module.setup):
                await module.setup(bot)
                print(f"Loaded command module: {module_name}")
            else:
                print(f"Skipped module {module_name} (no setup function)")
        except Exception as e:
            print(f"Error loading module {module_name}: {str(e)}")
    
    print(f"Loaded {len(command_files)} command modules")

def register_commands_path():
    """Add the commands directory to the Python path"""
    commands_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(commands_dir)
    
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)