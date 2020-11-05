import discord
from discord.ext import commands
import re
from essentials import command_handler
from essentials.command_checks import (
    command_exists,
    check_sessions,
    invalidate,
    get_command,
)


class Maker(commands.Cog):
    """Command maker cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)
    async def text(self, ctx, name: str, *, content: str = None):
        """Make a command that replies with a text"""

        cmds = [command.name for command in self.bot.commands]

        for cmd in cmds:
            if name.startswith(cmd):
                return await ctx.send(
                    "Command name contains reserved word. Please use a different name."
                )

        if await command_exists(self.bot, name, ctx.guild):
            return await ctx.send(f"A command with name `{name}` already exists.")

        # Stop conflicting with other commands
        def check(message):
            if (
                message.author == ctx.author and message.channel == ctx.channel
            ) and message.content != "":
                if message.content.lower().startswith(f"{ctx.prefix}"):
                    return False
                else:
                    return True
            else:
                return False

        session_check = check_sessions(self.bot, ctx, name)
        if session_check[0]:
            return await ctx.send(session_check[1])

        if not content:
            text_step = await ctx.send(
                f"Neat, the command name will be `{name}`. \nNow write some content for this command. "
            )

            try:
                text_input = await self.bot.wait_for(
                    "message", timeout=180, check=check
                )
            except:
                invalidate(self.bot, ctx.guild, ctx.author, name)
                return await ctx.send(
                    "Command creation cancelled and session destroyed."
                )

            content = text_input.content

            if content.lower() == "stop":
                invalidate(self.bot, ctx.guild, ctx.author, name)
                return await ctx.send(
                    "Command creation cancelled and session destroyed."
                )
        else:
            content = content

        if ctx.author.guild_permissions.manage_guild:
            isapproved = "yes"
            note = ""
        else:
            isapproved = "no"
            note = "Wait for server managers to approve this command"

        try:
            await self.bot.db.execute(
                "INSERT INTO commands(userid, guild, name, type, approved) VALUES($1, $2, $3, 'text', $4)",
                ctx.author.id,
                ctx.guild.id,
                name,
                isapproved,
            )

            data = await get_command(self.bot, name, ctx.guild.id)

            id_ = data["id"]
            try:
                await self.bot.db.execute(
                    "INSERT INTO text(command_id, content) VALUES($1, $2)", id_, content
                )

                invalidate(self.bot, ctx.guild, ctx.author, name)
                await ctx.send(f"Command created `{name}`. {note}")

                runner = command_handler.Runner(self.bot)

                await runner.run_command(ctx, name=name, indm=False, bypass_check=False)
            except Exception as e:
                print(e)
                print("Here")
                await self.bot.db.execute("DELETE FROM commands WHERE id=$1", id_)
                invalidate(self.bot, ctx.guild, ctx.author, name)
                return await ctx.send(
                    "Error creating command. Please join the support server and report this error. <https://discord.gg/7SaE8v2>"
                )
        except:
            invalidate(self.bot, ctx.guild, ctx.author, name)
            await ctx.send(
                "Error creating command. Please join the support server and report this error. <https://discord.gg/7SaE8v2>"
            )


def setup(bot):
    bot.add_cog(Maker(bot))
