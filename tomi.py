import discord
import logging
from discord.ext import commands
import os
import json
from spreadsheet import Spreadsheet
from members import autoplay_playlist_helper
import traceback
import argparse
import time

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

with open(token_path) as f:
    token = json.load(f)['token']
os.environ['TOMI_MODE'] = 'production' if args.production else 'test'
logging.info(f"Tomi is now running in {os.getenv('TOMI_MODE')} mode!")

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='.', intents=intents)
bot.spreadsheet = Spreadsheet()
bot.invite_cache = {}
bot.resident_invites = set()
bot.load_extension('timer')
bot.load_extension('questions')
bot.load_extension('quotes')
bot.load_extension('feedback')
bot.load_extension('RNG')
bot.load_extension('members')
bot.load_extension('events')

@bot.event
async def on_error(event, *args, **kwargs):
    logging.error(traceback.format_exc())

@bot.event
async def on_member_join(member):
    await member.create_dm()

    # Check which invite code has gone up in uses since we last cached.
    async def get_invite_code_for_user():
        invites_after = await member.guild.invites()
        if member.guild.id not in bot.invite_cache:
            logging.error("Invite code not found for user!")
            logging.info("Invite cache: ", bot.invite_cache)
            logging.info("Current invites: ", invites_after)
            return None
        for invite in invites_after:
            cached_invite = bot.invite_cache[member.guild.id].get(invite.code)
            if cached_invite is not None and invite.uses > cached_invite.uses:
                return invite.code
            
        return None

    resident_msg = "Welcome to the co-op! You're now a permanent resident, so go ahead and check out the #welcome channel to get all the info you need to get settled in."

    visitor_msg = "Welcome to the co-op! We're excited for your visit :) You're welcome to poke around until your host ends the day's event. If you're interested in living with us, just ask your host about it and they can tell you more."
    
    # If this user was invited permanently, go ahead and make them a resident.
    used_invite_code = await get_invite_code_for_user()
    logging.info(f"{member.name} has joined with {used_invite_code}")
    
    for user, invite_code in bot.resident_invites:
        # Check if this invite code was one of the ones meant for residents.
        if used_invite_code == invite_code:
            logging.info("The invite code is for residents")
            # Delete invite now that it isn't needed (and update cache)
            bot.resident_invites.remove((user, invite_code))
            await bot.invite_cache[member.guild.id][invite_code].delete()
            bot.invite_cache[member.guild.id] = {}
            invites = await member.guild.invites()
            for invite in invites:
                bot.invite_cache[member.guild.id][invite.code] = invite

            # Give user the resident role and welcome them appropriately.
            role = discord.utils.get(member.guild.roles, name="resident")
            await member.add_roles(role)
            await member.dm_channel.send(resident_msg)
            
            # Track who invited the user.
            bot.spreadsheet.add_invitee(user, member)
            return

    # Send just the visitor message if the user shouldn't become a resident.
    await member.dm_channel.send(visitor_msg)

@bot.event
async def on_ready():
    logging.info(f'{bot.user} has connected to Discord!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('This command requires an argument.')
    else:
        logging.error(traceback.format_exc())

@bot.event
async def on_voice_state_update(member, prev, cur):
    '''
    # Entering a voice channel.
    if cur.channel is not None:

        # Leaving a voice
        else:
            
        
    
    server = cur.channel.guild if cur.channel else prev.channel.guild

    await guild.create_role(name="role name")
    
    if 
    
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }

    await server.create_text_channel(cur.channel.name)
    '''
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
        
bot.run(token)
