import traceback
import aiofiles
import sys
import discord


async def command_exists(bot, command, guild):
    """Check for a commands existence return record or False according to existence"""

    cmd = await bot.db.fetchrow(
        "SELECT * FROM commands WHERE name = $1 and guild = $2", command, guild.id
    )
    if cmd:
        return cmd
    alias = await bot.db.fetchrow(
        "SELECT * FROM aliases WHERE name = $1 and guild = $2", command, guild.id
    )
    if alias:
        command = await bot.db.fetchrow(
            "SELECT * FROM commands WHERE id = $1", alias["cmd_id"]
        )
        return command
    else:
        return False


async def only_command_exists(bot, command, guild):
    """Check for a commands existence return record or False according to existence"""

    cmd = await bot.db.fetchrow(
        "SELECT * FROM commands WHERE name = $1 and guild = $2", command, guild.id
    )
    if cmd:
        return cmd
    else:
        return False


async def only_alias_exists(bot, command, guild):
    """Check for a alias existence return record or False according to existence"""

    alias = await bot.db.fetchrow(
        "SELECT * FROM aliases WHERE name = $1 and guild = $2", command, guild.id
    )
    if alias:
        return alias
    else:
        return False


def check_sessions(bot, ctx, name):
    """Checking if a session with that command name exists in this guild"""

    if ctx.author.id in bot.user_sessions:
        prev_cmd = bot.prev_commands[ctx.author.id]
        return [True, f"Please finish making the `{prev_cmd}` command first."]
    else:
        bot.user_sessions.append(ctx.author.id)
        prev_data = {ctx.author.id: name}
        bot.prev_commands.update(prev_data)
    try:
        sessions = bot.bot_sessions[ctx.guild.id]

        if name in sessions:
            return [
                True,
                f"Someone in this server already making a command with the name `{name}` please use a different name.",
            ]

        sessions.append(name)
        data = {ctx.guild.id: sessions}
        bot.bot_sessions.update(data)
        return [False]
    except:
        data = {ctx.guild.id: [name]}
        bot.bot_sessions.update(data)
        return [False]


def invalidate(bot, guild: discord.Guild, user: discord.Member, name: str):
    """Invalidate/destroy sessions after command making finished or cancelled"""

    try:
        sessions = bot.bot_sessions[guild.id]
        sessions.remove(name)
        if not sessions:
            bot.bot_sessions.pop(guild.id)

        bot.prev_commands.pop(user.id)
    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        exc_content = traceback.format_exception(exc_type, exc_value, exc_tb)

        with open("logs.txt", "a") as f:
            f.write(exc_content + "\n\n")

    if user.id in bot.user_sessions:
        bot.user_sessions.remove(user.id)


async def delete_command(bot, cmd_id: int):
    await bot.db.execute("DELETE FROM commands WHERE id=$1", cmd_id)


async def get_command(bot, name, guild_id):
    data = await bot.db.fetchrow(
        "SELECT * FROM commands WHERE name = $1 and guild = $2", name, guild_id
    )
    alias = None
    if not data:
        alias = await bot.db.fetchrow(
            "SELECT * FROM aliases WHERE name = $1 and guild = $2", name, guild_id
        )

    if alias:
        data = await bot.db.fetchrow(
            "SELECT * FROM commands WHERE id = $1", alias["cmd_id"]
        )

    return data
