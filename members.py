from discord.ext import commands
import pandas as pd 
import os.path



if not os.path.exists("./memberInfo.csv"):
    d = {'Nickname':[], 'Email': [], 'Venmo': []};
    df = pd.DataFrame(data=d)
    # In .gitignore
    df.to_csv("./memberInfo.csv", index=False)


class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.df = pd.read_csv("./memberInfo.csv", index_col='Nickname')

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

