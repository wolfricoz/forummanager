import logging
from collections.abc import AsyncIterator

import discord
from discord import Thread
from discord.ext import commands

from classes.support.queue import queue


class ForumTasks :

	def __init__(self, forum: discord.ForumChannel, bot: commands.Bot) :
		# setting up the data all the underlying functions need to reduce api calls.
		self.forum: discord.ForumChannel = forum
		self.threads: list[discord.Thread] = forum.threads
		self.archived: AsyncIterator[Thread] = forum.archived_threads(limit=None)
		self.members: list[int] = [member.id for member in forum.guild.members]
		self.bot = bot

	async def start(self) :
		"""This starts the checking of the forum and will walk through all the tasks."""
		await self.recover_archived_posts()
		for thread in self.threads :
			queue().add(self.cleanup_forum(thread), priority=0)

	async def recover_archived_posts(self) :
		"""Loop through archived posts and send a reminder there."""
		logging.info("recovering archived posts")
		async for archived_thread in self.archived :
			if archived_thread.owner.id not in self.members :
				queue().add(archived_thread.delete(), priority=0)
				continue
			if archived_thread.archived is False :
				continue
			queue().add(archived_thread.edit(archived=False), priority=0)

	async def cleanup_forum(self, thread: discord.Thread) :
		logging.info("Cleaning up the forum")
		if self.check_user(thread.owner) is None :
			logging.info(f"{thread.name}'s user left, cleaning up")
			queue().add(thread.delete())
			return

	def check_user(self, member: discord.Member) -> None | discord.Member :
		if member is None :
			return None
		if member.id not in self.members :
			return None
		return member
