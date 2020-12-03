import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from spreadsheet import Spreadsheet

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

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

@bot.event
async def on_error(event, *args, **kwargs):
    print("EVENT:", event)

@bot.event
async def on_member_join(member):
    await member.create_dm()

    # Check which invite code has gone up in uses since we last cached.
    async def get_invite_code_for_user():
        invites_after = await member.guild.invites()
        for invite in invites_after:
            cached_invite = bot.invite_cache[member.guild.id].get(invite.code)
            if cached_invite is not None and invite.uses > cached_invite.uses:
                return invite.code
            
        return None

    resident_msg = "Welcome to the co-op! You're now a permanent resident, so go ahead and check out the #welcome channel to get all the info you need to get settled in."

    visitor_msg = "Welcome to the co-op! We're excited for your visit :) You're welcome to poke around until your host ends the day's event. If you're interested in living with us, just ask your host about it and they can tell you more."
    
    # If this user was invited permanently, go ahead and make them a resident.
    used_invite_code = await get_invite_code_for_user()
    for user, invite_code in bot.resident_invites:

        # Check if this invite code was one of the ones meant for residents.
        if used_invite_code == invite_code:
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
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('This command requires an argument.')
    else: 
        print(error)
    
bot.run(TOKEN)
