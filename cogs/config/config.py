from discord.ext import commands
from config import default_prefix


class Config(commands.Cog):
    """Server configuration"""

    def __init__(self, bot):
        self.bot = bot

    async def ensure_data(self, guild_id):
        data = await self.bot.db.fetchrow(
            "SELECT * FROM guild_data WHERE guild=$1", guild_id
        )
        if not data:
            await self.bot.db.execute(
                "INSERT INTO guild_data(guild, prefix) VALUES($1, $2)",
                guild_id,
                default_prefix,
            )

    async def get_data(self, guild_id):
        await self.ensure_data(guild_id)
        data = await self.bot.db.fetchrow(
            "SELECT * FROM guild_data WHERE guild=$1", guild_id
        )
        return data

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, new_prefix: str):
        await self.get_data(ctx.guild.id)
        self.bot.prefixes[ctx.guild.id] = new_prefix
        await self.bot.db.execute(
            "UPDATE guild_data SET prefix=$1 WHERE guild=$2", new_prefix, ctx.guild.id
        )
        await ctx.send(f"Prefix changed to `{new_prefix}`")

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def ccprefix(self, ctx, new_prefix: str):
        await self.get_data(ctx.guild.id)
        self.bot.cprefix[ctx.guild.id] = new_prefix
        await self.bot.db.execute(
            "UPDATE guild_data SET cprefix=$1 WHERE guild=$2", new_prefix, ctx.guild.id
        )
        await ctx.send(f"Custom commands prefix changed to `{new_prefix}`")

    @ccprefix.command()
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx):
        await self.get_data(ctx.guild.id)
        self.bot.cprefix[ctx.guild.id] = None
        await self.bot.db.execute(
            "UPDATE guild_data SET cprefix=$1 WHERE guild=$2", None, ctx.guild.id
        )
        await ctx.send(f"Custom commands prefix removed.")

    @commands.group(invoke_without_command=True)
    async def noprefix(self, ctx):
        await ctx.send(
            f"If you want commands to run without prefix you then turn on `noprefix` using `{ctx.prefix}noprefix toggle`. Alternatively doing this will also turn off `noprefix` if its on. `{ctx.prefix}noprefix status` Will show current settings of noprefix."
        )

    @noprefix.command()
    async def status(self, ctx):
        data = await self.bot.db.fetchrow(
            "SELECT * FROM guild_data WHERE guild=$1", ctx.guild.id
        )
        if data["noprefix"] == "yes":
            await ctx.send("Status : On")
        else:
            await ctx.send("Status : Off")

    @noprefix.command()
    @commands.has_permissions(administrator=True)
    async def toggle(self, ctx):
        data = await self.get_data(ctx.guild.id)

        if data["noprefix"] == "yes":
            self.bot.noprefix[ctx.guild.id] = "no"
            await self.bot.db.execute(
                "UPDATE guild_data SET noprefix=$1 WHERE guild=$2", "no", ctx.guild.id
            )
            await ctx.send(
                f"Custom commands will execute only with prefix before them."
            )
        else:
            self.bot.noprefix[ctx.guild.id] = "yes"
            await self.bot.db.execute(
                "UPDATE guild_data SET noprefix=$1 WHERE guild=$2", "yes", ctx.guild.id
            )
            await ctx.send(f"Custom commands will execute with or without prefix.")


def setup(bot):
    bot.add_cog(Config(bot))
