from discord.ext import commands
import discord
import pandas as pd 
import os.path
from random import randint

CSV_LOC = "./memberInfo.csv"
import asyncio

if not os.path.exists(CSV_LOC):
    d = {'Nickname':[], 'Email': [], 'Venmo': [], 'Playlist' : [], 'Autoplay' : []}
    df = pd.DataFrame(data=d)
    # In .gitignore
    df.to_csv(CSV_LOC, index=False)

df = pd.read_csv(CSV_LOC, index_col='Nickname')

 # Called when user joins Library and Groovy is not already a part of it
async def autoplay_playlist_helper(channel, voice_channel, author, curr_voice_client):
    print("autoplay trying")
    user = author.name
    if user in df.index:
        playlist = df.at[user, 'Playlist']
        autoplay = df.at[user, 'Autoplay']
        if playlist is not None and str(autoplay) == "True":
            print("Playing ", playlist)
            token = randint(1,3)
            if token == 1:
                await channel.send(f"{user} just connected to the library. Let's jam!")
            elif token == 2:
                await channel.send(f"Hooray to {user} for being productive today! Let's get started!")
            else:
                await channel.send(f"Study time for {user}! How about some tunes? :D")

            if curr_voice_client is not None:
                await curr_voice_client.disconnect()

            await play_playlist_helper(channel, voice_channel, user, df)
 
async def play_playlist_helper(channel, voice_channel, user, df):
    print(channel)
    print(voice_channel)
    print(user)

    if user not in df.index or df.at[user, 'Playlist'] is None:
        print("No user registered playlist")
        await channel.send(f"{user} does not have a registered playlist!")
        return
    # If you are in a voice channel
    playlist = df.at[user, 'Playlist']
    print("Connecting to voice channel!")
    await voice_channel.connect()

    await channel.send("Note: Groovy ignores other bots, so please copy/paste the command below:")
    await channel.send(f"-play {playlist}")

class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.df = pd.read_csv("./memberInfo.csv", index_col='Nickname')
        self.invite_delay_hours = 24
        self.live_invites = set()

    @commands.command(name='cancel_invite', help='[admin] Cancel an invite, preventing a link from being generated.')        
    async def cancel_invite(self, ctx, *args):
        # Check the user has permissions to call this function.
        admin_role = discord.utils.get(ctx.guild.roles, name="admin")
        if admin_role not in ctx.author.roles:
            await ctx.send("You need the admin role to run this command!")
            return

        # Prevent the link from being generated.
        user_name = ' '.join(args)
        try:
            self.live_invites.remove(user_name)
        except KeyError:
            await ctx.send(f"'{user_name}' was not being invited. Maybe the spelling/capitalization is off?")
        else:    
            await ctx.send(f"{user_name} is no longer being invited.")

    async def _invite(self, ctx, user_name):
        # Generate an invite link.
        channel = discord.utils.get(ctx.guild.channels, name='welcome')
        custom_link = await channel.create_invite(unique=True)
        print(f"Generated link {custom_link}")
        await ctx.send(f"I'm now inviting {user_name}! <@{ctx.author.id}>, I'll be sending you a custom link to forward to {user_name}")
        await ctx.author.send(f"Here is the link for inviting {user_name}: {custom_link}")
        if user_name in self.live_invites: self.live_invites.remove(user_name)

        # Cache invite information for role assignment logic when the new member joins.
        self.bot.resident_invites.add((ctx.author, custom_link.code))
        if ctx.guild.id not in self.bot.invite_cache:
            self.bot.invite_cache[ctx.guild.id] = {}
        invites = await ctx.guild.invites()
        for invite in invites:
            self.bot.invite_cache[ctx.guild.id][invite.code] = invite
            
    @commands.command(name='invite', help='Propose inviting a certain person')        
    async def begin_invite(self, ctx, *args):
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

        # Handle the actual generation of the invite link.
        await self._invite(ctx, user_name)

    @commands.command(name='rush_invite', help='[admin] Directly generate a link to invite a resident')        
    async def rush_invite(self, ctx, *args):
        """
        Generate a link to invite a resident without a comment period.
        usage: .invite Anna Zeng
        """
        # Check the user has permissions to call this function.
        admin_role = discord.utils.get(ctx.guild.roles, name="admin")
        if admin_role not in ctx.author.roles:
            await ctx.send("You need the admin role to run this command!")
            return

        # Handle the actual generation of the invite link.
        user_name = ' '.join(args)
        await self._invite(ctx, user_name)
        
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

    @commands.command(name='set_playlist', help='Lets Tomi know what playlist you want saved!')
    async def set_playlist(self, ctx, playlist):
        await self.set_val(ctx, "Playlist", playlist)
        await ctx.send("Want Tomi to auto-play your playlist in Library? Do .autoplay_on!")


    @commands.command(name='get_playlist',
                 help='Gets playlists for a member. Use: get_playlist for yourself, get_playlist bob for bob')
    async def get_playlist(self, ctx, *args):
        if len(args) == 0:
            await self.get_val(ctx, "Playlist", ctx.author.name)
        else:
            await self.get_val(ctx, "Playlist", args[0])

    @commands.command(name='play_playlist',
                 help='Gets playlists for a member. Use: get_playlist for your playlist, get_playlist bob for bob playlist')
    async def play_playlist(self, ctx, *args):
        user = ctx.author.name
        if len(args) > 0:
            user = args[1]
        if ctx.author.voice and ctx.author.voice.channel:
            voice_channel = ctx.author.voice.channel
            curr_voice_client = ctx.message.guild.voice_client
            if curr_voice_client is not None:
                await curr_voice_client.disconnect()
            await play_playlist_helper(ctx, voice_channel, user, self.df)
        else:
            await ctx.send("You are not in a voice channel.")
        

    @commands.command(name='autoplay_on',
                 help='Sets autoplay-upon-entry to library to on [note -- does not work right now]')
    async def autoplay_on(self, ctx):
         await self.set_val(ctx, "Autoplay", True)
    
    @commands.command(name='autoplay_off',
                 help='Sets autoplay-upon-entry to library to off [note -- does not work right now]')
    async def autoplay_off(self, ctx):
         await self.set_val(ctx, "Autoplay", False)
    

    async def get_val(self, ctx, field, name):
        if name in self.df.index:
            val = self.df.at[name, field]
            if val is not None:
                await ctx.send(f"{name}'s {field} is {val}.")
                return
        await ctx.send(f"{field} not found for: {name}")

    async def set_val(self, ctx, field, value):
        self.df.loc[ctx.author.name, field] = value
        await ctx.send(f"Updated {ctx.author.name} with {field}: {value} ")
        self.df.to_csv("./memberInfo.csv")

   
def setup(bot):
    bot.add_cog(Members(bot))

