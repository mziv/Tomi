from discord.ext import commands
from datetime import datetime

COUNCIL_CHANNEL_ID = 711280196308697120

class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.out_channel = COUNCIL_CHANNEL_ID # By default, start as the-council. Yes, I know this is bad style.

    @commands.command(name='feedback', help='Send anonymous feedback to the council. Make sure to enclose your message in "".')
    async def send_feedback(self, ctx, msg):
        if msg == None or len(msg) == 0:
            await ctx.send("Please include a message after this command.")
            return

        if self.out_channel == None:
            await ctx.send("I'm sorry, the feedback channel isn't configured yet.")
            return

        channel = self.bot.get_channel(self.out_channel)
        await channel.send(f'Anonymous message: "{msg}"')
        await ctx.send(f'Sent "{msg}" to the feedback channel.')

    @commands.command(name='setfeedback', help='Configure which channel will be receiving feedback.')
    @commands.has_role('admin')
    async def set_feedback(self, ctx, channel):
        no_pound = int(channel[2:-1])
        self.out_channel = no_pound
        await ctx.send("Feedback channel set to " + self.out_channel.name + ".")

def setup(bot):
    bot.add_cog(Feedback(bot))