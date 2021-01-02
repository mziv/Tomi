import discord
import os
import random
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



    @commands.command(name='dog', help='Mia the co-op dog.')
    async def dog(self, ctx, dog_command: str):
        if dog_command == "picture":
            mia_pic_dir = os.path.join(os.path.dirname(__file__), "Mia_pictures")
            mia_pic_list = [os.path.join(mia_pic_dir, m) for m in os.listdir(mia_pic_dir)]
            await ctx.send(file=discord.File((random.choice(mia_pic_list))))
        elif dog_command == "video":
            mia_vid_dir = os.path.join(os.path.dirname(__file__), "Mia_videos")
            mia_vid_list = [os.path.join(mia_vid_dir, m) for m in os.listdir(mia_vid_dir)]
            await ctx.send(file=discord.File((random.choice(mia_vid_list))))
        elif dog_command == "help":
            await ctx.send('"picture" displays a random picture of Mia.\n"video" displays a random video of Mia.\n".dog help" displays this help message.')
        else:
            await ctx.send('Command not recognized. Please enter valid command. Enter ".dog help" for help message.')

def setup(bot):
    bot.add_cog(Events(bot))
