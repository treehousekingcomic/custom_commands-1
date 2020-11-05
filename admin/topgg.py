import dbl
from discord.ext import commands, tasks
import os

import asyncio


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = os.getenv("DBL")  # set this to your DBL token
        self.dblpy = dbl.DBLClient(
            self.bot,
            self.token,
            webhook_path="/dblwebhook",
            webhook_auth=os.getenv("WEBHOOK_AUTH"),
            webhook_port=5000,
        )
        self.bot.dblpy = self.dblpy
        self.bot.token = self.token

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            await self.dblpy.post_guild_count()
        except Exception as e:
            appinfo = await self.bot.application_info()
            owner = appinfo.owner

            await owner.send(
                "Failed to post server count\n{}: {}".format(type(e).__name__, e)
            )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            await self.dblpy.post_guild_count()
        except Exception as e:
            appinfo = await self.bot.application_info()
            owner = appinfo.owner

            await owner.send(
                "Failed to post server count\n{}: {}".format(type(e).__name__, e)
            )

    @commands.command()
    @commands.is_owner()
    async def pgc(self, ctx):
        try:
            await self.dblpy.post_guild_count()
            await ctx.send("Guild count updated successfully.")
        except Exception as e:
            await ctx.send(
                "Failed to post server count\n{}: {}".format(type(e).__name__, e)
            )

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        appinfo = await self.bot.application_info()
        owner = appinfo.owner

        await owner.send(data)


def setup(bot):
    bot.add_cog(TopGG(bot))
