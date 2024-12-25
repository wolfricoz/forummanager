import logging
import re

import discord
from discord.ext import commands, tasks

from classes.forumtasks import ForumTasks
from classes.support.queue import queue


# the base for a cog.
class Tools(commands.Cog) :
	def __init__(self, bot: commands.Bot) :
		self.bot = bot
		self.forum_manager.start()

	def cog_unload(self) :
		self.forum_manager.cancel()

	# Your first app command!
	@tasks.loop(hours=6)
	async def forum_manager(self) -> None :
		"""Searches the forums in all guilds and starts the forum manager."""
		logging.info("starting the forum manager! The forum will be cleaned.")
		archived_thread: discord.Thread
		channel: discord.ForumChannel
		channels = [
			channel
			for guild in self.bot.guilds
			for channel in guild.channels
			if channel.type == discord.ChannelType.forum
		]
		logging.info(f"Found {len(channels)} forum channels.")
		for channel in channels :
			logging.debug(f"[Forum Manager] Checking {channel.name}")
			forum = ForumTasks(channel, self.bot)
			queue().add(forum.start())

	@forum_manager.before_loop
	async def before_forum_manager(self) :
		await self.bot.wait_until_ready()

async def setup(bot) :
	await bot.add_cog(Tools(bot))
