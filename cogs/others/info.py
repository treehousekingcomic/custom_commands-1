import discord
from discord.ext import commands
from discord.ext import menus
import re
from essentials.command_checks import command_exists


class MySource(menus.ListPageSource):
    def __init__(self, data, title: str):
        super().__init__(data, per_page=10)
        self.title = title

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        embed = discord.Embed(title=f"({self.title})", color=discord.Color.blurple())
        description = "\n".join(
            f"{i+1}. {v}" for i, v in enumerate(entries, start=offset)
        )

        embed.description = description
        return embed


class Info(commands.Cog):
    """Other command functions"""

    def __init__(self, bot):
        self.bot = bot

    async def get_aliases(self, command, guild):
        aliases = await self.bot.db.fetch(
            "SELECT aliases.name FROM commands INNER JOIN aliases ON aliases.cmd_id = commands.id WHERE commands.name=$1 and commands.guild=$2",
            command,
            guild.id,
        )
        aliases = [alias["name"] for alias in aliases]
        if len(aliases) > 0:
            return aliases
        else:
            return False

    @commands.command()
    async def list(self, ctx, flag: str = "approve  d"):
        if not flag.lower().startswith("un"):
            flag = "Approved"
            data = await self.bot.db.fetch(
                "SELECT * FROM commands WHERE guild =$1 and approved = $2",
                ctx.guild.id,
                "yes",
            )
        else:
            flag = "Unapproved"
            data = await self.bot.db.fetch(
                "SELECT * FROM commands WHERE guild =$1 and approved = $2",
                ctx.guild.id,
                "no",
            )

        cmds = []
        for row in data:
            aliases = await self.get_aliases(row["name"], ctx.guild)
            if aliases:
                cmds.append(row["name"] + f" `({len(aliases)} aliases)`")
            else:
                cmds.append(row["name"])

        if len(cmds) == 0:
            return await ctx.send(f"There are no {flag.lower()} commands.")
        flag += " - " + str(len(cmds))
        pages = menus.MenuPages(
            source=MySource(cmds, title=f"Commands {flag.lower()}"),
            clear_reactions_after=True,
        )
        await pages.start(ctx)

    @commands.command(name="raw")
    async def raw_(self, ctx, *, command: str):
        data = await command_exists(self.bot, command, ctx.guild)

        if not data:
            return await ctx.send(
                f"A custom command with name `{command}` doesn't exists."
            )

        cmd_type = data["type"]

        owner = ctx.guild.get_member(data["userid"])

        if cmd_type == "embed":
            data = await self.bot.db.fetchrow(
                "SELECT * FROM embed WHERE command_id=$1", data["id"]
            )
            title = data["title"]
            description = data["description"]
            thumbnail = data["thumbnail"]
            image = data["image"]

            embed = discord.Embed(title=f"Raw content of {command}")
            embed.add_field(name="Command type", value="Embed", inline=False)
            embed.add_field(
                name="Title",
                value=discord.utils.escape_markdown(title),
                inline=False,
            )
            embed.add_field(
                name="Description",
                value=discord.utils.escape_markdown(description),
                inline=False,
            )
            if thumbnail:
                pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                is_link = re.findall(pattern, thumbnail)
                if len(is_link) > 0:
                    embed.add_field(
                        name="Thumbnail", value=f"[Link]({is_link[0][0]})", inline=False
                    )
                else:
                    embed.add_field(
                        name="Thumbnail",
                        value=f"{thumbnail}",
                        inline=False,
                    )
            else:
                embed.add_field(name="Thumbnail", value=f"None", inline=False)

            if image:
                pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                is_link = re.findall(pattern, image)
                if len(is_link) > 0:
                    embed.add_field(
                        name="Image", value=f"[Link]({is_link[0][0]})", inline=False
                    )
                else:
                    embed.add_field(
                        name="Image",
                        value=f"{image}",
                        inline=False,
                    )
            else:
                embed.add_field(name="Image", value=f"None", inline=False)

            embed.add_field(name="Owner", value=owner.mention)

        if cmd_type == "text":
            data = await self.bot.db.fetchrow(
                "SELECT * FROM text WHERE command_id=$1", data["id"]
            )
            content = data["content"]

            embed = discord.Embed(title=f"Raw content of {command}")
            embed.add_field(name="Command type", value="Text", inline=False)
            embed.add_field(
                name="Content",
                value=discord.utils.escape_markdown(content),
                inline=False,
            )
            embed.add_field(name="Owner", value=owner.mention, inline=False)

        if cmd_type == "role":
            data = await self.bot.db.fetchrow(
                "SELECT * FROM role WHERE command_id=$1", data["id"]
            )
            role = ctx.guild.get_role(data["role"])
            content = role.name + f" ({role.id})"

            embed = discord.Embed(title=f"Raw content of {command}")
            embed.add_field(name="Command type", value="Role", inline=False)
            embed.add_field(name="Role", value=content, inline=False)
            embed.add_field(
                name="Action",
                value=data["action"].replace("take", "remove") + "role",
                inline=False,
            )

            embed.add_field(name="Owner", value=owner.mention, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx, name: str, owner=True):
        prefix = ctx.prefix
        # Check if command exists
        data = await command_exists(self.bot, name, ctx.guild)
        print(data)

        if not data:
            return await ctx.send(
                f"A custom command with name `{name}` doesn't exists."
            )

        # Blank embed
        embed = discord.Embed(color=discord.Color.blurple())

        # cmd_maker = ctx.guild.get_member(data["userid"])
        cmd_id = data["id"]
        cmd_type = data["type"]
        cmd_name = prefix + data["name"]
        cmd_help = data["help"]

        if data["approved"] == "yes":
            state = ""
        else:
            state = "(Unapproved)"

        embed.title = f"{cmd_name} {state}"

        # if owner:
        #     embed.add_field(name="Owner", value=cmd_maker.mention)

        aliases = await self.get_aliases(name, ctx.guild)
        if aliases and len(aliases) > 0:
            val = ", ".join(aliases)
            embed.add_field(name="Aliases", value=val)

        if cmd_help is None:
            if cmd_type == "embed":
                description = "Sends an embed"

            if cmd_type == "text":
                description = "Sends a text message"

            if cmd_type == "role":
                data = await self.bot.db.fetchrow(
                    "SELECT * FROM role WHERE command_id=$1", cmd_id
                )

                roles = data["role"]
                role_mentions = ""
                for role in roles:
                    r = ctx.guild.get_role(role)
                    if r:
                        role_mentions += r.mention + " "
                action = data["action"]

                if action == "give":
                    description = (
                        f"Gives " + role_mentions + " role to command executor"
                    )
                if action == "take":
                    description = (
                        f"Removes " + role_mentions + " role to command executor"
                    )
                if action == "toggle":
                    description = (
                        f"Gives or removes "
                        + role_mentions
                        + " role to command executor"
                    )
        else:
            description = cmd_help

        embed.description = description

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
