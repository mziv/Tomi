import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='end_event', help='Politely usher non-resident users out the door.')
    async def end_event(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name="resident")
        guests = []
        for member in ctx.guild.members:
            if role not in member.roles:
                guests.append(member)

        if len(guests) == 0:
            await ctx.send(f"Everyone here is a resident!")
        else:
            await ctx.send("Bye everyone! Come again soon!")
            guest_names = []
            for guest in guests:
                if guest.dm_channel is None:
                    await guest.create_dm()
                await guest.dm_channel.send("Thanks for visiting The Co-Op!")
                await guest.kick(reason="end_of_event")
                guest_names.append(guest.name)
            await ctx.send(f"Our guest(s) ({','.join(guest_names)}) have been shown out.")
        
def setup(bot):
    bot.add_cog(Events(bot))
