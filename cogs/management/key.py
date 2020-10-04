from discord.ext import commands
from random import randint
import datetime
from timetils import Formatter


class ClientAdmin(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def check_avail(self, key: str):
        res = await self.client.db.fetchrow("SELECT * FROM keys WHERE key=$1", key)

        if res:
            return True
        else:
            return False

    async def chek_used(self, key: str):
        res = await self.client.db.fetchrow(
            "SELECT guild FROM keys WHERE key = $1",
            key
        )
        if res["guild"] == 0:
            return False
        else:
            return True

    async def do_reg(self, key: str, guildid: int, delta=None):
        try:
            try:
                await self.client.db.execute(
                    "DELETE FROM keys WHERE guild = $1", guildid
                )
            except:
                pass
            if delta:
                res = await self.client.db.fetchrow(
                    "SELECT * FROM keys WHERE key = $1", key
                )
                valid_till = res["valid_till"] + delta
                await self.client.db.execute(
                    f"UPDATE keys SET guild= $1, valid_till = $2 WHERE key= $3",
                    guildid,
                    valid_till,
                    key,
                )
            else:
                await self.client.db.execute(
                    f"UPDATE keys SET guild = $1 WHERE key= $2", guildid, key
                )
            return True
        except:
            return False

    @staticmethod
    def generate_key():
        datas = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
        key = ""
        while len(key) < 12:
            key += datas[randint(0, len(datas) - 1)]
        return key

    @commands.command(hidden=True)
    @commands.is_owner()
    async def generate(self, ctx, xtime: int = 30, dmy: str = "D"):
        key = self.generate_key()
        todays_date = datetime.datetime.now()
        expire_date = None

        if dmy == "D":
            expire_date = todays_date + datetime.timedelta(days=xtime)

        if dmy == "M":
            expire_date = todays_date + datetime.timedelta(days=xtime * 30)

        if dmy == "Y":
            expire_date = todays_date + datetime.timedelta(days=xtime * 365)

        if dmy == "m":
            expire_date = todays_date + datetime.timedelta(minutes=xtime)

        if dmy == "h":
            expire_date = todays_date + datetime.timedelta(hours=xtime)

        await self.client.db.execute(
            "INSERT INTO keys(key, guild, created_at, valid_till) VALUES($1, $2, $3, $4)",
            key,
            0,
            todays_date,
            expire_date,
        )

        await ctx.send(f"Key Generated : `{key}` for {xtime}{dmy}")
        await ctx.send(f"```{key}```")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def register(self, ctx, key: str):
        isavailable = await self.check_avail(key)
        res = await self.client.db.fetchrow(
            "SELECT * FROM keys WHERE guild = $1", ctx.guild.id
        )

        if isavailable:
            isused = await self.chek_used(key)
            if isused:
                await ctx.send("Key is already in use")
            else:
                if res:
                    valid_till = res["valid_till"]
                    delta = valid_till - datetime.datetime.now()
                else:
                    delta = None
                suc = await self.do_reg(key, ctx.guild.id, delta)
                if suc:
                    if delta:
                        msg = "This server's premium membership extended 🎉"
                    else:
                        msg = "This sever is now premium  🎉"
                    await ctx.send(msg)
                else:
                    await ctx.send("Something went wrong.")
        else:
            await ctx.send("Key is wrong")

    @commands.command(invoke_without_command=True)
    async def premium(self, ctx):
        """Check if server is premium or not"""
        result = await self.client.db.fetchrow(
            "SELECT * FROM keys WHERE guild = $1", ctx.guild.id
        )
        if result:
            now = datetime.datetime.now()
            delta = result['valid_till'] - now
            remain = Formatter().natural_delta(delta, as_string=True)
            return await ctx.send("This server enjoying __Premium__. 🎉"
                                  f"\n**Remaining :** {remain}")
        else:
            return await ctx.send(
                "This server is not subscribed to premium. Join the official server to get premium."
            )


def setup(client):
    client.add_cog(ClientAdmin(client))
