from discord.ext import commands
from datetime import datetime

class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timer_dict = {}
        self.current_idx = 0

    @commands.command(name='start', help='Start a timer')
    async def start_timer(self, ctx, num_min: int):
        self.current_idx = (self.current_idx + 1) % 10
        if self.current_idx in self.timer_dict:
            await ctx.send("Unfortunately, you're out of timers and out of luck. Timers are scarce these days.")
            return

        response = "Starting timer {} for {} min...".format(self.current_idx, num_min)
        await ctx.send(response)

        timer_dict[self.current_idx] = dict(start_time=datetime.now(),
                                            duration=num_min)

        async def timer(idx):
            await asyncio.sleep(60*num_min)
            if idx in timer_dict:
                await ctx.send(f"Timer {idx} finished!")
                del timer_dict[idx]

        self.bot.loop.create_task(timer(self.current_idx))

    @commands.command(name='check', help='Check how long is left on the timer')
    async def check_timer(ctx, idx: int):
        if idx in self.timer_dict:
            time_remaining = self.timer_dict[idx]['duration'] - (datetime.now() - timer_dict[idx]['start_time']).seconds//60 - 1
            await ctx.send(f"{time_remaining} minutes left!")
        else:
            await ctx.send(f"Timer {idx} isn't running.")

    @commands.command(name='cancel', help='Cancel a given timer')
    async def cancel_timer(ctx, idx: int):
        if not idx in self.timer_dict:
            await ctx.send('That timer and I? We\'ve never met.')
            return
        del self.timer_dict[idx]
        await ctx.send(f"Timer {idx} cancelled!")

def setup(bot):
    bot.add_cog(Timer(bot))
