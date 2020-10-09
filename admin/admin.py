import random
from discord.ext import commands
import asyncio


class Admin(commands.Cog):
    """Bot owner commands"""

    def __init__(self, bot):
        self.bot = bot

    async def get_running_sessions(self):
        sessions_running = 0
        for session in self.bot.bot_sessions:
            sessions_running += len(self.bot.bot_sessions[session])

        return sessions_running

    @commands.command()
    @commands.is_owner()
    async def ping(self, ctx):
        latency = int(self.bot.latency * 1000)

        await ctx.send(f"{latency}ms")

    @commands.command()
    @commands.is_owner()
    async def logout(self, ctx):
        waiting = await ctx.send(
            f"Waiting to finish {await self.get_running_sessions()} running sessions."
        )
        await asyncio.sleep(1)

        while len(self.bot.bot_sessions) != 0:
            await waiting.edit(
                content=f"Waiting to finish {await self.get_running_sessions()} running sessions."
            )
            await asyncio.sleep(5)

        await self.bot.db.close()
        await waiting.edit(content="Closing db connection...")
        await asyncio.sleep(1)
        await waiting.edit(content=f"Logging out")
        await self.bot.logout()

    @commands.group(invoke_without_command=True, hidden=True)
    @commands.is_owner()
    async def disable(self, ctx):
        """Disable command cog or group"""
        await ctx.send(f"Do `{ctx.prefix}help disable` to get help on this command")

    @disable.command(hidden=True)
    @commands.is_owner()
    async def command(self, ctx, command: str):
        cmd = self.bot.get_command(command)
        if cmd is None:
            return await ctx.send("Not found!")

        if isinstance(cmd, commands.Group):
            for c in cmd.commands:
                try:
                    c.enabled = False
                except Exception as e:
                    return await ctx.send(e)
                finally:
                    cmd.enabled = False
            return await ctx.send(
                f"All the subcommands of `{cmd.qualified_name}` is disabled now"
            )

        if isinstance(cmd, commands.Command):
            try:
                cmd.enabled = False
            except Exception as e:
                return await ctx.send(e)
            await ctx.send(f"Command `{cmd.qualified_name}` is disabled now")

    @disable.command(hidden=True)
    @commands.is_owner()
    async def cog(self, ctx, cog: str = None):
        if cog is None:
            return await ctx.send("Please specify a cog")

        cogg = self.bot.cogs[cog]

        if cogg is None:
            return await ctx.send("Not found")

        for command in cogg.get_commands():
            if isinstance(command, commands.Group):
                for cmd in command.commands:
                    try:
                        cmd.enabled = False
                    except Exception as e:
                        await ctx.send(e)
                    finally:
                        command.enabled = False
            if isinstance(command, commands.Command):
                try:
                    command.enabled = False
                except Exception as e:
                    await ctx.send(e)

        await ctx.send(
            f"All the command and group of `{cogg.qualified_name}` is disabled now"
        )

    @commands.group(invoke_without_command=True, hidden=True)
    @commands.is_owner()
    async def enable(self, ctx):
        """Disable command cog or group"""
        await ctx.send(f"Do `{ctx.prefix}help enable` to get help on this command")

    @enable.command(hidden=True, name="command")
    @commands.is_owner()
    async def cmd(self, ctx, command: str = None):
        if command is None:
            return await ctx.send("Please specify a command to enable")

        cmd = self.bot.get_command(command)
        if cmd is None:
            return await ctx.send("Not found!")

        if isinstance(cmd, commands.Group):
            for c in cmd.commands:
                try:
                    c.enabled = True
                except Exception as e:
                    return await ctx.send(e)
                finally:
                    cmd.enabled = True
            return await ctx.send(
                f"All the subcommands of `{cmd.qualified_name}` is disabled now"
            )

        if isinstance(cmd, commands.Command):
            try:
                cmd.enabled = True
            except Exception as e:
                return await ctx.send(e)
            await ctx.send(f"Command `{cmd.qualified_name}` is disabled now")

    @enable.command(hidden=True, name="cog")
    @commands.is_owner()
    async def cogg(self, ctx, cog: str = None):
        if cog is None:
            return await ctx.send("Please specify a cog")

        cogg = self.bot.cogs[cog]

        if cogg is None:
            return await ctx.send("Not found")

        for command in cogg.get_commands():
            if isinstance(command, commands.Group):
                for cmd in command.commands:
                    try:
                        cmd.enabled = True
                    except Exception as e:
                        await ctx.send(e)
                    finally:
                        command.enabled = True
            if isinstance(command, commands.Command):
                try:
                    command.enabled = True
                except Exception as e:
                    await ctx.send(e)

        await ctx.send(
            f"All the command and group of `{cogg.qualified_name}` is enabled now"
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def selectwinner(self, ctx, message_id: int):
        message = await ctx.channel.fetch_message(message_id)
        if not message:
            return await ctx.send("Message not found.")

        reactions = message.reactions[0]
        participants = await reactions.users().flatten()

        if len(participants) < 3:
            return await ctx.send("Not qualified for giveaway.")

        winner = random.choice(participants)
        await ctx.send(f"The winner is {winner.mention}. ")


def setup(bot):
    bot.add_cog(Admin(bot))
