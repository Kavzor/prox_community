import discord
from discord.ext import commands

class LogCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def fetch(self, ctx):
        await ctx.send("unable to fetch any data at the moment")

def setup(bot):
    bot.add_cog(LogCommands(bot))