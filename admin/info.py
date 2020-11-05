import discord
import sys
import humanize
import os
from discord.ext import commands, menus
import asyncpg
import psutil
import functools
import asyncio


class MySource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=20)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        print(self)
        embed = discord.Embed(title=f"Guilds", color=discord.Color.blurple())
        embed.description = "\n".join(
            f"{i+1}. {v}" for i, v in enumerate(entries, start=offset)
        )
        # embed.set_thumbnail(url=ctx.guild.icon_url)
        return embed


class Info(commands.Cog):
    """Get bot info"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="guilds")
    @commands.is_owner()
    async def guilds_(self, ctx):
        guilds = []
        for guild in self.bot.guilds:
            rows = await self.bot.db.fetch(
                "SELECT * FROM commands WHERE guild=$1", guild.id
            )
            data = f"{guild.name} `({len(rows)})`"
            guilds.append(data)

        pages = menus.MenuPages(source=MySource(guilds), clear_reactions_after=True)
        await pages.start(ctx)

    @commands.group()
    async def about(self, ctx):
        """Get bot info"""

        pyv = (
            str(sys.version_info[0])
            + "."
            + str(sys.version_info[1])
            + "."
            + str(sys.version_info[2])
        )
        lib = "discord.py"
        dpv = str(discord.__version__)
        owner = "Shahriyar#9770"
        cmds = len(self.bot.commands)
        shards = len(self.bot.shards)
        ccmds = await self.bot.db.fetch(
            "SELECT * FROM commands WHERE type<>$1", "alias"
        )

        dirs = [
            os.getcwd() + "/cogs",
            os.getcwd() + "/admin",
            os.getcwd() + "/essentials",
        ]

        af = []
        for dir in dirs:
            for root, dirs, files in os.walk(dir):
                for file in files:
                    if file.endswith(".py"):
                        af.append(os.path.join(root, file))

        line = 0
        for file in af:
            with open(file, "r") as f:
                lines = f.readlines()
                line += len(lines)

        with open("bot.py", "r") as f:
            lines = f.readlines()
            line += len(lines)

        des = ""
        des += "**Owner** : " + owner + "\n"
        des += "**Lib** : " + lib + ", v" + dpv + "\n"
        des += "**Shards** : " + str(shards) + "\n"
        des += "**Python** : " + pyv + "\n"
        # des += "**Total commands** : " + str(cmds) + "\n"
        des += (
            "**Active since** : "
            + str(humanize.naturaldate(self.bot.user.created_at))
            + "\n"
        )
        des += "**Guilds** : " + str(len(self.bot.guilds)) + "\n"
        des += "**Commands Made** : " + str(len(ccmds)) + "\n"
        des += "**Users** : " + str(len(self.bot.users)) + "\n"
        des += "**Started** : " + humanize.naturaltime(self.bot.launch_time)

        des += f"\n\n__**Since last reboot**__ \n"
        des += f"**Command ran** : {self.bot.command_ran} times\n"
        des += f"**Custom command ran** : {self.bot.custom_command_ran} times\n"
        des += f"\n\n*This bot has `{len(af)+1}` files containing `{line}` lines of code and `{str(cmds)}` commands!* \n\n"

        des += f"[Join Support Server](https://discord.gg/7SaE8v2)"
        # des += "[![Discord Bots](https://top.gg/api/widget/696975708907503636.svg)](https://top.gg/bot/696975708907503636)"
        embed = discord.Embed(
            color=ctx.author.color,
            title="Custom commands V4.1",
            description=des,
            timestamp=ctx.message.created_at,
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    def get_info(self):
        cores = psutil.cpu_count()
        cpup = psutil.cpu_percent()
        vram = psutil.virtual_memory()
        free = round(vram.free / 1048576, 2)
        total = round(vram.total / 1048576, 2)
        used = round(vram.used / 1048576, 2)
        disktotal = round(psutil.disk_usage("/").total / 1073741824, 2)
        diskused = round(psutil.disk_usage("/").used / 1073741824, 2)
        diskfree = round(psutil.disk_usage("/").free / 1073741824, 2)

        data = f"■ **Cpu Info**\n"
        data += f"▪︎▪︎Cores : {cores} \n"
        data += f"▪︎▪︎Percentage : {cpup}% \n"
        data += f"■ **Ram Info**\n"
        data += f"▪︎▪︎Total : {total} MB\n"
        data += f"▪︎▪︎Used : {used} MB\n"
        data += f"▪︎▪︎Free : {free} MB\n"
        data += f"■ **Disk Info**\n"
        data += f"▪︎▪︎Total {disktotal} GB\n"
        data += f"▪︎▪︎Used {diskused} GB\n"
        data += f"▪︎▪︎Free {diskfree} GB\n"

        return data

    @commands.command()
    @commands.is_owner()
    async def systeminfo(self, ctx, count: int = 10):
        for i in range(1, count + 1):
            thing = functools.partial(self.get_info)
            data = await self.bot.loop.run_in_executor(None, thing)

            try:
                await mmsg.edit(content=data)
            except:
                mmsg = await ctx.send(data)
            await asyncio.sleep(1.5)

        await mmsg.delete()

    @commands.command()
    async def invite(self, ctx):
        link = "https://discord.com/oauth2/authorize?client_id=724847752449753140&permissions=268815424&scope=bot"
        embed = discord.Embed(
            color=ctx.author.color,
            title="Custom Commands",
            description=f"[click here]({link})",
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
