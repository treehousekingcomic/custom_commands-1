import discord
from discord.ext import commands
from essentials.command_checks import only_command_exists, only_alias_exists


class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def approve(self, ctx, *, command: str):
        data = await only_command_exists(self.bot, command, ctx.guild)
        if not data:
            alias = await only_alias_exists(self.bot, command, ctx.guild)
            if alias:
                return await ctx.send("Aliases can't be approved or unapproved.")

            return await ctx.send("Command not found. ")

        if data["approved"] == "yes":
            return await ctx.send("This command is already approved.")

        await self.bot.db.execute(
            "UPDATE commands SET approved=$1 WHERE id=$2", "yes", data["id"]
        )

        # Notifying command owner
        if data["userid"] != ctx.author.id:
            cmd_owner = ctx.guild.get_member(data["userid"])
            if cmd_owner:
                try:
                    await cmd_owner.send(
                        f"Your command `{data['name']}` has been approved in `[{ctx.guild.name}]`"
                    )
                except:
                    pass

        return await ctx.send(
            f"Command `{command}` has been approved. Now can be executed."
        )

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def unapprove(self, ctx, command: str, reason: str = None):
        data = await only_command_exists(self.bot, command, ctx.guild)
        if not data:
            alias = await only_alias_exists(self.bot, command, ctx.guild)
            if alias:
                return await ctx.send("Aliases can't be approved or unapproved.")

            return await ctx.send("Command not found. ")

        if data["approved"] == "no":
            return await ctx.send("This command is already unapproved.")

        await self.bot.db.execute(
            "UPDATE commands SET approved=$1 WHERE id=$2", "no", data["id"]
        )

        # Notifying command owner
        if data["userid"] != ctx.author.id:
            cmd_owner = ctx.guild.get_member(data["userid"])
            if cmd_owner:
                try:
                    await cmd_owner.send(
                        f"Your command `{data['name']}` has been unapproved in `[{ctx.guild.name}]`"
                    )
                except:
                    pass

        return await ctx.send(
            f"Command `{command}` has been approved. Now can be executed."
        )


def setup(bot):
    bot.add_cog(Management(bot))
