import discord
from discord import app_commands
from discord.ext import commands, tasks


# the base for a cog.
class Tools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Your first app command!
    @tasks.loop(hours=24)
    async def forum_manager(self) -> None :
        """makes all posts active again"""
        print("starting the forum manager! The forum will be cleaned.")
        archived_thread: discord.Thread
        channel: discord.ForumChannel
        regex = re.compile(f"search", flags=re.IGNORECASE)
        channels = [
            channel
            for guild in self.bot.guilds
            for channel in guild.channels
            if channel.type == discord.ChannelType.forum and regex.search(channel.name)
        ]
        for channel in channels :
            logging.debug(f"[Forum Manager] Checking {channel.name}")
            forum = ForumTasks(channel, self.bot)
            queue().add(forum.start())




async def setup(bot):
    await bot.add_cog(Tools(bot))
