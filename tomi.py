import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from spreadsheet import Spreadsheet
from members import autoplay_playlist_helper

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
    
bot = commands.Bot(command_prefix='.')
bot.spreadsheet = Spreadsheet()
bot.load_extension('timer')
bot.load_extension('questions')
bot.load_extension('quotes')
bot.load_extension('feedback')
bot.load_extension('RNG')
bot.load_extension('members')

@bot.event
async def on_error(event, *args, **kwargs):
    print("EVENT:", event)

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the co-op! Please make sure to set your nickname by right-clicking your name in the online list in the server and clicking "Change Nickname".'
    )

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('This command requires an argument.')
    else: 
        print(error)


@bot.event
async def on_voice_state_update(member, prev, cur):
    ### Note: does not work right now. Supposed to auto-play playlist if user enters the library, has a playlist registered, and has auto-play on
    if cur.channel.name != "Library" or prev.channel.name == "Library":
        return

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
        
bot.run(TOKEN)
