# Modified Version 4.1b

## Updates
- Better management
- Table relationship added to make it easy

### Custom Command
A discord bot that allow users to make custom commands per server [Read Docs Here](https://shahprog.github.io/docs/)

### Installation
1. Install **postgresql**
2. Create a new **role** and **database** and give necessary privilages to the role on the database
3. Edit **config.py** and fill up with right credentials
4. Edit **.env** and add `token`

### Required packages
1. `jishaku`(For debugging)
2. `asyncpg`(For database oprations)
3. [discord.ext.menus](https://github.com/Rapptz/discord-ext-menus) (For paginating command list)
4. `psutil`(For systeminfo)
5. `humanize`(For human readable date conversion)

After all the upper steps done run the `bot.py` file.

### Contributors
`AliTheKing#9129`
