import discord
from discord.ext import commands
import datetime
from config import default_prefix


class Events(commands.Cog):
    """Bot event listeners"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.bot.prefixes[guild.id] = default_prefix
        self.bot.cprefix[guild.id] = None
        self.bot.noprefix[guild.id] = "no"

        data = await self.bot.db.fetchrow(
            "SELECT * FROM guild_data WHERE guild=$1", guild.id
        )
        if not data:
            await self.bot.db.execute(
                "INSERT INTO guild_data(guild, prefix) VALUES($1, $2)",
                guild.id,
                default_prefix,
            )

        # Sending notification to bot-logs channel
        su_guild = self.bot.get_guild(700374484955299900)
        channel = discord.utils.get(su_guild.text_channels, id=727603709885939793)
        embed = discord.Embed(
            title="New Server join",
            description=f"Bot has been added to - {guild.name}",
            timestamp=datetime.datetime.utcnow(),
        )

        embed.set_thumbnail(url=str(self.bot.user.avatar_url))
        embed.set_footer(text=f"Current server count - {len(self.bot.guilds)}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            await self.bot.db.execute("DELETE FROM guild_data WHERE guild=$1", guild.id)
            print(f"Bot get kicked from {guild.name} and data deleted.")
        except:
            print(f"Something went wrong deleting a row {guild.id}")

        # Sending notification to bot-logs channel
        su_guild = self.bot.get_guild(700374484955299900)
        channel = discord.utils.get(su_guild.text_channels, id=727603709885939793)
        embed = discord.Embed(
            title="Server leave",
            description=f"Bot has been removed from - {guild.name}",
            timestamp=datetime.datetime.utcnow(),
        )

        embed.set_thumbnail(url=str(self.bot.user.avatar_url))
        embed.set_footer(text=f"Current server count - {len(self.bot.guilds)}")
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Events(bot))
