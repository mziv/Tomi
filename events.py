from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='end_event', help='Politely usher non-resident users out the door.')
    async def end_event(self, ctx):
        pass
        
def setup(bot):
    bot.add_cog(Events(bot))
