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

    @commands.command()
    async def messages(self, ctx, *argument, member: discord.Member = None):
        member = member or ctx.author
        user = await self.bot.fetch_user(argument[0])
        if(int(argument[1]) <= 10):
            #self.bot.db_manager.find_user(user.id, user.name)
            messages = self.bot.db_manager.select_data(Logs.MESSAGE, "owner", like = argument[0])
            embed = discord.Embed(title = f"Last {argument[1]} messages of {user.name}")
            channel_messages = {}
            for message in messages[:5]:
                if not message['channel'] in channel_messages: channel_messages[message['channel']] = []
                created_at = datetime.datetime.strptime(message['created_at'], "%a %b %d %H:%M:%S %Y")
                channel_messages[message['channel']].append(f"({created_at}) {message['content']}")
            for channel_message in channel_messages:
                embed.add_field(name = channel_message, value = "\n".join(channel_messages[channel_message]), inline = False)
            await ctx.message.channel.send(embed = embed)


def setup(bot):
    bot.add_cog(LogCommands(bot))