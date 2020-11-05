import discord
from discord.ext import commands
import asyncpg
import os
import datetime
import dotenv
from config import extensions, db_config, default_prefix, query_strings
from essentials import command_handler
from essentials.core import getprefix
from halo import Halo


class MyBot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_cache = []

    async def on_ready(self):
        print(
            f"{str(self.user)} started successfully. latency is {self.latency * 1000}ms"
        )
        self.launch_time = datetime.datetime.now()
        self.command_ran = 0
        self.custom_command_ran = 0

        self.prefixes = {}
        self.noprefix = {}
        self.cprefix = {}

        # Caching prefixes data
        data = await self.db.fetch("SELECT * FROM guild_data")

        for row in data:
            self.prefixes[row["guild"]] = row["prefix"]
            self.noprefix[row["guild"]] = row["noprefix"]
            self.cprefix[row["guild"]] = row["cprefix"]

        print(self.prefixes[700374484955299900])

    async def on_command(self, ctx):
        self.command_ran += 1

    async def on_message(self, message):
        if not message.guild or message.author == self.user or message.content == "":
            return

        await self.process_commands(message)

        try:
            noprefix = bot.noprefix[message.guild.id]
            cprefix = bot.cprefix[message.guild.id]
            prefix = bot.prefixes[message.guild.id]
            if cprefix is not None:
                prefix = cprefix

        except:
            data = await self.db.fetchrow(
                "SELECT * FROM guild_data WHERE guild=$1", message.guild.id
            )

            if data is None:
                await self.db.execute(
                    "INSERT INTO guild_data(guild, prefix) VALUES($1, $2)",
                    message.guild.id,
                    default_prefix,
                )

                prefix = default_prefix
                noprefix = "no"
                cprefix = None
                if cprefix:
                    prefix = cprefix
            else:
                prefix = data["prefix"]
                cprefix = data["cprefix"]
                noprefix = data["noprefix"]

                if cprefix:
                    prefix = cprefix

        if noprefix == "yes":
            if message.content.startswith(prefix):
                ccmd = message.content[len(prefix) :]
            else:
                ccmd = message.content
        else:
            if message.content.startswith(prefix):
                ccmd = message.content[len(prefix) :]
            else:
                return

        ctx = await self.get_context(message)
        runner = command_handler.Runner(self)

        await runner.run_command(ctx, name=ccmd, indm=False, bypass_check=False)


bot = MyBot(
    command_prefix=getprefix,
    allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=False),
)
bot.remove_command("help")


async def create_db_pool():
    bot.db = await asyncpg.create_pool(**db_config)
    for query in query_strings:
        await bot.db.execute(query)


bot.loop.run_until_complete(create_db_pool())

log = ""
with Halo(text="Loading Extensions", spinner="dots"):
    for extenstion in extensions:
        try:
            bot.load_extension(extenstion)
        except Exception as e:
            log += f"Failed to load {extenstion} {e}.\n"

print(log)

dotenv.load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
