async def getprefix(bot, message):
    data = await bot.db.fetchrow(
        "SELECT * FROM guild_data WHERE guild=$1", message.guild.id
    )
    if data:
        prefix = data["prefix"]
    else:
        prefix = "**"

    return prefix
