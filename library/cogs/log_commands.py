import discord
from discord.ext import commands
from discord.utils import get

class LogCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return get(ctx.guild.roles, name = "Admin") in ctx.author.roles
        
    @commands.command()
    async def fetch(self, ctx):
        await ctx.send("unable to fetch any data at the moment")

def setup(bot):
    bot.add_cog(LogCommands(bot))