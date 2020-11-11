import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def help(self, ctx, command: str = None):
        if command is not None:
            cmd = self.bot.get_command("info")

            return await ctx.invoke(cmd, command, False)
        prefix = ctx.prefix
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Help for Custom Commands",
            description=f"Type `{prefix}help <command_type>` to get help on a specific type of command. \n\n"
                        f"Or go to [Web Dashboard](https://customcommands.xyz) and start making commands\n",
        )

        available_commands = f"1. embed `{prefix}help embed` \n2. text `{prefix}help text`\n3. giverole `{prefix}help giverole`\n4. removerole `{prefix}help removerole`\n5. togglerole `{prefix}help togglerole`\n6. giveandremove `{prefix}help giveandremove`\n7. random `{prefix}help random`"
        other_commands = f"1. poll `{prefix}help poll`\n2. vote `{prefix}help vote`"

        embed.add_field(name="Available command types", value=available_commands)
        embed.add_field(name="Other commands", value=other_commands)

        embed.add_field(
            name="Management",
            value=f"Use `{prefix}help management` to see management related commands.",
            inline=False,
        )

        embed.set_footer(text=f"Use `{prefix}prefix <new_prefix>` to change prefix")

        await ctx.send(embed=embed)

    @help.command()
    async def management(self, ctx):
        prefix = ctx.prefix

        desc = (
            f"`{prefix}list [approved/unapproved]` list all commands of this server. \n"
        )
        desc += f"`{prefix}delete <command_name>` Delete a command. \n"
        desc += f"`{prefix}info <command_name>` See info of a command.\n"
        desc += f"`{prefix}raw <command_name>` See raw data of a command.\n"
        desc += (
            f"`{prefix}help <command_name>` will also show your custom command help.\n"
        )
        desc += f"`{prefix}alias <command_name> <alias>` Will alias a command to another one.\n\n"
        desc += f"`{prefix}approve <command_name>` To approve an command made by server members.\n"
        desc += f"`{prefix}unapprove <command_name>` To unapprove an command.\n"
        desc += f"`{prefix}noprefix toggle` will turn on/off noprefix settings.\n"
        desc += f"`{prefix}ccprefix <new_prefix>` If you want different prefix for custom commands.\n"
        desc += (
            f"`{prefix}ccprefix reset` Will reset custom commands prefix.\n\n"
            f"__Backup and Restore__\n"
            f"This feature requires premium subscription \n\n"
            f"`{prefix}backup` Backup all your command and variables\n"
            f"`{prefix}restore <code>` Restore commands from a backup in any server\n"
        )
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Help for `Management commands`",
            description=desc,
        )
        await ctx.send(embed=embed)

    @help.command()
    async def embed(self, ctx):
        prefix = ctx.prefix
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Help for `embed` commands",
            description=f"Arguments wrapped with [] are optional, Argument wrapped with <> is compulsory.\n\n",
        )

        embed.description += f"\n__Syntax__ \n`{prefix}embed <command_name>` \n\nThen you will be prompted to enter some addtional information like `title`, `description`, `thumbnail`, `image`\n\n"
        embed.description += (
            "You can use variables on embed description like `{user}`, `{server}` and `{members}`. "
            + f"\nTo get help on variables type `{prefix}help variables`"
        )

        await ctx.send(embed=embed)

    @help.command()
    async def variable(self, ctx):
        prefix = ctx.prefix
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Help for `variable`",
            description="Use variable to make command more interactive.",
        )

        embed.description += "\n\n__Pre defined Variables__ :\n"
        embed.description += "`{user}` - Command author name.\n"
        embed.description += "`{user_id}` - Command author id.\n"
        embed.description += "`{user_avatar}` - Command author avatar url.\n"
        embed.description += "`{server}` - server name.\n"
        embed.description += "`{server_owner}` - server owner name.\n **.....**\n"
        embed.description += "See a list of all pre defined variables [Here](https://custom-commands-is.the-be.st/#/?id=making-command-interactive)\n"

        embed.description += "\n\n__Custom variable__\n"
        embed.description += (
            f"`{prefix}variable add <name> <value>` - To make your own variable.\n"
        )
        embed.description += (
            f"`{prefix}variable edit <name> <new_value>` - To edit a variable.\n"
        )
        embed.description += (
            f"`{prefix}variable view <name>` - To view value of a variable.\n"
        )
        embed.description += (
            f"`{prefix}variable remove <name>` - To remove/delete variable.\n"
        )
        embed.description += f"`{prefix}variable list` - See all available variable.\n"
        embed.description += f"\n**Note :** Making a variable already available in pre defined variables will override that.\n"

        await ctx.send(embed=embed)

    @help.command()
    async def text(self, ctx):
        prefix = ctx.prefix
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Help for `text` commands",
            description=f"Arguments wrapped with [] are optional, Argument wrapped with <> is compulsory.\n",
        )

        embed.description += f"\n__Syntax__ \n`{prefix}text <command_name>` \nThen you will be prompted to enter contents of that command\n\n"
        embed.description += (
            "You can use variables like `{user}`, `{server}` and `{members}`. "
            + f"\nTo get help on variables type `{prefix}help variable`"
        )

        await ctx.send(embed=embed)

    @help.command()
    async def random(self, ctx):
        prefix = ctx.prefix
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Help for `text` commands",
            description=f"Arguments wrapped with [] are optional, Argument wrapped with <> is compulsory.\n",
        )

        embed.description += f"\n__Syntax__ \n`{prefix}random <command_name>` \n" \
                             f"Then you will be prompted to enter contents of that command. " \
                             f"Which will be same as text but here you can have multiple responses. " \
                             f"Be sure to separate them using `|`\n\n"

        await ctx.send(embed=embed)

    @help.command()
    async def giverole(self, ctx):
        prefix = ctx.prefix
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Help for `goverole` commands",
            description=f"Arguments wrapped with [] are optional, Argument wrapped with <> is compulsory.\n\nAdd specific role to command executor\n",
        )

        embed.description += f"\n__Syntax__ \n`{prefix}giverole <command_name> <role1><role2><role3>...` \nThis type of command requires manage roles permission to the bot. Make sure to grant that before."

        await ctx.send(embed=embed)

    @help.command()
    async def removerole(self, ctx):
        prefix = ctx.prefix
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Help for `removerole` commands",
            description=f"Arguments wrapped with [] are optional, Argument wrapped with <> is compulsory.\n\nRemove specific role from command executor\n",
        )

        embed.description += f"\n__Syntax__ \n`{prefix}removerole <command_name> <role1><role2><role3>...` \nThis type of command requires manage roles permission to the bot. Make sure to grant that before."

        await ctx.send(embed=embed)

    @help.command()
    async def togglerole(self, ctx):
        prefix = ctx.prefix
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Help for `togglerole` commands",
            description=f"Arguments wrapped with [] are optional, Argument wrapped with <> is compulsory.\n\nIf a user has that role it removes that and if user dont have the role it adds that.\n",
        )

        embed.description += f"\n__Syntax__ \n`{prefix}togglerole <command_name> <role1><role2><role3>...` \nThis type of command requires manage roles permission to the bot. Make sure to grant that before."

        await ctx.send(embed=embed)

    @help.command()
    async def giveandremove(self, ctx):
        prefix = ctx.prefix
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Help for `giveandremove` commands",
            description=f"Arguments wrapped with [] are optional, Argument wrapped with <> is compulsory.\n\nIt will add certain role and remove role at a time.\n",
        )

        embed.description += f"\n__Syntax__ \n`{prefix}giveandremove <command_name> ` \nThis type of command requires manage roles permission to the bot. Make sure to grant that before."

        await ctx.send(embed=embed)

    @help.command()
    async def poll(self, ctx):
        prefix = ctx.prefix
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Help for `poll` commands",
            description=f"Arguments wrapped with [] are optional, Argument wrapped with <> is compulsory.\n",
        )

        embed.description += f'__Syntax__ \n`{prefix}poll <question> <choices>` \n__Example : __ `{prefix}poll "Are you feeling good today?" Yes,No,IDK` \n\nIts compulsory to separate choices with comma(,). Max choice is 4. If you give more than 4, only first 4 will be taken'

        await ctx.send(embed=embed)

    @help.command()
    async def vote(self, ctx):
        prefix = ctx.prefix
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Help for `vote` command",
            description=f"Arguments wrapped with [] are optional, Argument wrapped with <> is compulsory.\n",
        )

        embed.description += f'__Syntax__ \n`{prefix}vote <question> <duration_in_seconds> <options>` \n__Example : __ `{prefix}poll "Who should be the next mod of our server?" John,Doe,No One` \n\nIts compulsory to separate options with comma(,). Max option is 4. If you give more than 4, only first 4 will be taken \nAfter <duration_in_seconds> time finished vote will close and result will be published'

        await ctx.send(embed=embed)

    @help.command()
    async def edit(self, ctx, command_type: str = None):
        if not command_type:
            prefix = ctx.prefix
            embed = discord.Embed(
                color=discord.Color.blurple(),
                title="Help for Custom Commands",
                description=f"Type `{prefix}help edit <command_type>` to get help on a specific type of command",
            )

            available_commands = "1. embed \n2.text \n3. role\n4. command"

            embed.add_field(name="Editable commands", value=available_commands)

            await ctx.send(embed=embed)

        if command_type.lower() == "command":
            prefix = ctx.prefix
            embed = discord.Embed(
                color=discord.Color.blurple(),
                title="Help for editing embed commands",
                description="",
            )

            embed.description += f"__Syntax__ \n`{prefix}edit command <component> <command_name> <value>` \n__Example : __ `{prefix}edit command help your_command  Your own info for a command` \n\n__Editable components :__ `help`, `name`, `owner`"
            await ctx.send(embed=embed)

        if command_type.lower() == "embed":
            prefix = ctx.prefix
            embed = discord.Embed(
                color=discord.Color.blurple(),
                title="Help for editing embed commands",
                description="",
            )

            embed.description += f"__Syntax :__ \n`{prefix}edit embed <command_name> <component> <value>`\n__Example :__ \n`{prefix}edit embed myembed title This is new title`\n\n__Editable components : __`title`, `thumbnail`, `image`, `description`"
            await ctx.send(embed=embed)

        if command_type.lower() == "text":
            prefix = ctx.prefix
            embed = discord.Embed(
                color=discord.Color.blurple(),
                title="Help for editing text commands",
                description="",
            )

            embed.description += f"__Syntax__ \n`{prefix}edit text <command_name> <content>` \n__Example : __ `{prefix}edit text mytextcommand Some new content.`"
            await ctx.send(embed=embed)

        if command_type.lower() == "role":
            prefix = ctx.prefix
            embed = discord.Embed(
                color=discord.Color.blurple(),
                title="Help for editing give role commands",
                description="",
            )

            embed.description += f"Any role related command can be editted by this. Whether thats a give, remove or toggle role command. \n\n__Syntax__ \n`{prefix}edit role <command_name> <new_role>` \n__Example : __ `{prefix}edit role myrolecommand @MyNewRole.`"
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
