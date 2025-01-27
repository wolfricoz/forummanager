import logging
import re

import discord
from discord import app_commands
from discord.ext import commands
from requests import session

from classes.config import GuildConfig
from classes.forumtasks import ForumTasks
from classes.support.discord_tools import send_message, send_response
from classes.support.queue import queue


# the base for a cog.
class Forum(commands.GroupCog, name="forum") :
	def __init__(self, bot) :
		self.bot = bot

	# Your first app command!
	@app_commands.command(name='stats')
	@app_commands.checks.has_permissions(manage_channels=True)
	async def stats(self, interaction: discord.Interaction, forum: discord.ForumChannel) :
		"""Get stats for a forum"""
		await send_response(interaction, f"Getting stats for {forum.name}", ephemeral=True)
		embed = discord.Embed(title=f"Stats for {forum.name}")
		data = {
			"Threads"  : len(forum.threads),
			"archived" : len([thread for thread in forum.threads if thread.archived]),
			"tags"     : [tag.name for tag in forum.available_tags],
		}
		for key, value in data.items() :
			embed.add_field(name=key, value=value)
		await send_message(interaction.channel, embed=embed)

	@app_commands.command(name="recover", description="Recover archived posts")
	@app_commands.checks.has_permissions(manage_channels=True)
	async def recover(self, interaction: discord.Interaction, forum: discord.ForumChannel) :
		"""Recover archived posts"""
		await send_response(interaction, f"Recovering archived posts for {forum.name}, this may take some time.",
		                    ephemeral=True)
		archived_thread: discord.Thread
		channel: discord.ForumChannel
		regex = re.compile(f"search", flags=re.IGNORECASE)
		channels = [
			channel
			for channel in interaction.guild.channels
			if channel.type == discord.ChannelType.forum and regex.search(channel.name)
		]
		for channel in channels :
			logging.debug(f"[Forum Manager] Checking {channel.name}")
			forum = ForumTasks(channel, self.bot)
			queue().add(forum.start())

	@app_commands.command(name="copy", description="Copy a forum with all settings!")
	@app_commands.checks.has_permissions(manage_channels=True)
	async def copy(self, interaction: discord.Interaction, forum: discord.ForumChannel, name: str = None) :
		"""Copy a forum with all settings!"""
		await send_response(interaction, "Copying a forum with all settings!", ephemeral=True)
		f = await forum.clone(name=f"{name if name else forum.name}-Copy")
		[await f.create_tag(name=tag.name, moderated=tag.moderated, emoji=tag.emoji,
		                    reason="Forum copied through forum manager") for tag in forum.available_tags]
		queue().add(f.edit(default_thread_slowmode_delay=forum.default_thread_slowmode_delay,
		             default_auto_archive_duration=forum.default_auto_archive_duration,
		             default_layout=forum.default_layout,
		             default_sort_order=forum.default_sort_order,
		             default_reaction_emoji=forum.default_reaction_emoji), priority=2)
		await send_message(interaction.channel, f"Forum {forum.mention} copied to {f.mention}")

	@app_commands.command(name="cleanup_toggle", description="[config] Toggle the removal of threads from users that left")
	async def cleanup_toggle(self, interaction: discord.Interaction, active: bool) :
		"""Toggle the removal of threads from users that left"""
		config = GuildConfig(interaction.guild.id)
		config.set("cleanup", active)
		await send_response(interaction, f"Cleanup is now {active}", ephemeral=True)



async def setup(bot) :
	await bot.add_cog(Forum(bot))
