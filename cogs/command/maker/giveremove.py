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
    async def giveandremove(self, ctx, name: str):
        cmds = [command.name for command in self.bot.commands]

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

        gives = []
        removes = []

        def check(message):
            return len(message.role_mentions) > 0

        def can_add(role, bot):
            if bot.top_role < role:
                return [False, "Bot's top role is lower than " + role.mention + " role. Cant add."]
            if role.managed:
                return [False, role.mention + " role is a managed role. Cant add."]
            if ctx.author.top_role < role and ctx.author.guild_permissions(manage_roles=False):
                return [False, role.mention + " is higher than your top role"]
            else:
                return [True]

        await ctx.send("[ + ]Mention the roles you want to add.")
        note = ""
        try:
            msg : discord.Message = await self.bot.wait_for("message", timeout=60, check=check)
            for role in msg.role_mentions:
                x = can_add(role, ctx.guild.get_member(self.bot.user.id))
                if x[0]:
                    gives.append(role)
                else:
                    note += x[1] + "\n"
            if len(gives) < 1:
                invalidate(self.bot, ctx.guild, ctx.author, name)
                return await ctx.send("None of the mentioned role can be managed by bot or you. Command creation cancelled, try again.")
            else:
                added = ""
                for role in set(gives):
                    added += role.mention + " "

                added += " roles are added."

                await ctx.send(note + "\n" + added)
        except Exception as e:
            print(e)
            invalidate(self.bot, ctx.guild, ctx.author, name)
            return await ctx.send("Timeout")

        # ----------------------------------------------------------------------------
        await ctx.send("[ + ]Mention the roles you want to Remove.")
        note = ""
        try:
            msg: discord.Message = await self.bot.wait_for("message", timeout=60, check=check)
            for role in msg.role_mentions:
                x = can_add(role, ctx.guild.get_member(self.bot.user.id))
                if x[0]:
                    removes.append(role)
                else:
                    note += x[1] + "\n"
            if len(gives) < 1:
                invalidate(self.bot, ctx.guild, ctx.author, name)
                return await ctx.send("None of the mentioned role can be managed by bot or you. Command creation cancelled, try again.")
            else:
                added = ""
                for role in set(removes):
                    added += role.mention + " "

                added += " roles are added."

                await ctx.send(note + "\n" + added)
        except Exception as e:
            print(e)
            invalidate(self.bot, ctx.guild, ctx.author, name)
            return await ctx.send("Timeout")


        gives = [role.id for role in gives]
        removes = [role.id for role in removes]

        await self.bot.db.execute(
            "INSERT INTO commands(userid, guild, name, type, approved) VALUES($1, $2, $3, 'mrl', 'yes')",
            ctx.author.id,
            ctx.guild.id,
            name,
        )

        data = await get_command(self.bot, name, ctx.guild.id)

        id_ = data["id"]
        await self.bot.db.execute(
            "INSERT INTO multirole(command_id, gives, removes) VALUES ($1, $2, $3)",
            id_,
            gives,
            removes,
        )

        invalidate(self.bot, ctx.guild, ctx.author, name)
        await ctx.send(f"Command created `{name}`.")


def setup(bot):
    bot.add_cog(Maker(bot))
