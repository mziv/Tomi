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
bot.load_extension('rooms')

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

try:
    bot.run(token)
except KeyboardInterrupt:
    print("now closing!")
    raise
    
