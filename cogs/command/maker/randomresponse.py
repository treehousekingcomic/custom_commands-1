from discord.ext import commands
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
    async def random(self, ctx, name: str):
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

        text_step = await ctx.send(
            f"Neat, the command name will be `{name}`. \nNow write 2 or more text responses spearated with `|`."
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

        options = [text.strip() for text in content.split("|")]
        if len(options) < 2:
            invalidate(self.bot, ctx.guild, ctx.author, name)
            return await ctx.send(
                "At least 2 option must provided. \nCommand creation cancelled and session destroyed."
                )

        if ctx.author.guild_permissions.manage_guild:
            isapproved = "yes"
            note = ""
        else:
            isapproved = "no"
            note = "Wait for server managers to approve this command"

        try:
            await self.bot.db.execute(
                "INSERT INTO commands(userid, guild, name, type, approved) VALUES($1, $2, $3, 'random', $4)",
                ctx.author.id,
                ctx.guild.id,
                name,
                isapproved,
            )

            data = await get_command(self.bot, name, ctx.guild.id)

            id_ = data["id"]
            try:
                await self.bot.db.execute(
                    "INSERT INTO randomtext(command_id, contents) VALUES($1, $2)", id_, options
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
                    "Error creating command. Please join the support server and report this error. "
                    "<https://discord.gg/7SaE8v2>"
                )
        except:
            invalidate(self.bot, ctx.guild, ctx.author, name)
            await ctx.send(
                "Error creating command. Please join the support server and report this error. "
                "<https://discord.gg/7SaE8v2>"
            )


def setup(bot):
    bot.add_cog(Maker(bot))
