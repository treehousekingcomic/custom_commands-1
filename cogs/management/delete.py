import discord
from discord.ext import commands
from essentials.command_checks import (
    command_exists,
    check_sessions,
    invalidate,
    only_command_exists,
    only_alias_exists,
)


class Management(commands.Cog):
    """Other command functions"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def delete(self, ctx, *, name: str):
        data = await only_command_exists(self.bot, name, ctx.guild)
        alias = await only_alias_exists(self.bot, name, ctx.guild)

        if data:
            user = data["userid"]
            cmd_id = data["id"]

            if user == ctx.author.id or ctx.author.guild_permissions.administrator:
                await self.bot.db.execute("DELETE FROM commands WHERE id=$1", cmd_id)
                await ctx.send(
                    f"Command `{name}` and all corresponding aliases deleted."
                )
            else:
                await ctx.send("You can't delete this command!")

        elif alias:
            user = alias["user_id"]
            cmd_id = alias["id"]

            if user == ctx.author.id or ctx.author.guild_permissions.administrator:
                await self.bot.db.execute("DELETE FROM aliases WHERE id=$1", cmd_id)
                await ctx.send(f"Alias `{name}` deleted.")
            else:
                await ctx.send("You can't delete this alias!")

        else:
            await ctx.send("Command or alias not found")


def setup(bot):
    bot.add_cog(Management(bot))
