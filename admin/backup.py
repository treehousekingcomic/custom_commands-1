from discord.ext import commands
import discord
import json


class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def backupall(self, ctx):
        mm = await ctx.send("Data backup initiated..")
        rows = 0
        data = {}

        for guild in self.bot.guilds:
            rows += 1
            data[guild.id] = {"settings": None, "variables": None, "commands": None}
            commands_data = {}
            variable_data = {}

            settings = await self.bot.db.fetchrow(
                "SELECT * FROM guild_data WHERE guild = $1", guild.id
            )
            settings_data = {
                "prefix": settings["prefix"],
                "cprefix": settings["cprefix"],
                "noprefix": settings["noprefix"],
            }

            data[guild.id]["settings"] = settings_data

            commands_ = await self.bot.db.fetch(
                "SELECT * FROM commands WHERE guild = $1", guild.id
            )
            variables = await self.bot.db.fetch(
                "SELECT * FROM variables WHERE guild = $1", guild.id
            )

            for variable in variables:
                rows += 1
                variable_data[variable["id"]] = {
                    "name": variable["name"],
                    "value": variable["value"],
                    "guild": variable["guild"],
                    "userid": variable["userid"],
                    "editorid": variable["editorid"],
                }

            data[guild.id]["variables"] = variable_data

            for command in commands_:
                rows += 2
                commands_data[command["id"]] = {
                    "userid": command["userid"],
                    "guild": command["guild"],
                    "name": command["name"],
                    "type": command["type"],
                    "help": command["help"],
                    "approved": command["approved"],
                }
                if command["type"] == "embed":
                    embed = await self.bot.db.fetchrow(
                        "SELECT * FROM embed WHERE command_id = $1", command["id"]
                    )
                    command_info = {
                        "title": embed["title"],
                        "description": embed["description"],
                        "thumbnail": embed["thumbnail"],
                        "image": embed["image"],
                    }

                    commands_data[command["id"]]["data"] = command_info

                if command["type"] == "text":
                    text = await self.bot.db.fetchrow(
                        "SELECT * FROM text WHERE command_id = $1", command["id"]
                    )
                    command_info = {"content": text["content"]}
                    commands_data[command["id"]]["data"] = command_info

                if command["type"] == "random":
                    text = await self.bot.db.fetchrow(
                        "SELECT * FROM randomtext WHERE command_id = $1", command["id"]
                    )
                    command_info = {"contents": text["contents"]}
                    commands_data[command["id"]]["data"] = command_info

                if command["type"] == "role":
                    role = await self.bot.db.fetchrow(
                        "SELECT * FROM role WHERE command_id = $1", command["id"]
                    )
                    if role:
                        command_info = {"role": role["role"], "action": role["action"]}
                        commands_data[command["id"]]["data"] = command_info
                    else:
                        print(command['id'])

                if command["type"] == "mrl":
                    role = await self.bot.db.fetchrow(
                        "SELECT * FROM multirole WHERE command_id = $1", command["id"]
                    )
                    command_info = {"gives": role["gives"], "removes": role["removes"]}
                    commands_data[command["id"]]["data"] = command_info

                aliases = await self.bot.db.fetch(
                    "SELECT * FROM aliases WHERE cmd_id = $1", command["id"]
                )
                alias_data = {}
                for alias in aliases:
                    rows += 1
                    alias_data[alias["id"]] = {
                        "name": alias["name"],
                        "cmd_id": alias["cmd_id"],
                        "user_id": alias["user_id"],
                        "guild": alias["guild"],
                    }

                commands_data[command["id"]]["aliases"] = alias_data

                data[guild.id]["commands"] = commands_data

        with open("data.json", "w") as f:
            f.write("{}")

        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)

        file = discord.File(fp="data.json", filename="data.json")
        await mm.edit(content=f"Successfully backed up {rows} rows of data.")
        await ctx.author.send(file=file)

    async def insert_command(
        self, userid, guild, name, type, help, approved, data, aliases
    ):
        await self.bot.db.execute(
            "INSERT INTO commands(userid, guild, name, type, help, approved) VALUES ($1, $2, $3, $4, $5, $6)",
            userid,
            guild,
            name,
            type,
            help,
            approved,
        )
        command = await self.bot.db.fetchrow(
            "SELECT * FROM commands WHERE name = $1 and guild = $2", name, guild
        )

        command_id = command["id"]

        if type == "embed":
            await self.bot.db.execute(
                "INSERT INTO embed(command_id, title, description, thumbnail, image) VALUES ($1, $2, $3, $4, $5)",
                command_id,
                data["title"],
                data["description"],
                data["thumbnail"],
                data["image"],
            )

        if type == "text":
            await self.bot.db.execute(
                "INSERT INTO text (command_id, content) VALUES ($1, $2)",
                command_id,
                data["content"],
            )

        if type == "random":
            await self.bot.db.execute(
                "INSERT INTO randomtext (command_id, contents) VALUES ($1, $2)",
                command_id,
                data["contents"],
            )

        if type == "role":
            try:
                await self.bot.db.execute(
                    "INSERT INTO role (command_id, role, action) VALUES ($1, $2, $3)",
                    command_id,
                    data["role"],
                    data["action"],
                )
            except:
                print(data)

        if type == "mrl":
            await self.bot.db.execute(
                "INSERT INTO multirole (command_id, gives, removes) VALUES ($1, $2, $3)",
                command_id,
                data["gives"],
                data["removes"],
            )

        for alias_id, data in aliases.items():
            await self.bot.db.execute(
                "INSERT INTO aliases(name, cmd_id, user_id, guild) VALUES ($1, $2, $3, $4)",
                data["name"],
                command_id,
                data["user_id"],
                guild,
            )

    @commands.command()
    @commands.is_owner()
    async def restoreall(self, ctx):
        mm = await ctx.send("Restore data initiated.")
        rows = 0
        await self.bot.db.execute("DELETE FROM guild_data")
        with open("data.json", "r") as f:
            data = json.load(f)

        for guild, datas in data.items():
            rows += 1
            guild_id = int(guild)
            settings = datas["settings"]
            commands = datas["commands"]
            variables = datas["variables"]

            try:
                await self.bot.db.execute(
                    "INSERT INTO guild_data(guild, prefix, noprefix, cprefix) VALUES ($1, $2, $3, $4)",
                    guild_id,
                    settings["prefix"],
                    settings["noprefix"],
                    settings["cprefix"],
                )
            except Exception as e:
                print(e)

            if commands:
                rows += 2
                for _id, info in commands.items():
                    userid = info["userid"]
                    guild = info["guild"]
                    name = info["name"]
                    type = info["type"]
                    help = info["help"]
                    approved = info["approved"]
                    data = info["data"]
                    aliases = info["aliases"]

                    await self.insert_command(
                        userid, guild, name, type, help, approved, data, aliases
                    )

            if variables:
                rows += 1
                for var_id, vdata in variables.items():
                    await self.bot.db.execute(
                        "INSERT INTO variables(name, value, guild, userid, editorid) VALUES ($1, $2, $3, $4, $5)",
                        vdata["name"],
                        vdata["value"],
                        guild_id,
                        vdata["userid"],
                        vdata["editorid"],
                    )

        await mm.edit(content=f"Successfully restored {rows} rows of data.")


def setup(bot):
    bot.add_cog(Backup(bot))
