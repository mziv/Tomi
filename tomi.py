import discord
from discord.ext import commands
import json

with open('token.json') as f:
    TOKEN = json.load(f)["token"]
    
bot = commands.Bot(command_prefix='.')
bot.load_extension('timer')
bot.load_extension('questions')

@bot.event
async def on_error(event, *args, **kwargs):
    print("EVENT:", event)
        
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
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
    
bot.run(TOKEN)
