from discord.ext import tasks, commands
from datetime import datetime


class KeyCheck(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check_exp.start()

    async def doit(self):
        # print("Checking for expired keys")
        guild = None
        res = await self.client.db.fetch("SELECT * FROM keys")

        for result in res:
            todate = result["valid_till"]

            today = datetime.today()

            if today >= todate:
                # print("Broken key")
                key = result["key"]

                await self.client.db.fetchrow(f"DELETE FROM keys WHERE key=$1", key)

                try:
                    guild = self.client.get_guild(result["guild"])
                except:
                    pass

                if guild is not None:
                    try:
                        await guild.owner.send(
                            "Your key is expired. Buy a new one to continue premium membership."
                        )
                    except:
                        pass
            else:
                pass

    @tasks.loop(minutes=30)
    async def check_exp(self):
        await self.doit()


def setup(client):
    client.add_cog(KeyCheck(client))
