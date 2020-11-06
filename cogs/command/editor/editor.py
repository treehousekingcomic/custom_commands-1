import discord
from discord.ext import commands
import typing
from essentials.command_checks import (
    command_exists,
    only_command_exists,
    only_alias_exists,
    invalidate,
    get_command,
    check_sessions,
)


class Editor(commands.Cog):
    """Command editor"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def edit(self, ctx):
        await ctx.send(
            "Command type is missing. Use `**help edit` to see available commands."
        )

    @edit.command(name="command")
    async def command_(
        self,
        ctx,
        component: str,
        command: str,
        *,
        value: typing.Union[discord.Member, str],
    ):
        data = await only_command_exists(self.bot, command, ctx.guild)
        if not data:
            return await ctx.send(f"A command with name `{command}` doesnt exists.")

        if await only_alias_exists(self.bot, command, ctx.guild):
            return await ctx.send(
                f"`{value}` is an alias. Cant be edited. Please edit the actual command."
            )

        if not data["userid"] == ctx.author.id:
            return await ctx.send("You are not the owner of this command.")

        if component == "help":
            if value.lower() == "reset":
                await self.bot.db.execute(
                    "UPDATE commands SET help=$1 WHERE id=$2", None, data["id"]
                )
                return await ctx.send(f"Help reseted of command `{command}`.")

            await self.bot.db.execute(
                "UPDATE commands SET help=$1 WHERE id=$2", value, data["id"]
            )
            return await ctx.send(f"Help editted of command `{command}`.")

        if component.lower() == "name":
            # checks if someone in the same server is in the middle of making a command with that name or not
            session = check_sessions(self.bot, ctx, value)
            if session[0]:
                return await ctx.send(session[1])
            else:
                pass

            cmds = [command.name for command in self.bot.commands]

            for cmd in cmds:
                if value.startswith(cmd + " "):
                    return await ctx.send(
                        "Command name contains reserved word. Please use a different name."
                    )

            if await only_command_exists(self.bot, value, ctx.guild):
                invalidate(self.bot, ctx.guild, ctx.author, value)
                return await ctx.send(
                    f"A command with name `{value}` already exists. Please use different name."
                )

            if await only_alias_exists(self.bot, value, ctx.guild):
                invalidate(self.bot, ctx.guild, ctx.author, value)
                return await ctx.send(
                    f"An alias with name `{value}` exists. Please use a different name."
                )

            await self.bot.db.execute(
                "UPDATE commands SET name=$1 WHERE id=$2", value, data["id"]
            )

            # After command making finish invalidate the session so no already making error occur
            invalidate(self.bot, ctx.guild, ctx.author, value)
            return await ctx.send(
                f"Name editted of command from `{command}` to `{value}`."
            )

        if component == "owner":
            if not isinstance(value, discord.Member):
                return await ctx.send("Please mention a valid user.")

            await self.bot.db.execute(
                "UPDATE commands SET userid=$1 WHERE id=$2", value.id, data["id"]
            )
            return await ctx.send(
                f"Ownership transferred of command `{command}` to {value.mention}."
            )

    @edit.command(name="embed")
    async def embed_(self, ctx, command: str, component: str, *, value: str):

        data = await only_command_exists(self.bot, command, ctx.guild)
        if not data:
            return await ctx.send(f"A command with name `{command}` doesnt exists.")

        if data["type"] != "embed":
            return await ctx.send(f"`{command}` is  not an embed command.")

        if not data["userid"] == ctx.author.id:
            return await ctx.send("You are not the owner of this command.")

        if component.lower() == "title":
            await self.bot.db.execute(
                "UPDATE embed SET title=$1 WHERE command_id=$2", value, data["id"]
            )

        elif component.lower() == "thumbnail":
            await self.bot.db.execute(
                "UPDATE embed SET thumbnail=$1 WHERE command_id=$2", value, data["id"]
            )

        elif component.lower() == "image":
            await self.bot.db.execute(
                "UPDATE embed SET image=$1 WHERE command_id=$2", value, data["id"]
            )

        elif component.lower() == "description":
            await self.bot.db.execute(
                "UPDATE embed SET description=$1 WHERE command_id=$2", value, data["id"]
            )

        else:
            return await ctx.send(
                f"Unknown component `{component}`. Valid components are `title`, `description`, `thumbnail` and `image`"
            )

        if not ctx.author.guild_permissions.manage_guild:
            await self.bot.db.execute(
                "UPDATE commands SET approved=$1 WHERE id=$2", "no", data["id"]
            )
            await ctx.send(
                f"Command `{command}` editted successfully. As you are not server manager editing your command maked it unapproved. So wait for approval"
            )
        else:
            await ctx.send(f"Content editted of command `{command}`.")

    @edit.command(name="text")
    async def text_(self, ctx, command: str, *, content: str):
        note = ""
        data = await only_command_exists(self.bot, command, ctx.guild)
        if not data:
            return await ctx.send(f"A command with name `{command}` doesnt exists.")

        if data["type"] != "text":
            return await ctx.send(f"`{command}` is  not a text command.")

        if not data["userid"] == ctx.author.id:
            return await ctx.send("You are not the owner of this command.")

        if not ctx.author.guild_permissions.manage_guild:
            await self.bot.db.execute(
                "UPDATE commands SET approved=$1 WHERE id=$2", "no", data["id"]
            )

            note = f"As you are not server manager editing your command maked it unapproved. So wait for approval"

        await self.bot.db.execute(
            "UPDATE text SET content=$1 WHERE command_id=$2", content, data["id"]
        )
        return await ctx.send(f"Content editted of command `{command}`. {note}")

    @edit.command(name="role", aliases=["giverole", "removerole", "togglerole"])
    @commands.has_permissions(manage_roles=True)
    async def role_(self, ctx, command: str, roles: commands.Greedy[discord.Role]):
        data = await only_command_exists(self.bot, command, ctx.guild)
        if len(roles) < 1:
            return await ctx.send("Please mention some roles.")
        if not data:
            return await ctx.send(f"A command with name `{command}` doesnt exists.")

        if data["type"] != "role":
            return await ctx.send(f"`{command}` is  not a role command.")

        if not data["userid"] == ctx.author.id:
            return await ctx.send("You are not the owner of this command.")

        bot_ = ctx.guild.get_member(self.bot.user.id)

        valids = []
        reasons = []

        for role in roles:
            if not bot_.top_role < role:
                if not ctx.author.top_role < role:
                    if not role.managed:
                        valids.append(role.id)
                    else:
                        reasons.append(f"{role.name} is automatically managed.")
                else:
                    if ctx.author.guild_permissions.administrator:
                        valids.append(role.id)
                    else:
                        reasons.append(f"Your top role is lower than {role.name}.")
            else:
                reasons.append(f"Bots top role is lower than {role.name} role")

        if len(valids) < 1:
            reasons = "\n".join(reasons)
            return await ctx.send(
                f"Command editing failed failed. \nReasons ->\n`{reasons}`."
            )

        note = ""
        if len(reasons) > 0:
            note = (
                "`Some roles where declined reasons below. \n"
                + "\n".join(reasons)
                + "`"
            )

        await self.bot.db.execute(
            "UPDATE role SET role=$1 WHERE command_id=$2", valids, data["id"]
        )
        return await ctx.send(f"Role editted of command `{command}`. \n\n{note}")


def setup(bot):
    bot.add_cog(Editor(bot))
