import discord
from discord.ext import commands
import json


class Admin(commands.Cog):
    """Bot owner commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def res(self, ctx):
        with open('data.json', 'r') as f:
            data = json.load(f)
        for guild, datas in data.items():

            settings = datas['settings']
            try:
                await self.bot.db.execute("INSERT INTO guild_data(guild, prefix, noprefix, cprefix) VALUES ($1, $2, $3, $4)", int(guild), settings['prefix'], settings['noprefix'], settings['cprefix'])
            except:
                pass

            vars = datas['variables']
            for key, value in vars.items():
                name = key
                id = value['id']
                val = value['value']
                userid = value['userid']
                guildid = value['guild']
                editorid = value['editorid']

                await self.bot.db.execute("INSERT INTO variables(name, value, guild, userid, editorid) VALUES ($1, $2, $3, $4, $5)", name, val, guildid, userid, editorid)

            guildid = int(guild)
            cmds = datas['commands']
            for name, info in cmds.items():
                id = info['id']
                type = info['type']
                userid = info['userid']
                guild = guildid
                help = info['help']
                approved = info['approved']

                try:
                    await self.bot.db.execute("INSERT INTO commands(id, userid, guild, name, type, help, approved) VALUES ($1, $2, $3, $4, $5, $6, $7)", id, userid, guild, name, type, help, approved)
                except:
                    pass

                if type == "embed":
                    cdata = info['data']
                    command_id = cdata['command_id']
                    title = cdata['title']
                    description = cdata['description']
                    thumbnail = cdata['thumbnail']
                    image = cdata['image']

                    try:
                        await self.bot.db.execute("INSERT INTO embed(command_id, title, description, thumbnail, image) VALUES ($1, $2, $3, $4, $5)", command_id, title, description, thumbnail, image)
                    except:
                        pass


                if type == "text":
                    cdata = info['data']
                    command_id = cdata['command_id']
                    content = cdata['content']

                    try:
                        await self.bot.db.execute("INSERT INTO text(command_id, content) VALUES ($1, $2)", command_id, content)
                    except:
                        pass

                if type == "role":
                    cdata = info['data']
                    command_id = cdata['command_id']
                    role = cdata['role']
                    action = cdata['action']

                    try:
                        await self.bot.db.execute("INSERT INTO role(command_id, role, action) VALUES ($1, $2, $3)", command_id, role, action)
                    except:
                        pass

            aliases = datas['aliases']
            for name, alias in aliases.items():
                name = name
                cmd_id = alias['cmd_id']
                userid = alias['userid']
                guildid = alias['guildid']

                try:
                    await self.bot.db.execute("INSERT INTO aliases(name, cmd_id, user_id, guild) VALUES ($1, $2, $3, $4)", name, cmd_id, userid, guildid)
                except:
                    pass


def setup(bot):
    bot.add_cog(Admin(bot))
