import discord
import os
import random
from discord.ext import commands
from datetime import datetime, timezone

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekdays = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday',
                         'friday', 'saturday']
        self.min_people_for_event = 3

    @commands.Cog.listener()
    async def on_ready(self):
        data = self.bot.cache.get_data('events')
        self.tracked_msgs = {int(msg_id):user for msg_id, user in data.get('tracked_msgs', {})}

    # TODO(rachel-1): this currently doesn't work for messages sent while Tomi was down.
    @commands.Cog.listener()
    async def on_reaction_add(self, new_reaction, user):
        msg = new_reaction.message
        if msg.id in self.tracked_msgs:
            for reaction in msg.reactions:
                try:
                    emoji_name = reaction.emoji.name
                # Skip default emojis
                except AttributeError:
                    continue

                # Skip unrelated emojis
                if emoji_name not in self.weekdays: continue

                # If enough people have reacted already, ping the event organizer.
                weekday = emoji_name 
                if reaction.count > self.min_people_for_event:
                    original_user = self.bot.get_user(self.tracked_msgs[msg.id])
                    if original_user.dm_channel is None:
                        await original_user.create_dm()
                    await original_user.dm_channel.send(f"As a heads up, it looks like several people are down for coming to your event on {weekday.capitalize()} :tada:")
                    del self.tracked_msgs[msg.id]
                    return
        
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

    @commands.command(name='suggest_event', help='Assess interest and pick a time for an event.')
    async def suggest_event(self, ctx):
        msg = await ctx.send(":tada: Sounds good to me! Alright team, you know the drill: react for the days that work for you, :cry: if you're interested but busy, and :eyes: if this isn't your cup of tea (be honest!).")
        
        # TODO(rachel-1): this is a sketchy way of converting from UTC to PDT,
        # but timezones are a pain so here we are.
        today = datetime.now().weekday() + 1
        
        # Add emojis for each day of the week starting with today.
        for emoji_name in self.weekdays[today:] + self.weekdays[:today]:
            emoji = discord.utils.get(ctx.message.guild.emojis, name=emoji_name)
            await msg.add_reaction(emoji)
        # Add the cry emoji.
        await msg.add_reaction('😢')
        # Add the eyes emoji.
        await msg.add_reaction('👀')

        # Track this message to ping the author when we get some reactions.
        self.tracked_msgs[msg.id] = ctx.message.author.id

    # TODO(rachel-1): this shouldn't go here, but we'll deal with it eventually.
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

    def __del__(self):
        self.bot.cache.save_data('events', tracked_msgs=self.tracked_msgs)

def setup(bot):
    bot.add_cog(Events(bot))
