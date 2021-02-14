import discord
import asyncio
import os
from discord.ext import commands

class Rooms(commands.Cog):
    """
    All things related to entering/joining rooms of the house.
    """

    def __init__(self, bot):
        self.bot = bot
        # Create a shared lock to protect code which cannot run concurrently.
        self.lock = asyncio.Lock()

        # TODO(rachel0): allow picking a channel name to use for publishing log
        # of people entering voice channels.

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, prev, cur):
        # If this is some update other than entering/leaving a channel, ignore it.
        if cur.channel and prev.channel and cur.channel.id == prev.channel.id:
            return

        # Lock this region so multiple members joining a channel at once can't
        # trigger concurrent on_voice_state_update handlers and mess up the state.
        async with self.lock:
            guild = cur.channel.guild if cur.channel else prev.channel.guild

            # Possibly entering a voice channel.
            if cur.channel is not None:
                # Set up a private text channel for this voice channel if it doesn't exist already.
                role = discord.utils.get(guild.roles, name=cur.channel.name)
                if role is None:
                    role = await guild.create_role(name=cur.channel.name)
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        role: discord.PermissionOverwrite(read_messages=True)
                    }
                    channel_name = cur.channel.name.lower()
                    print(f"Creating text channel {channel_name}")
                    channel = await guild.create_text_channel(channel_name, overwrites=overwrites,
                                                              category=cur.channel.category,
                                                              position=cur.channel.position)

                    print(f"Adding {member.display_name} to {role.name}")
                    await member.add_roles(role)
                    comms_channel = discord.utils.get(guild.channels, name="comms")
                    if comms_channel is not None:
                        await comms_channel.send(f"{member.display_name} has joined the {channel_name}!")

                    jpg_image_path = os.path.join('images', f"{channel_name}.jpg")
                    png_image_path = os.path.join('images', f"{channel_name}.png")
                    if os.path.isfile(jpg_image_path):
                        await channel.send(f"Welcome to the {channel_name}!",
                                           file=discord.File(jpg_image_path))
                    elif os.path.isfile(png_image_path):
                        await channel.send(f"Welcome to the {channel_name}!",
                                           file=discord.File(png_image_path))
                    else:
                        await channel.send(f"Welcome to the {channel_name}! There isn't a picture to show, since this room is still under construction. Please send suggestions in the #renovations channel!")
                # Role already existed, but the user is newly joining the channel.
                elif role not in member.roles:
                    print(f"Adding {member.display_name} to {role.name}")
                    await member.add_roles(role)
                    await channel.send(f"Hi {member.display_name}!")
                    comms_channel = discord.utils.get(guild.channels, name="comms")
                    if comms_channel is not None:
                        await comms_channel.send(f"{member.display_name} has joined the {cur.channel.name.lower()}!")
                # The user defeaned, turned on their video or otherwise triggered
                # this event without actually leaving/joining a channel
                else:
                    logger.error(f"{member} already has role {role}")

            # Possibly leaving a voice channel.
            if prev.channel is not None:
                role = discord.utils.get(guild.roles, name=prev.channel.name)

                # Do error checking, you know, just in case.
                if role is None:
                    logger.error(f"{prev.channel.name} is not a role!")
                    return
                if role not in member.roles:
                    logger.error(f"{member} does not have role '{role}'!")
                    return

                await member.remove_roles(role)
                print(f"Removing {member.display_name} from {role.name}")

                # We're the last one out, so turn off the lights.
                if len(prev.channel.members) == 0:
                    await role.delete()
                    text_channel = discord.utils.get(guild.text_channels, name=prev.channel.name.lower())
                    print(f"Deleting text channel {prev.channel.name.lower()}")
                    await text_channel.delete()

'''
### Note: does not work right now. Supposed to auto-play playlist if user enters the library, has a playlist registered, and has auto-play on
#if cur.channel.name != "Library" or prev.channel.name == "Library":
#return

for guild in bot.guilds:
    if guild.name == "Bot Testing Server":
        # Temp channel
        text_channel = bot.get_channel(752221173546221598)
        print("asdf")
        ### this part does not work!
        print(guild.voiceConnection)
        print("fdsa")
        await autoplay_playlist_helper(text_channel, cur.channel, member, guild.voiceConnection)
        return

    elif guild.name == "The Co-op":
        # Library
        text_channel = bot.get_channel(708882378877173811) 
        await autoplay_playlist_helper(text_channel, cur.channel, member, guild.voiceConnection)
        return
'''

def setup(bot):
    bot.add_cog(Rooms(bot))
