from discord.ext import commands

class Quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spreadsheet = bot.spreadsheet

    @commands.command(name='quote', help='Get a random quote from one of the book club books')
    async def get_book_quote(self, ctx, book_name):
        quote = self.spreadsheet.get_book_quote(book_name)
        if quote:
            await ctx.send(f"[{book_name}] \"{quote}\"")
        else:
            await ctx.send(f"[{book_name}] There are no quotes for this book!")

def setup(bot):
    bot.add_cog(Quotes(bot))
