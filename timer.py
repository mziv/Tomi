from discord.ext import commands
from datetime import datetime, timedelta
import asyncio

class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.max_num_timers = 10

    @commands.Cog.listener()
    async def on_ready(self):
        data = self.bot.cache.get_data('timer')
        self.timer_dict = {}
        for idx, end_date in data.get('timer_dict', {}).items():
            delta = end_date - datetime.now()
            # If this timer is still valid, queue the callback and add to dict.
            if delta.total_seconds() > 0:
                num_min = delta.seconds//60
                self.bot.loop.create_task(self.timer_alert(idx, num_min))
                self.timer_dict[idx] = end_date

        self.current_idx = 0

    async def timer_alert(self, channel_id, idx, num_min):
        await asyncio.sleep(60*num_min)
        if idx in self.timer_dict:
            channel = self.bot.get_channel(channel_id)
            await channel.send(f"Timer {idx} finished!")
            del self.timer_dict[idx]
    
    @commands.command(name='start', help='Start a timer')
    async def start_timer(self, ctx, num_min: int):
        # Look for unused timer index.
        old_idx = self.current_idx
        while self.current_idx in self.timer_dict:
            self.current_idx = (self.current_idx + 1) % self.max_num_timers
            if self.current_idx == old_idx:
                await ctx.send("Unfortunately, you're out of timers and out of luck. Timers are scarce these days.")
                return
        
        response = "Starting timer {} for {} min...".format(self.current_idx, num_min)
        await ctx.send(response)
        
        # Map the index of the timer to its end time.
        self.timer_dict[self.current_idx] = datetime.now() + timedelta(seconds=num_min*60)

        self.bot.loop.create_task(self.timer_alert(ctx.channel.id, self.current_idx, num_min))

    @commands.command(name='check', help='Check how long is left on the timer')
    async def check_timer(self, ctx, idx: int):
        if idx in self.timer_dict:
            num_seconds = (self.timer_dict[idx] - datetime.now()).seconds
            num_minutes = num_seconds//60
            if num_minutes < 2:
                msg = f"{num_seconds} seconds left!"
            else:
                msg = f"{num_minutes} minutes left!"
            await ctx.send(msg)
        else:
            await ctx.send(f"Timer {idx} isn't running.")

    @commands.command(name='cancel', help='Cancel a given timer')
    async def cancel_timer(self, ctx, idx: int):
        if not idx in self.timer_dict:
            await ctx.send('That timer and I? We\'ve never met.')
            return
        del self.timer_dict[idx]
        await ctx.send(f"Timer {idx} cancelled!")

    def __del__(self):
        # Cache timers that have yet to go off.
        self.bot.cache.save_data('timer',
                        timer_dict=self.timer_dict)

def setup(bot):
    bot.add_cog(Timer(bot))
