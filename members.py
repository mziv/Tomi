from discord.ext import commands
import discord
import pandas as pd 
import os.path
import asyncio


if not os.path.exists("./memberInfo.csv"):
    d = {'Nickname':[], 'Email': [], 'Venmo': []};
    df = pd.DataFrame(data=d)
    # In .gitignore
    df.to_csv("./memberInfo.csv", index=False)


SERVER_ID = 744657737027158166
    
class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.df = pd.read_csv("./memberInfo.csv", index_col='Nickname')
        self.invite_delay_hours = 24
        self.live_invites = set()

    @commands.command(name='cancel_invite', help='Cancel an invite, preventing a link from being generated.')        
    async def cancel_invite(self, ctx, *args):
        user_name = ' '.join(args)
        try:
            self.live_invites.remove(user_name)
        except KeyError:
            await ctx.send(f"'{user_name}' was not being invited. Maybe the spelling/capitalization is off?")
        else:    
            await ctx.send(f"{user_name} is no longer being invited.")
        
    @commands.command(name='invite', help='Propose inviting a certain person')        
    async def invite(self, ctx, *args):
        """
        Start the invite process for a certain person. This starts a timer of invite_delay_hours, then after the
        timer is up, generates a custom link to send to the person who called this command.
        usage: .invite Anna Zeng
        """
        user_name = ' '.join(args)

        # Trigger the comment period for a given proposed invite.
        await ctx.send(f"The invite process for {user_name} has begun! You now have {self.invite_delay_hours} hours to use .feedback to anonymously veto the person for any reason before they are automatically invited as a permanent resident.")
        self.live_invites.add(user_name)

        # Wait the appropriate number of hours.
        await asyncio.sleep(60*60*self.invite_delay_hours)

        # If the invite has been cancelled, don't do anything.
        if user_name not in self.live_invites: return

        # Since the invite wasn't cancelled, go ahead and generate an invite link.
        channel = discord.utils.get(ctx.guild.channels, name='welcome')
        custom_link = await channel.create_invite(unique=True)
        await ctx.send(f"I'm now inviting {user_name}! <@{ctx.author.id}>, I'll be sending you a custom link to forward to {user_name}")
        await ctx.author.send(f"Here is the link for inviting {user_name}!: {custom_link}")
        self.live_invites.remove(user_name)

        # Cache invite information for role assignment logic when the new member joins.
        self.bot.resident_invites.add((ctx.author, custom_link.code))
        self.bot.invite_cache[ctx.guild.id] = {}
        invites = await ctx.guild.invites()
        for invite in invites:
            self.bot.invite_cache[ctx.guild.id][invite.code] = invite

        
    ## Note: if we have duplicate nicknames this will be bad lol
    @commands.command(name='set_email', help='Lets Tomi know what your email is! Use: set_email bob@gmail.com')
    async def set_email(self, ctx, email):
        await self.set_val(ctx, "Email", email)


    @commands.command(name='get_email',
                 help='Gets email for a member. Use: get_email for yourself, get_email bob for bob')
    async def get_email(self, ctx, *args):
        if len(args) == 0:
            await self.get_val(ctx, "Email", ctx.author.name)
        else:
            await self.get_val(ctx, "Email", args[0])
        

    @commands.command(name='set_venmo', help='Lets Tomi know what your venmo is! Use: set_venmo bob3')
    async def set_venmo(self, ctx, venmo):
        await self.set_val(ctx, "Venmo", venmo)


    @commands.command(name='get_venmo',
                 help='Gets venmo for a member. Use: get_venmo for yourself, get_venmo bob for bob')
    async def get_venmo(self, ctx, *args):
        if (len(args) == 0):
            await self.get_val(ctx, "Venmo", ctx.author.name)
        else:
            await self.get_val(ctx, "Venmo", args[0])
    

    async def get_val(self, ctx, field, name):
        if name in self.df.index:
            val = self.df.at[name, field]
            if val is not None:
                await ctx.send(f"{name}'s {field} is {val}.")
                return
        await ctx.send(f"{field} not found for: {name}")

    async def set_val(self, ctx, field, value):
        self.df.at[ctx.author.name, field] = value
        await ctx.send(f"Updated {ctx.author.name} with {field}: {value} ")
        self.df.to_csv("./memberInfo.csv")
   
def setup(bot):
    bot.add_cog(Members(bot))

