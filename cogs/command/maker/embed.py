from discord.ext import commands
from essentials import command_handler
from essentials.command_checks import (
    command_exists,
    invalidate,
    get_command,
    check_sessions,
)


class Maker(commands.Cog):
    """Command maker cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)
    async def embed(self, ctx, name: str):
        cmds = [command.name for command in self.bot.commands]
        for cmd in cmds:
            if name.startswith(cmd):
                return await ctx.send(
                    "Command name contains reserved word. Please use a different name."
                )

        if await command_exists(self.bot, name, ctx.guild):
            return await ctx.send(f"A command with name `{name}` already exists.")

        session_check = check_sessions(self.bot, ctx, name)
        if session_check[0]:
            return await ctx.send(session_check[1])

        def check(message):
            if (message.author == ctx.author and message.channel == ctx.channel) and (
                message.content != "" or len(message.attachments) > 0
            ):
                if message.content.lower().startswith(f"{ctx.prefix}"):
                    return False
                else:
                    return True
            else:
                return False

        embed_step = await ctx.send(
            f"Neat, the command name will be `{name}`. \nWrite embed title below."
        )

        try:
            embed_input = await self.bot.wait_for("message", timeout=180, check=check)
        except:
            invalidate(self.bot, ctx.guild, ctx.author, name)
            return await ctx.send("Command creation cancelled and session destroyed.")

        title = embed_input.content
        if title.lower() == "stop":
            invalidate(self.bot, ctx.guild, ctx.author, name)
            return await ctx.send("Command creation cancelled and session destroyed.")

        if len(title) >= 256:
            invalidate(self.bot, ctx.guild, ctx.author, name)
            return await ctx.send(
                "Title can't be larger that 256 character. Command creation cancelled and session destroyed."
            )

        # Ask description
        embed_step = await ctx.send("Now type description.")

        try:
            embed_input = await self.bot.wait_for("message", timeout=180, check=check)
        except:
            invalidate(self.bot, ctx.guild, ctx.author, name)
            return await ctx.send("Command creation cancelled and session destroyed.")

        description = embed_input.content

        if description.lower() == "stop":
            invalidate(self.bot, ctx.guild, ctx.author, name)
            return await ctx.send("Command creation cancelled and session destroyed.")

        # Ask Thumbnail
        embed_step = await ctx.send(
            "What will be the thumbnail url?  `Be sure to put a valid image url. If you dont want any, type 'pass'`"
        )

        try:
            embed_input = await self.bot.wait_for("message", timeout=180, check=check)
        except:
            invalidate(self.bot, ctx.guild, ctx.author, name)
            return await ctx.send("Command creation cancelled and session destroyed.")

        thumb_url = embed_input.content

        if isinstance(thumb_url, str):
            if thumb_url.lower() == "stop":
                invalidate(self.bot, ctx.guild, ctx.author, name)
                return await ctx.send(
                    "Command creation cancelled and session destroyed."
                )

        if thumb_url == "":
            if len(embed_input.attachments) > 0:
                thumb_url = embed_input.attachments[0].url
                exts = [
                    "jpg",
                    "gif",
                    "png",
                    "webph",
                    "jpeg",
                    "JPEG",
                    "JPG",
                    "PNG",
                    "WEBPH",
                    "GIF",
                ]
                if thumb_url.split(".")[-1] in exts:
                    pass
                else:
                    thumb_url = None
            else:
                pass

        if isinstance(thumb_url, str):
            if thumb_url.lower() == "pass":
                thumb_url = None

        # Ask Image
        embed_step = await ctx.send(
            "What will be the image url?  `Be sure to put a valid image url. If you dont want any, type 'pass'`"
        )

        try:
            embed_input = await self.bot.wait_for("message", timeout=180, check=check)
        except:
            invalidate(self.bot, ctx.guild, ctx.author, name)
            return await ctx.send("Command creation cancelled and session destroyed.")

        image_url = embed_input.content

        if isinstance(image_url, str):
            if image_url.lower() == "stop":
                invalidate(self.bot, ctx.guild, ctx.author, name)
                return await ctx.send("Command creation cancelled.")

        if not image_url:
            if len(embed_input.attachments) > 0:
                image_url = embed_input.attachments[0].url
                exts = [
                    "jpg",
                    "gif",
                    "png",
                    "webph",
                    "jpeg",
                    "JPEG",
                    "JPG",
                    "PNG",
                    "WEBPH",
                    "GIF",
                ]
                if image_url.split(".")[-1] in exts:
                    pass
                else:
                    image_url = None
            else:
                pass
        if isinstance(image_url, str):
            if image_url.lower() == "pass":
                image_url = None

        if ctx.author.guild_permissions.manage_guild:
            isapproved = "yes"
            note = ""
        else:
            isapproved = "no"
            note = "Wait for server managers to approve this command"

        try:
            await self.bot.db.execute(
                "INSERT INTO commands(userid, guild, name, type, approved) VALUES($1, $2, $3, 'embed', $4)",
                ctx.author.id,
                ctx.guild.id,
                name,
                isapproved,
            )

            data = await get_command(self.bot, name, ctx.guild.id)

            id_ = data["id"]
            try:
                await self.bot.db.execute(
                    "INSERT INTO embed(command_id, title, description, thumbnail, image) VALUES($1, $2, $3, $4, $5)",
                    id_,
                    title,
                    description,
                    thumb_url,
                    image_url,
                )

                invalidate(self.bot, ctx.guild, ctx.author, name)
                await ctx.send(f"Command created `{name}`. {note}")

                runner = command_handler.Runner(self.bot)

                await runner.run_command(ctx, name=name, indm=False, bypass_check=False)
            except Exception as e:
                print(e)
                print("Here")
                await self.bot.db.execute("DELETE FROM commands WHERE id=$1", id_)
                invalidate(self.bot, ctx.guild, ctx.author, name)
                return await ctx.send(
                    "Error creating command. Please join the support server and report this error. <https://discord.gg/7SaE8v2>"
                )
        except:
            invalidate(self.bot, ctx.guild, ctx.author, name)
            await ctx.send(
                "Error creating command. Please join the support server and report this error. <https://discord.gg/7SaE8v2>"
            )


def setup(bot):
    bot.add_cog(Maker(bot))
