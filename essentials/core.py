async def getprefix(bot, message):
    try:
        prefix = bot.prefixes[message.guild.id]
        return prefix
    except:
        data = await bot.db.fetchrow(
            "SELECT * FROM guild_data WHERE guild=$1", message.guild.id
        )
        if data:
            prefix = data["prefix"]
        else:
            prefix = "**"

    return prefix