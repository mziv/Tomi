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
    response = "Starting timer {} for {} min...".format(current_idx, num_min)
    await ctx.send(response)

    timer_dict[current_idx] = dict(should_notify=True,
                                   start_time=datetime.now(),
                                   duration=num_min)
    
    async def timer(idx):
        await asyncio.sleep(60*num_min)
        if timer_dict[idx]['should_notify']:
            await ctx.send(f"Timer {current_idx} finished!")
        del timer_dict[idx]
    
    bot.loop.create_task(timer(current_idx))

@bot.command(name='check', help='Check how long is left on the timer')
async def check_timer(ctx, idx: int):
    if timer_dict[idx]['should_notify']:
        time_remaining = timer_dict[idx]['duration'] - (datetime.now() - timer_dict[idx]['start_time']).seconds//60 - 1
        await ctx.send(f"{time_remaining} minutes left!")
    else:
        await ctx.send(f"Timer {idx} was cancelled.")

@bot.event
async def on_error(event, *args, **kwargs):
    print("EVENT:", event)
    
@bot.command(name='cancel', help='Cancel a given timer')
async def cancel_timer(ctx, idx: int):
    timer_dict[idx]['should_notify'] = False
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
    
bot.run(TOKEN)
