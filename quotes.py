from discord.ext import commands

class Quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.command(name='quote', help='Get a random quote from one of the book club books')
    async def get_book_quote(ctx):
        pass

def setup(bot):
    bot.add_cog(Quotes(bot))
