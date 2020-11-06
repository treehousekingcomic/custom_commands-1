import discord
from discord.ext import commands, menus


class MySource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=20)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        embed = discord.Embed(title=f"Variable List", color=discord.Color.blurple())
        description = "\n".join(
            f"{i+1}. {v}" for i, v in enumerate(entries, start=offset)
        )
        description = discord.utils.escape_mentions(description)
        embed.description = description
        # embed.set_thumbnail(url=ctx.guild.icon_url)
        return embed


class Variables(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def var_exists(self, name: str, guild: discord.Guild):
        data = await self.bot.db.fetchrow(
            "SELECT * FROM variables WHERE name=$1 and guild=$2", name, guild.id
        )
        if data:
            return True
        else:
            return False

    @commands.group()
    async def variable(self, ctx):
        pass

    @variable.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, name: str, *, value: str):
        if name.startswith("{") and name.endswith("}"):
            if await self.var_exists(name, ctx.guild):
                return await ctx.send(
                    f"A variable with the name `{name}` already exists. "
                    f"Please choose a different name or edit that with new content."
                )

            if name == value:
                return await ctx.send("Name and value can't be equal.")

            if name in value:
                return await ctx.send("Variable name cant be in variable value.")

            await self.bot.db.execute(
                "INSERT into variables(name, value, guild, userid) VALUES($1, $2, $3, $4)",
                name,
                value,
                ctx.guild.id,
                ctx.author.id,
            )
            await ctx.send(f"Variable `{name}` created successfully.")
        else:
            return await ctx.send(
                "Variable name must be wrapped with `{` `}`. Example : `{myvariable}`."
            )

    @variable.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, name: str):
        if not await self.var_exists(name, ctx.guild):
            return await ctx.send(f"A variabled with the name `{name}` doesn't esists.")

        await self.bot.db.execute(
            "DELETE FROM variables WHERE name=$1 and guild=$2", name, ctx.guild.id
        )
        await ctx.send(f"Variable `{name}` deleted successfully.")

    @variable.command(name="edit")
    @commands.has_permissions(administrator=True)
    async def edit_(self, ctx, name: str, *, value: str):
        if not await self.var_exists(name, ctx.guild):
            return await ctx.send(f"A variabled with the name `{name}` doesn't esists.")

        if name == value:
            return await ctx.send("Name and value can't be equal.")

        await self.bot.db.execute(
            "UPDATE variables SET value=$1, editorid=$2 WHERE name=$3 and guild=$4",
            value,
            ctx.author.id,
            name,
            ctx.guild.id,
        )
        await ctx.send(f"Variable `{name}` editted successfully.")

    @variable.command(name="view")
    @commands.has_permissions(administrator=True)
    async def view_(self, ctx, name: str):
        if not await self.var_exists(name, ctx.guild):
            return await ctx.send(f"A variabled with the name `{name}` doesn't esists.")

        data = await self.bot.db.fetchrow(
            "SELECT * FROM variables WHERE name=$1 and guild=$2", name, ctx.guild.id
        )
        value = data["value"]

        if data["editorid"]:
            editor = ctx.guild.get_member(data["editorid"])
            if editor:
                edited = f"Last editted by {str(editor)}"
            else:
                edited = f"Last editted by Unknown"
        else:
            edited = "Not edited"

        await ctx.send(
            f'Variable : {discord.utils.escape_mentions(data["name"])} \nValue : {discord.utils.escape_mentions(value)}\nActivity : {edited}'
        )

    @variable.command()
    async def list(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM variables WHERE guild=$1", ctx.guild.id
        )
        variables = [row["name"] for row in data]

        pages = menus.MenuPages(source=MySource(variables), clear_reactions_after=True)
        await pages.start(ctx)


def setup(bot):
    bot.add_cog(Variables(bot))
