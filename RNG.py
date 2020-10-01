import discord
from discord.ext import commands
from random import randint

class RNG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='d20', help='Roll a D20!')
    async def d20(self, ctx):
        await ctx.send(f"{ctx.author.name} rolled a: {randint(1,20)}.")


    @commands.command(name='d6', help='Roll a D6!')
    async def d6(self, ctx):
        await ctx.send(f"{ctx.author.name} rolled a: {randint(1,6)}.")


def setup(bot):
    bot.add_cog(RNG(bot))
