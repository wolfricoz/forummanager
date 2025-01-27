# dependencies included in requrements.txt. To install do pip -r requirements.txt
# (or for a specific python version: python3.10 -m pip -r requirements.txt)
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

from classes.config import GuildConfig
from classes.support.discord_tools import send_message

# Creates database
# loads env and variables
load_dotenv('.env')
token = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX')
# declares the bots intent
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
activity = discord.Activity(type=discord.ActivityType.watching, name="the forums")
bot = commands.Bot(command_prefix=PREFIX, case_insensitive=False, intents=intents, activity=activity)
bot.DEV = os.getenv("DEV")
print(bot.DEV)
dev_channel = bot.get_channel(int(bot.DEV))


# start up event; bot.tree.sync is required for the slash commands.
@bot.event
async def on_ready() :
	await bot.tree.sync()
	guilds = [guild.name for guild in bot.guilds]
	for guild in bot.guilds :
		GuildConfig(guild.id)
	await dev_channel.send(f"Bot started in {len(guilds)} guilds: {guilds}")
	print("Commands synced, start up _done_")


@bot.event
async def on_guild_join(guild):
	GuildConfig(guild.id)
	await guild.system_channel.send("Hello! I am Forum Manager. I am here to help you with your forum channels. Please make sure to set up the channel permissions correctly and I will do the rest! The bot will automatically restore archived posts every 48 hours, if you want to trigger this manually, use the /forum recover command.")
	await send_message(dev_channel, f"Bot joined {guild.name}({guild.id}) owned by {guild.owner.name}({guild.owner.id})")

@bot.event
async def on_guild_remove(guild):
	await send_message(dev_channel, f"Bot removed from {guild.name}({guild.id}) owned by {guild.owner.name}({guild.owner.id})")

# Grabs all the modules from the modules folder and loads them.
@bot.event
async def setup_hook() :
	for filename in os.listdir("modules") :

		if filename.endswith('.py') :
			await bot.load_extension(f"modules.{filename[:-3]}")
			print({filename[:-3]})
		else :
			print(f'Unable to load {filename[:-3]}')


# reloads all the modules.
@bot.command(aliases=["cr", "reload"])
@commands.is_owner()
async def cogreload(ctx) :
	filesloaded = []
	for filename in os.listdir("modules") :
		if filename.endswith('.py') :
			await bot.reload_extension(f"modules.{filename[:-3]}")
			filesloaded.append(filename[:-3])
	fp = ', '.join(filesloaded)
	await ctx.send(f"Modules loaded: {fp}")
	await bot.tree.sync()


# runs the bot with the token
bot.run(token)
