import discord
from discord.ext import commands
import asyncio


class Others(commands.Cog):
    """Other userfull commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def poll(self, ctx, question: str, *, choices: str):
        """Make polls (Not a command). Max choices is 4. Choices should be separated by comma. example : `**make polls "Are you happy today? Yes,No,Not Sure,IDK"`"""
        inits = [choice.strip() for choice in choices.split(",") if choice != ""]
        options = []
        checking = list(set(inits))
        for option in inits:
            if option in checking:
                options.append(option)
                checking.remove(option)

        if len(options) < 2:
            return await ctx.send("At least 2 unique choice is mandatory")

        if len(options) > 4:
            await ctx.send(
                "```More than 4 choice supplied. First 4 of them taken```",
                delete_after=3,
            )

        options = options[:4]
        emojis = [
            "\N{REGIONAL INDICATOR SYMBOL LETTER A}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER B}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER C}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER D}",
        ]
        indexes = ["A", "B", "C", "D"]

        embed = discord.Embed(title=question,)

        desc = ""
        for i in range(0, len(options)):
            desc += (
                f"`[{indexes[i]}]` **{discord.utils.escape_mentions(options[i])}** \n"
            )

        embed.description = desc
        embed.set_footer(text=f"Poll by - {ctx.author}", icon_url=ctx.author.avatar_url)
        poll = await ctx.send(embed=embed)
        for i in range(0, len(options)):
            try:
                await poll.add_reaction(emojis[i])
            except:
                pass
            await asyncio.sleep(0.2)

    @commands.command()
    async def vote(self, ctx, question: str, duration: int, *, choices: str):
        """Make vote (Not a command). Max choices is 4. Choices should be separated by comma. example : `**make vote "Are you happy today? 60 Yes,No,Not Sure,IDK"`"""
        inits = [choice.strip() for choice in choices.split(",") if choice != ""]
        print(inits)
        options = []
        checking = list(set(inits))
        print(checking)
        for option in inits:
            if option in checking:
                options.append(option)
                checking.remove(option)

        print(options)
        if len(options) < 2:
            return await ctx.send("At least 2 unique choice is mandatory")

        if len(options) > 4:
            await ctx.send(
                "```More than 4 choice supplied. First 4 of them taken```",
                delete_after=3,
            )

        options = options[:4]
        emojis = [
            "\N{REGIONAL INDICATOR SYMBOL LETTER A}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER B}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER C}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER D}",
        ]
        indexes = ["A", "B", "C", "D"]

        embed = discord.Embed(title=question, description="")

        for i in range(0, len(options)):
            embed.description += (
                f"`[{indexes[i]}]` **{discord.utils.escape_mentions(options[i])}** \n"
            )

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text=f"Vote ends in {duration} seconds.")

        msg = await ctx.send(embed=embed)
        for i in range(0, len(options)):
            try:
                await msg.add_reaction(emojis[i])
            except:
                pass
            await asyncio.sleep(0.2)

        await asyncio.sleep(duration)

        msg = await ctx.channel.fetch_message(msg.id)
        counts = []
        for react in msg.reactions:
            counts.append(react.count)
        winner = counts.index(max(counts))
        choice = options[winner]

        if max(counts) == min(counts):
            description = "No option won this vote."
        else:
            if counts.count(max(counts)) > 1:
                description = f"{counts.count(max(counts))} option got same vote. No winner this time."
            else:
                description = f"`{choice}` won with {max(counts) -1} votes."

        embed = discord.Embed(title=question, description=description)
        await msg.edit(embed=embed)


def setup(bot):
    bot.add_cog(Others(bot))
