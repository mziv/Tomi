import os

import discord
from discord.ext import commands
import json
import asyncio
from datetime import datetime

with open('token.json') as f:
    TOKEN = json.load(f)["token"]
    
bot = commands.Bot(command_prefix='.')

timer_dict = {}
current_idx = 0

@bot.command(name='start', help='Start a timer')
async def start_timer(ctx, num_min: int):
    global current_idx
    current_idx = (current_idx + 1) % 10
    if current_idx in timer_dict:
        await ctx.send("Unfortunately, you're out of timers and out of luck. Timers are scarce these days.")
        return

    response = "Starting timer {} for {} min...".format(current_idx, num_min)
    await ctx.send(response)

    timer_dict[current_idx] = dict(start_time=datetime.now(),
                                   duration=num_min)
    
    async def timer(idx):
        await asyncio.sleep(60*num_min)
        if idx in timer_dict:
            await ctx.send(f"Timer {idx} finished!")
            del timer_dict[idx]
    
    bot.loop.create_task(timer(current_idx))

@bot.command(name='check', help='Check how long is left on the timer')
async def check_timer(ctx, idx: int):
    if idx in timer_dict:
        time_remaining = timer_dict[idx]['duration'] - (datetime.now() - timer_dict[idx]['start_time']).seconds//60 - 1
        await ctx.send(f"{time_remaining} minutes left!")
    else:
        await ctx.send(f"Timer {idx} isn't running.")

@bot.event
async def on_error(event, *args, **kwargs):
    print("EVENT:", event)
    
@bot.command(name='cancel', help='Cancel a given timer')
async def cancel_timer(ctx, idx: int):
    if not idx in timer_dict:
        await ctx.send('That timer and I? We\'ve never met.')
        return
    del timer_dict[idx]
    await ctx.send(f"Timer {idx} cancelled!")
    
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
