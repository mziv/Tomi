from discord.ext import commands

class Questions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spreadsheet = bot.spreadsheet

    @commands.command(name='ask', help='Generate a question with the given spiciness (1=bland, 5=spicy)')
    async def ask_question(self, ctx, spiciness: int):
        if spiciness < 1 or spiciness > 5:
            await ctx.send(f"Spiciness '{spiciness}' is out of range!!")
            return
        question, spiciness = self.spreadsheet.get_question(spiciness)
        await ctx.send(f"[{spiciness}] {question}")

    @commands.command(name='add_question',
                 help='Submit a question along with its spice level (1=bland, 5=spicy)')
    async def add_question(self, ctx, question: str, spiciness: int):
        if spiciness < 1 or spiciness > 5:
            await ctx.send('Spiciness should be in the range 1-5!')
            return

        success = self.spreadsheet.add_question(ctx.author, question, spiciness)
        if not success:
            await ctx.send("There was an error adding the question...")
    
def setup(bot):
    bot.add_cog(Questions(bot))
