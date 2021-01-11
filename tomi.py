import discord
import logging
from discord.ext import commands
import os, sys
import json
from spreadsheet import Spreadsheet
from cache import Cache
from members import autoplay_playlist_helper
import traceback
import argparse
import time
import asyncio

# Save log data to a file and print to console.
if not os.path.isdir('logs'): os.mkdir('logs')
log_path = os.path.join('logs', time.strftime("%Y%m%d-%H%M%S")+'.log')
logging.basicConfig(filename=log_path, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

# To get these files, please download them from the Drive.
production_token_path = 'tomi_production_token.json'
test_token_path = 'tomi_test_token.json'

# Determine if we want to run Tomi (production) or TestTomi (test).
parser = argparse.ArgumentParser()
parser.add_argument('--production', action='store_true', default=False)
args = parser.parse_args()
token_path = production_token_path if args.production else test_token_path

# Load the appropriate token, if possible.
if not os.path.isfile(token_path):
    raise Exception(f"{token_path} not found!")

# Run in the given mode.
with open(token_path) as f:
    token = json.load(f)['token']
logging.info(f"Now running in {'production' if args.production else 'test'} mode!")

# Create a bot subscribed to all possible events.
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)
bot.is_production = args.production

# Store the objects common across cogs. Note that this can't themselves be cogs
# since they may be needed in __del__ of individual cogs.
bot.spreadsheet = Spreadsheet(args.production)
bot.cache = Cache(args.production)

# Load custom modules. For example, timer.py holds timer-related functionality.
bot.load_extension('timer')
bot.load_extension('questions')
bot.load_extension('quotes')
bot.load_extension('feedback')
bot.load_extension('RNG')
bot.load_extension('members')
bot.load_extension('events')

# Create a shared lock to protect code which cannot run concurrently.
lock = asyncio.Lock()

@bot.event
async def on_error(event, *args, **kwargs):
    print("on_error")
    logging.error(traceback.format_exc())

@bot.event
async def on_ready():
    logging.info(f'{bot.user} has connected to Discord!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('This command requires an argument.')
    else:
        print("on_command_error")
        logging.error(traceback.format_exc())
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

@bot.event
async def on_voice_state_update(member, prev, cur):
    guild = cur.channel.guild if cur.channel else prev.channel.guild

    # Lock this region or multiple members joining a channel at once can't
    # trigger concurrent on_voice_state_update handlers and mess up the state.
    async with lock:
        # Entering a voice channel.
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
                
                image_path = os.path.join('images', f"{channel_name}.jpg")
                if os.path.isfile(image_path):
                    await channel.send(f"Welcome to the {channel_name}!",
                                       file=discord.File('test.jpg'))
                else:
                    await channel.send(f"Welcome to the {channel_name}! There isn't a picture to show, since this room is still under construction. Please send suggestions in the #renovations channel!")
                    
            print(f"Adding {member.display_name} to {role.name}")
            await member.add_roles(role)

        # Leaving a voice channel.
        if prev.channel is not None:
            role = discord.utils.get(guild.roles, name=prev.channel.name)
            await member.remove_roles(role)
            print(f"Removing {member.display_name} from {role.name}")

            # We're the last one out, so turn off the lights.
            if len(prev.channel.members) == 0:
                await role.delete()
                text_channel = discord.utils.get(guild.text_channels, name=prev.channel.name.lower())
                print(f"Deleting text channel {prev.channel.name.lower()}")
                await text_channel.delete()

    ### Note: does not work right now. Supposed to auto-play playlist if user enters the library, has a playlist registered, and has auto-play on
    return
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

try:
    bot.run(token)
except KeyboardInterrupt:
    print("now closing!")
    raise
    
