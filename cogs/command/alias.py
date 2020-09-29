from discord.ext import commands
from essentials.command_checks import check_sessions, invalidate, only_command_exists, only_alias_exists


class Maker(commands.Cog):
    """Command maker cog"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.bot_sessions = {}
        self.bot.user_sessions = []
        self.bot.prev_commands = {}

    @commands.command(name="alias")
    async def alias_(self, ctx, command: str, alias: str):
        cmds = [command.name for command in self.bot.commands]

        for cmd in cmds:
            if alias.startswith(cmd):
                return await ctx.send(
                    "Alias name contains reserved word. Please use a different alias."
                )
        if data := await only_command_exists(self.bot, command, ctx.guild):
            pass
        else:
            return await ctx.send(f"A command with name `{command}` doesn't exists.")

        if await only_alias_exists(self.bot, alias, ctx.guild):
            return await ctx.send(
                f"A command/alias with name `{alias}` already exists ."
            )

        if await only_command_exists(self.bot, alias, ctx.guild):
            return await ctx.send(
                f"A command with name `{alias}` already exists ."
            )

        session_check = check_sessions(self.bot, ctx, alias)
        if session_check[0]:
            return await ctx.send(session_check[1])

        await self.bot.db.execute(
            "INSERT INTO aliases(name, cmd_id, user_id, guild) VALUES($1, $2, $3, $4)",
            alias,
            data["id"],
            ctx.author.id,
            ctx.guild.id
        )
        invalidate(self.bot, ctx.guild, ctx.author, alias)

        await ctx.send(f"Command `{command}` has been aliased to `{alias}`.")


def setup(bot):
    bot.add_cog(Maker(bot))
