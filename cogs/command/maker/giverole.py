import discord
from discord.ext import commands
from essentials.command_checks import command_exists, check_sessions, invalidate, get_command


class Maker(commands.Cog):
    """Command maker cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.max_concurrency(1, commands.BucketType.user)
    async def giverole(self, ctx, name: str, roles: commands.Greedy[discord.Role]):
        cmds = [command.name for command in self.bot.commands]

        if len(roles) < 1:
            return await ctx.send("Roles are missing. Please see help for info.")

        for cmd in cmds:
            if name.startswith(cmd):
                return await ctx.send(
                    "Command name contains reserved word. Please use a different name."
                )

        if await command_exists(self.bot, name, ctx.guild):
            return await ctx.send(f"A command with name `{name}` already exists.")

        session_check = check_sessions(self.bot, ctx, name)
        if session_check[0]:
            return await ctx.send(session_check[1])

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
            invalidate(self.bot, ctx.guild, ctx.author, name)
            return await ctx.send(
                f'Command creation failed. Reasons -> `{", ".join(reasons)}`.'
            )

        await self.bot.db.execute(
            "INSERT INTO commands(userid, guild, name,type, approved) VALUES($1, $2, $3, 'role', 'yes')",
            ctx.author.id,
            ctx.guild.id,
            name,
        )

        data = await get_command(self.bot, name, ctx.guild.id)
        
        id_ = data["id"]
        await self.bot.db.execute(
            "INSERT INTO role(command_id, role, action) VALUES($1, $2, 'give')",
            id_,
            valids,
        )

        note = ""
        if len(reasons) > 0:
            note = "`Some roles where declined reasons below. \n" + "\n".join(reasons) + "`"

        invalidate(self.bot, ctx.guild, ctx.author, name)
        await ctx.send(f"Command created `{name}`\n\n{note}")


def setup(bot):
    bot.add_cog(Maker(bot))
