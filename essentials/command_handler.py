import discord
import asyncio
import re
from essentials.command_checks import get_command


class Runner:
    def __init__(self, bot):
        self.bot = bot

    async def get_parent_variables(self, ctx, description, attempt):
        variables = {}
        data = await self.bot.db.fetch(
            "SELECT * FROM variables WHERE guild=$1", ctx.guild.id
        )
        for row in data:
            name, value = row["name"], row["value"]
            variables[name] = value

        for old, new in variables.items():
            description = description.replace(old, new)

        return description

    async def get_dynamic_string(self, ctx, description):
        attempt = 0
        description = description
        while attempt < 5:
            if len(re.findall(r"(\{.+?\})", description)) == 0:
                break
            description = await self.get_parent_variables(ctx, description, attempt)
            attempt += 1

        variables = {
            "{user}": str(ctx.author),
            "{user_id}": str(ctx.author.id),
            "{user_avatar}": str(ctx.author.avatar_url),
            "{server}": ctx.guild.name,
            "{server_id}": str(ctx.guild.id),
            "{server_owner}": str(ctx.guild.owner),
            "{server_logo}": str(ctx.guild.icon_url),
            "{server_locale}": ctx.guild.preferred_locale,
            "{members}": str(ctx.guild.member_count),
            "{level}": str(ctx.guild.premium_tier),
            "{boosts}": str(ctx.guild.premium_subscription_count),
            "{boosters}": str(len(ctx.guild.premium_subscribers)),
            "{text_channels}": str(len(ctx.guild.text_channels)),
            "{voice_channels}": str(len(ctx.guild.voice_channels)),
            "{total_channels}": str(
                len(ctx.guild.text_channels) + len(ctx.guild.voice_channels)
            ),
            "{categories}": str(len(ctx.guild.categories)),
            "{roles}": str(len(ctx.guild.roles)),
            "{emojis}": str(len(ctx.guild.emojis)),
            "{emoji_limit}": str(ctx.guild.emoji_limit),
            "{filesize_limit}": str((ctx.guild.filesize_limit / (1024 * 1024))) + " MB",
        }

        data = await self.bot.db.fetch(
            "SELECT * FROM variables WHERE guild=$1", ctx.guild.id
        )
        for row in data:
            name, value = row["name"], row["value"]
            variables[name] = value

        for old, new in variables.items():
            description = description.replace(old, new)

        return description

    async def run_command(self, ctx, name: str, indm: bool = True, bypass_check=False):
        # Check if command exists
        command = await get_command(ctx.bot, name, ctx.guild.id)

        if not command:
            return

        self.bot.custom_command_ran += 1

        if command["approved"] == "no" and (
            ctx.author.guild_permissions.manage_guild == False and bypass_check == False
        ):
            return await ctx.channel.send(
                "This command is not approved by any server manager. Wait untill they approve."
            )

        cmd_type = command["type"]
        cmd_id = command["id"]
        cmd_name = command["name"]
        cmd_status = command["approved"]

        if cmd_type == "embed":
            data = await self.bot.db.fetchrow(
                "SELECT * FROM embed WHERE command_id=$1", cmd_id
            )

            title = await self.get_dynamic_string(ctx, data["title"])
            if len(title) >= 256:
                await ctx.send("This embed's title is larger than 256 character cant execute. Please edit the command or delete this and make a new one")
            description = await self.get_dynamic_string(ctx,  data["description"])

            if thumbnail := data["thumbnail"]:
                thumbnail = await self.get_dynamic_string(ctx, data["thumbnail"])

            if image := data["image"]:
                image = await self.get_dynamic_string(ctx, data["image"])

            description = await self.get_dynamic_string(ctx, description)

            embed = discord.Embed(
                title=title,
                description=discord.utils.escape_mentions(description),
                color=discord.Color.blurple(),
            )

            pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
            try:
                thumb = re.findall(pattern, thumbnail)

                if len(thumb) > 0:
                    try:
                        embed.set_thumbnail(url=thumb[0][0])
                    except:
                        pass
            except:
                pass

            try:
                img = re.findall(pattern, image)
                if len(img) > 0:
                    try:
                        embed.set_image(url=img[0][0])
                    except:
                        pass
            except:
                pass

            if cmd_status == "no":
                await ctx.send(embed=embed)
                await ctx.send(
                    f"This command is not approved. Use `{ctx.prefix}approve {cmd_name}` to approve this command. Or `{ctx.prefix}delete {cmd_name}` to delete."
                )
            else:
                await ctx.send(embed=embed)

        if cmd_type == "text":
            data = await self.bot.db.fetchrow(
                "SELECT * FROM text WHERE command_id=$1", cmd_id
            )
            description = data["content"]
            msg = await self.get_dynamic_string(ctx, description)

            if cmd_status == "no":
                await ctx.send(msg)
                await ctx.send(
                    f"This command is not approved. Use `{ctx.prefix}approve {cmd_name}` to approve this command. Or `{ctx.prefix}delete {cmd_name}` to delete."
                )
            else:
                await ctx.send(msg)

        if cmd_type == "role":
            data = await self.bot.db.fetchrow(
                "SELECT * FROM role WHERE command_id=$1", cmd_id
            )

            roles = data["role"]
            action = data["action"]
            for r in roles:
                role = ctx.guild.get_role(r)
                if role is not None:
                    if action == "give":
                        try:
                            await ctx.author.add_roles(role)
                        except Exception as e:
                            print(e)

                    if action == "take":
                        try:
                            await ctx.author.remove_roles(role)
                        except:
                            pass

                    if action == "toggle":
                        if role not in ctx.author.roles:
                            try:
                                await ctx.author.add_roles(role)
                            except Exception as e:
                                pass

                        else:
                            try:
                                await ctx.author.remove_roles(role)
                            except Exception as e:
                                pass
                    await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
                    await asyncio.sleep(3)
                    await ctx.message.delete()

        if cmd_type == "mrl":
            data = await self.bot.db.fetchrow(
                "SELECT * FROM multirole WHERE command_id=$1", cmd_id
            )

            gives = data['gives']
            removes = data['removes']

            for r in gives:
                role = ctx.guild.get_role(r)
                if role is not None:
                    try:
                        await ctx.author.add_roles(role)
                    except:
                        pass

            for r in removes:
                role = ctx.guild.get_role(r)
                if role is not None:
                    try:
                        await ctx.author.remove_roles(role)
                    except:
                        pass

            await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
            await asyncio.sleep(3)
            await ctx.message.delete()
