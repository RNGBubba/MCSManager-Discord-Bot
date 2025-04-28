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
import random
import asyncio
import datetime
import os
import json
import aiohttp
from typing import Optional, List

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MESSAGE = os.getenv("EPHEMERAL_MESSAGE", "False").lower() in ("true", "1")
        
    fun_group = app_commands.Group(name="fun", description="Fun and entertainment commands")
    
    @fun_group.command(name="8ball", description="Ask the magic 8-ball a question")
    @app_commands.describe(question="The question to ask the magic 8-ball")
    async def eightball(self, interaction: discord.Interaction, question: str):
        """Ask the magic 8-ball a question and get a random response"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes, definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]
        
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=random.choice(responses), inline=False)
        embed.set_footer(text=f"Asked by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)
    
    @fun_group.command(name="roll", description="Roll dice with custom notation (e.g., 2d6, 1d20)")
    @app_commands.describe(dice="Dice notation (e.g., 2d6, 1d20+5)")
    async def roll(self, interaction: discord.Interaction, dice: str = "1d20"):
        """Roll dice with custom notation"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            dice = dice.lower().replace(" ", "")
            
            modifier = 0
            if "+" in dice:
                dice, mod = dice.split("+")
                modifier = int(mod)
            elif "-" in dice:
                dice, mod = dice.split("-")
                modifier = -int(mod)
            
            if "d" not in dice:
                await interaction.followup.send("Invalid dice notation. Use format like '2d6' or '1d20+5'.")
                return
                
            num_dice, sides = dice.split("d")
            
            if not num_dice:
                num_dice = 1
            else:
                num_dice = int(num_dice)
                
            sides = int(sides)
            
            if num_dice <= 0 or sides <= 0 or num_dice > 100:
                await interaction.followup.send("Invalid dice parameters. Use 1-100 dice with positive sides.")
                return
                
            rolls = [random.randint(1, sides) for _ in range(num_dice)]
            total = sum(rolls) + modifier
            
            embed = discord.Embed(
                title="🎲 Dice Roll",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Notation", value=f"{num_dice}d{sides}{'+' + str(modifier) if modifier > 0 else '-' + str(abs(modifier)) if modifier < 0 else ''}", inline=False)
            
            if num_dice > 1:
                embed.add_field(name="Individual Rolls", value=", ".join(str(r) for r in rolls), inline=False)
                
            if modifier != 0:
                embed.add_field(name="Calculation", value=f"{sum(rolls)} {'+' + str(modifier) if modifier > 0 else '-' + str(abs(modifier))} = {total}", inline=False)
                
            embed.add_field(name="Result", value=str(total), inline=False)
            embed.set_footer(text=f"Rolled by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @fun_group.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        """Flip a coin and get heads or tails"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        result = random.choice(["Heads", "Tails"])
        
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"The coin landed on **{result}**!",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now()
        )
        
        embed.set_footer(text=f"Flipped by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)
    
    @fun_group.command(name="rps", description="Play Rock, Paper, Scissors against the bot")
    @app_commands.describe(choice="Your choice: rock, paper, or scissors")
    @app_commands.choices(choice=[
        app_commands.Choice(name="Rock", value="rock"),
        app_commands.Choice(name="Paper", value="paper"),
        app_commands.Choice(name="Scissors", value="scissors")
    ])
    async def rps(self, interaction: discord.Interaction, choice: str):
        """Play Rock, Paper, Scissors against the bot"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        choices = ["rock", "paper", "scissors"]
        bot_choice = random.choice(choices)

        if choice == bot_choice:
            result = "It's a tie!"
            color = discord.Color.yellow()
        elif (choice == "rock" and bot_choice == "scissors") or \
             (choice == "paper" and bot_choice == "rock") or \
             (choice == "scissors" and bot_choice == "paper"):
            result = "You win!"
            color = discord.Color.green()
        else:
            result = "I win!"
            color = discord.Color.red()
        
        emojis = {
            "rock": "🪨",
            "paper": "📄",
            "scissors": "✂️"
        }
        
        embed = discord.Embed(
            title="Rock, Paper, Scissors",
            description=result,
            color=color,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Your Choice", value=f"{emojis[choice]} {choice.capitalize()}", inline=True)
        embed.add_field(name="My Choice", value=f"{emojis[bot_choice]} {bot_choice.capitalize()}", inline=True)
        embed.set_footer(text=f"Played by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)
    
    @fun_group.command(name="poll", description="Create a poll with up to 10 options")
    @app_commands.describe(
        question="The poll question",
        option1="Option 1",
        option2="Option 2",
        option3="Option 3 (optional)",
        option4="Option 4 (optional)",
        option5="Option 5 (optional)",
        option6="Option 6 (optional)",
        option7="Option 7 (optional)",
        option8="Option 8 (optional)",
        option9="Option 9 (optional)",
        option10="Option 10 (optional)"
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        option1: str,
        option2: str,
        option3: Optional[str] = None,
        option4: Optional[str] = None,
        option5: Optional[str] = None,
        option6: Optional[str] = None,
        option7: Optional[str] = None,
        option8: Optional[str] = None,
        option9: Optional[str] = None,
        option10: Optional[str] = None
    ):
        """Create a poll with up to 10 options"""
        await interaction.response.defer(ephemeral=False)
        
        options = [opt for opt in [option1, option2, option3, option4, option5, 
                                  option6, option7, option8, option9, option10] if opt]
        
        emoji_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        embed = discord.Embed(
            title="📊 Poll",
            description=question,
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        for i, option in enumerate(options):
            embed.add_field(name=f"Option {i+1}", value=f"{emoji_numbers[i]} {option}", inline=False)
            
        embed.set_footer(text=f"Poll created by {interaction.user.display_name}")
        
        poll_message = await interaction.followup.send(embed=embed)
        
        for i in range(len(options)):
            await poll_message.add_reaction(emoji_numbers[i])
    
    @fun_group.command(name="joke", description="Get a random joke")
    async def joke(self, interaction: discord.Interaction):
        """Get a random joke from an API"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://official-joke-api.appspot.com/random_joke") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        embed = discord.Embed(
                            title="😄 Random Joke",
                            color=discord.Color.purple(),
                            timestamp=datetime.datetime.now()
                        )
                        
                        embed.add_field(name="Setup", value=data["setup"], inline=False)
                        embed.add_field(name="Punchline", value=data["punchline"], inline=False)
                        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
                        
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send("Sorry, I couldn't fetch a joke at the moment.")
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @fun_group.command(name="quote", description="Get an inspirational quote")
    async def quote(self, interaction: discord.Interaction):
        """Get a random inspirational quote"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.quotable.io/random") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        embed = discord.Embed(
                            title="💭 Inspirational Quote",
                            description=f"*\"{data['content']}\"*",
                            color=discord.Color.teal(),
                            timestamp=datetime.datetime.now()
                        )
                        
                        embed.set_footer(text=f"— {data['author']} | Requested by {interaction.user.display_name}")
                        
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send("Sorry, I couldn't fetch a quote at the moment.")
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

    @fun_group.command(name="choose", description="Let the bot choose between multiple options")
    @app_commands.describe(options="Options separated by commas (e.g., 'pizza, burger, salad')")
    async def choose(self, interaction: discord.Interaction, options: str):
        """Let the bot choose between multiple options"""
        await interaction.response.defer(ephemeral=self.MESSAGE)
        
        choices = [choice.strip() for choice in options.split(",") if choice.strip()]
        
        if len(choices) < 2:
            await interaction.followup.send("Please provide at least two options separated by commas.")
            return
            
        chosen = random.choice(choices)
        
        embed = discord.Embed(
            title="🤔 Choice Maker",
            description=f"I choose: **{chosen}**",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Options", value=", ".join(choices), inline=False)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    """Add the cog to the bot and register context menu commands"""
    await bot.add_cog(FunCommands(bot))
    print("Fun commands module loaded")