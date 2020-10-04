import json
from discord.ext import commands, menus
import random
import asyncio
import os
from essentials.command_checks import command_exists, only_alias_exists
import discord


class MySource(menus.ListPageSource):
    def __init__(self, data, title: str):
        super().__init__(data, per_page=10)
        self.title = title

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        embed = discord.Embed(
            title=f"({self.title})", color=discord.Color.blurple()
        )
        description = "\n".join(
            f"{i+1}. {v}" for i, v in enumerate(entries, start=offset)
        )

        embed.description = description
        return embed


class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def insert_command(self, userid, guild, name, type, help, approved, data, aliases):
        await self.bot.db.execute(
            "INSERT INTO commands(userid, guild, name, type, help, approved) VALUES ($1, $2, $3, $4, $5, $6)",
            userid, guild, name, type, help, approved)
        command = await self.bot.db.fetchrow("SELECT * FROM commands WHERE name = $1 and guild = $2", name, guild)

        command_id = command['id']

        if type == 'embed':
            await self.bot.db.execute(
                "INSERT INTO embed(command_id, title, description, thumbnail, image) VALUES ($1, $2, $3, $4, $5)",
                command_id, data['title'], data['description'], data['thumbnail'], data['image'])

        if type == 'text':
            await self.bot.db.execute("INSERT INTO text (command_id, content) VALUES ($1, $2)", command_id,
                                      data['content'])

        if type == 'role':
            await self.bot.db.execute("INSERT INTO role (command_id, role, action) VALUES ($1, $2, $3)", command_id,
                                      data['role'], data['action'])

        if type == 'mrl':
            await self.bot.db.execute("INSERT INTO multirole (command_id, gives, removes) VALUES ($1, $2, $3)",
                                      command_id, data['gives'], data['removes'])

        for alias_id, data in aliases.items():
            await self.bot.db.execute("INSERT INTO aliases(name, cmd_id, user_id, guild) VALUES ($1, $2, $3, $4)",
                                      data['name'], command_id, userid, guild)

    async def get_command_data(self, ctx):
        commands_ = await self.bot.db.fetch("SELECT * FROM commands WHERE guild = $1 and approved = $2", ctx.guild.id, 'yes')
        commands_data = {}
        for command in commands_:
            commands_data[command['id']] = {
                'userid': command['userid'],
                'guild': command['guild'],
                'name': command['name'],
                'type': command['type'],
                'help': command['help'],
                'approved': command['approved'],
            }
            if command['type'] == 'embed':
                embed = await self.bot.db.fetchrow("SELECT * FROM embed WHERE command_id = $1", command['id'])
                command_info = {
                    'title': embed['title'],
                    'description': embed['description'],
                    'thumbnail': embed['thumbnail'],
                    'image': embed['image']
                }

                commands_data[command['id']]['data'] = command_info

            if command['type'] == 'text':
                text = await self.bot.db.fetchrow("SELECT * FROM text WHERE command_id = $1", command['id'])
                command_info = {
                    'content': text['content']
                }
                commands_data[command['id']]['data'] = command_info

            if command['type'] == 'role':
                role = await self.bot.db.fetchrow("SELECT * FROM role WHERE command_id = $1", command['id'])
                command_info = {
                    'role': role['role'],
                    'action': role['action']
                }
                commands_data[command['id']]['data'] = command_info

            if command['type'] == 'mrl':
                role = await self.bot.db.fetchrow("SELECT * FROM multirole WHERE command_id = $1", command['id'])
                command_info = {
                    'gives': role['gives'],
                    'removes': role['removes']
                }
                commands_data[command['id']]['data'] = command_info

            aliases = await self.bot.db.fetch("SELECT * FROM aliases WHERE cmd_id = $1", command['id'])
            alias_data = {}
            for alias in aliases:
                alias_data[alias['id']] = {
                    'name': alias['name'],
                    'cmd_id': alias['cmd_id'],
                    'user_id': alias['user_id'],
                    'guild': alias['guild']
                }

            commands_data[command['id']]['aliases'] = alias_data

        return commands_data

    async def get_var_data(self, ctx):
        variables = await self.bot.db.fetch("SELECT * FROM variables WHERE guild = $1", ctx.guild.id)

        variable_data = {}
        for variable in variables:
            variable_data[variable['id']] = {
                'name': variable['name'],
                'value': variable['value'],
                'guild': variable['guild'],
                'userid': variable['userid'],
                'editorid': variable['editorid']
            }

        return variable_data

    async def get_settings_data(self, ctx):
        settings = await self.bot.db.fetchrow("SELECT * FROM guild_data WHERE guild = $1", ctx.guild.id)
        settings_data = {
            'prefix': settings['prefix'],
            'cprefix': settings['cprefix'],
            'noprefix': settings['noprefix']
        }

        return settings_data

    def get_random_name(self):
        data = "abcdefghijklmnopqrstuvwxyzABCDEFGNIJKLMNOPQRSTUVWXYZ1234567890"
        code = ""
        for _ in range(10):
            code += data[random.randint(0, len(data) - 1)]
        return code

    async def is_premium(self, guild):
        res = await self.bot.db.fetchrow("SELECT * FROM keys WHERE guild = $1", guild.id)
        if res:
            return True
        else:
            return False

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx):
        if not await self.is_premium(ctx.guild):
            embed = discord.Embed(title="Ignite Support")
            embed.description = f"Backup command requires premium subscription. [Join the official support server](https://discord.gg/7SaE8v2) to get premium free."
            return await ctx.send(embed=embed)

        data = {
            'password': None,
            'owner': ctx.author.id,
            'public': None,
            'guild': ctx.guild.id,
            'settings': None,
            'commands': None,
            'variables': None,
        }

        settings_data = await self.get_settings_data(ctx)
        commands_data = await self.get_command_data(ctx)
        variable_data = await self.get_var_data(ctx)

        data['variables'] = variable_data
        data['settings'] = settings_data
        data['commands'] = commands_data

        def check(m):
            check1 = m.author == ctx.author and m.channel == ctx.channel
            check2 = 8 <= len(m.content) <= 32
            check3 = m.content == "pass"

            if check1 and (check2 or check3):
                return True
            else:
                return False

        pp = await ctx.send(
            "Do you want to password protect this backup? If yes then reply with a password if no then type `pass` within 60 seconds.\n\n"
            "__**Note:**__ "
            "**1**. Password must be 8-32 character long")
        password_ = await self.bot.wait_for('message', timeout=60, check=check)
        password = password_.content
        await password_.delete()
        await pp.delete()

        if password == "pass":
            password = None

        data['password'] = password
        data['owner'] = ctx.author.id

        def check2(m):
            check1 = m.author == ctx.author and m.channel == ctx.channel
            check2 = m.content.lower() in ['yes', 'y', 'no', 'n', 'pass']

            if check1 and check2:
                return True
            else:
                return False

        pp = await ctx.send(
            "Do you want to make this backup publicly available? Reply with `Yes` or `No` within 60 seconds.\n\n"
            "__**Note:**__ "
            f"Making a backup public means anyone can use this backup without any restrictions if theres no password. Learn more about backups by typing `{ctx.prefix}help backup`")

        public_ = await self.bot.wait_for('message', timeout=60, check=check2)
        public = public_.content
        await public_.delete()
        await pp.delete()

        if public.lower() in ['yes', 'y']:
            data['public'] = 'yes'
            aud = True
        else:
            data['public'] = 'no'
            aud = False

        backup_code = self.get_random_name()

        filename = os.path.join(os.getcwd(), 'backup', f"{backup_code}.json")
        with open(filename, 'w') as f:
            f.write('{}')

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

        m = await ctx.send(f"{self.bot.get_emoji(700698346784030810)} Data backup in progress...")
        await self.bot.db.execute("INSERT INTO backups(guild, userid, key, aud) VALUES ($1, $2, $3, $4)", ctx.guild.id,
                                  ctx.author.id, backup_code, aud)
        await asyncio.sleep(5)
        await m.edit(
            content="\N{WHITE HEAVY CHECK MARK}" + f" Data backup successfull. Code `{backup_code}`. Use this code to restore commands anytime.\n\n"
                                                   "__**Note**__: Any type of role command will not work if you restore this backup in s different server. You have to edit them or delete and make new.")

    @backup.command()
    async def list(self, ctx):
        backups = await self.bot.db.fetch("SELECT * FROM backups WHERE guild = $1", ctx.guild.id)

        if len(backups) < 1:
            return await ctx.send("This server has no public backup.")

        lines = []
        for b in backups:
            if b['aud']:
                f = "Public"
            else:
                f = 'Private'

            x = f"{b['key']} `({f})`"
            lines.append(x)

        pages = menus.MenuPages(source=MySource(lines, title=f"Backups"), clear_reactions_after=True)
        await pages.start(ctx)

    @backup.command()
    async def info(self, ctx, code):
        backups = await self.bot.db.fetchrow("SELECT * FROM backups WHERE guild = $1 and key = $2", ctx.guild.id, code)
        if not backups:
            return await ctx.send("Backup not found")

        filename = os.path.join(os.getcwd(), 'backup', f"{code}.json")

        with open(filename, 'r') as f:
            data = json.load(f)

        owner = ctx.guild.get_member(data['owner'])
        if owner:
            owner = owner.mention
        else:
            owner = "Unknown"

        cc = len(data['commands'])
        var = len(data['variables'])
        if backups['aud']:
            priv = "Public"
        else:
            priv = "Private"

        embed = discord.Embed(title=f"Info of `{code}`", color=discord.Color.blurple())
        embed.description = f"**Created by :** {owner}\n" \
                            f"**Commands :** {cc}\n" \
                            f"**Variables :** {var}\n" \
                            f"**Privacy :** {priv}"

        await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def restore(self, ctx, code, password=None):
        filename = os.path.join(os.getcwd(), 'backup', f"{code}.json")
        access1 = False
        can_delete = None
        can_replace = None

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        if not os.path.exists(filename):
            return await ctx.send(f'No backup found with code `{code}`.')

        with open(filename, 'r') as f:
            data = json.load(f)

        if data['public'] == 'yes':
            if data['password'] and data['owner'] != ctx.author.id:
                if not password:
                    mmm = await ctx.send("Enter password of this backup..")
                    try:
                        password_ = await self.bot.wait_for('message', timeout=60, check=check)
                    except:
                        return await ctx.send("Timeout...")

                    if password_.content == data['password']:
                        access1 = True

                    await mmm.delete()
                else:
                    if password == data['password']:
                        access1 = True
            else:
                access1 = True

        if data['public'] == 'no':
            if data['owner'] == ctx.author.id:
                access1 = True
            else:
                return await ctx.send(f'No backup found with code `{code}`.')


        if access1:
            emoji1 = "✅"
            emoji2 = "❎"

            bot = ctx.guild.get_member(self.bot.user.id)
            p = ctx.channel.permissions_for(bot)

            # Delete commands

            if not p.add_reactions or not p.manage_messages:
                return await ctx.send(
                    "Bot need `add reactions` and `manage messages` permission to work further. Please give permissions and try again.")

            delete = await ctx.send("Do you want to delete previous commands?")
            await delete.add_reaction(emoji1)
            await delete.add_reaction(emoji2)

            try:
                def check(reaction, user):
                    return str(reaction.emoji) in [emoji1, emoji2] and (user.id == ctx.author.id and reaction.message.id == delete.id)

                reaction, user = await self.bot.wait_for('reaction_add',  timeout=60, check=check)

                if reaction.emoji == emoji1:
                    can_delete = True

                await delete.delete()

            except:
                await delete.delete()
                return await ctx.send("Timeout...")

            # Replace or rename
            if not can_delete:
                replace = await ctx.send(f"If two command has same name do you want to replace them? React with {emoji1} if you want to replace. If you react with {emoji2} commands with same name will be renamed.")
                await replace.add_reaction(emoji1)
                await replace.add_reaction(emoji2)

                try:
                    def check(reaction, user):
                        return str(reaction.emoji) in [emoji1, emoji2] and (
                                    user.id == ctx.author.id and reaction.message.id == replace.id)

                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)

                    if reaction.emoji == emoji1:
                        can_replace = True

                    await replace.delete()

                except:
                    await replace.delete()
                    return await ctx.send("Timeout...")

            # Restore process
            cmds = data['commands']
            variables = data['variables']

            if can_delete:
                await self.bot.db.execute("DELETE FROM commands WHERE guild = $1", ctx.guild.id)
                await self.bot.db.execute("DELETE FROM variables WHERE guild = $1", ctx.guild.id)

            if cmds:
                for _id, info in cmds.items():
                    userid = info['userid']
                    if not ctx.guild.get_member(userid):
                        userid = ctx.author.id
                    guild = ctx.guild.id
                    name = info['name']
                    type = info['type']
                    help = info['help']
                    approved = info['approved']
                    data = info['data']
                    aliases = info['aliases']

                    xc = await command_exists(self.bot, name, ctx.guild)
                    if xc:
                        if can_delete:
                            await self.insert_command(userid, guild, name, type, help, approved, data, aliases)
                        if not can_replace:
                            name = name + str(random.randint(1, 9))
                            await self.insert_command(userid, guild, name, type, help, approved, data, aliases)
                        else:
                            await self.bot.db.execute("DELETE FROM commands WHERE name = $1 and guild = $2", name, ctx.guild.id)
                    else:
                        await self.insert_command(userid, guild, name, type, help, approved, data, aliases)

            if variables:
                for var_id, vdata in variables.items():
                    userid = vdata['userid']
                    name = vdata['name']
                    if not ctx.guild.get_member(userid):
                        userid = ctx.author.id
                    if await only_alias_exists(self.bot, name, ctx.guild) and not can_delete:
                        name = name + str(random.randint(1, 9))
                        await self.bot.db.execute(
                            "INSERT INTO variables(name, value, guild, userid, editorid) VALUES ($1, $2, $3, $4, $5)",
                            name, vdata['value'], ctx.guild.id, userid, None)
                    else:
                        await self.bot.db.execute("INSERT INTO variables(name, value, guild, userid, editorid) VALUES ($1, $2, $3, $4, $5)", name, vdata['value'], ctx.guild.id, userid, None)

            await ctx.send("Data restored.")

        else:
            return await ctx.send(f'Invalid password.')


    @commands.command()
    async def changepassword(self, ctx, code, new_password):
        filename = os.path.join(os.getcwd(), 'backup', f"{code}.json")

        if not os.path.exists(filename):
            return await ctx.send(f'No backup found with code `{code}`.')

        with open(filename, 'r') as f:
            data = json.load(f)


        if data['owner'] == ctx.author.id:
            if 8 <= len(new_password) <= 32:
                data['password'] = new_password

                with open(filename, 'w') as f:
                    json.dump(data, f)

                await ctx.message.delete()
                await ctx.send(f"Password changed for backup `{code}`")
            else:
                await ctx.send("Password must be in 8-32 characters.")
        else:
            if data['public'] == 'yes' and data['guild'] == ctx.guild.id:
                return await ctx.send("You dont have permissions to change password of this backup.")
            else:
                 return await ctx.send(f'No backup found with code `{code}`.')

    @commands.command()
    async def makepublic(self, ctx, code):
        filename = os.path.join(os.getcwd(), 'backup', f"{code}.json")

        if not os.path.exists(filename):
            return await ctx.send(f'No backup found with code `{code}`.')

        with open(filename, 'r') as f:
            data = json.load(f)

        if data['owner'] == ctx.author.id:
            if data['public'] == 'yes':
                return await ctx.send(f'This backup is already public.')
            data['public'] = 'yes'

            with open(filename, 'w') as f:
                json.dump(data, f)

            await self.bot.db.execute("UPDATE backups SET aud = $1 WHERE key = $2", True, code)

            await ctx.send(f"Backup `{code}` is now public.")
        else:
            if data['public'] == 'yes' and data['guild'] == ctx.guild.id:
                return await ctx.send("You dont have permissions to make this backup public.")
            else:
                return await ctx.send(f'No backup found with code `{code}`.')

    @commands.command()
    async def makeprivate(self, ctx, code):
        filename = os.path.join(os.getcwd(), 'backup', f"{code}.json")

        if not os.path.exists(filename):
            return await ctx.send(f'No backup found with code `{code}`.')

        with open(filename, 'r') as f:
            data = json.load(f)

        if data['owner'] == ctx.author.id:
            if data['public'] == 'no':
                return await ctx.send(f'This backup is already private.')
            data['public'] = 'no'

            with open(filename, 'w') as f:
                json.dump(data, f)

            await self.bot.db.execute("UPDATE backups SET aud = $1 WHERE key = $2", False, code)

            await ctx.send(f"Backup `{code}` is now private.")
        else:
            if data['public'] == 'yes' and data['guild'] == ctx.guild.id:
                return await ctx.send("You dont have permissions to make this backup public.")
            else:
                return await ctx.send(f'No backup found with code `{code}`.')


def setup(bot):
    bot.add_cog(Management(bot))
