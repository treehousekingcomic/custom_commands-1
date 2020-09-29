from discord.ext import commands


class Maker(commands.Cog):
    """Command maker cog"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.bot_sessions = {}
        self.bot.user_sessions = []
        self.bot.prev_commands = {}


def setup(bot):
    bot.add_cog(Maker(bot))
