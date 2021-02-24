import discord
from discord.ext import commands
from discord.utils import get
import datetime

from library.const.logs import Logs

class LogCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return get(ctx.guild.roles, name = "Staff") in ctx.author.roles
        
    @commands.command()
    async def played(self, ctx, *argument, member: discord.Member = None):
        member = member or ctx.author
        mentions = ctx.message.mentions
        if len(mentions) == 0:
            member_voice_time = self.bot.sync_voice_duration(member)['member']['voice_time']
            await ctx.send(f"User @{member} has been in voice channels for a total of {datetime.timedelta(seconds=member_voice_time)} (HH/MM/SS)")
        elif len(mentions) == 1:
            member_voice_time = self.bot.sync_voice_duration(mentions[0])['member']['voice_time']
            await ctx.send(f"User @{mentions[0]} has been in voice channels for a total of {datetime.timedelta(seconds=member_voice_time)} (HH/MM/SS)")
        elif len(mentions) == 2:
            self.bot.sync_voice_duration(mentions[0])['member']['voice_time']
            self.bot.sync_voice_duration(mentions[1])['member']['voice_time']
            connected_time = self.bot.db_manager.select_data(Logs.VOICE, id = f"{mentions[0].id}-{mentions[1].id}")
            if not 'duration' in connected_time: connected_time['duration'] = 0
            await ctx.send(f"User @{mentions[0]} has played {datetime.timedelta(seconds=connected_time['duration'])} (HH/MM/SS) with @{mentions[1]}")


def setup(bot):
    bot.add_cog(LogCommands(bot))