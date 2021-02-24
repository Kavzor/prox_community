import discord
from discord.ext import commands
import asyncio
import datetime

from library.managers.file_manager import FileManager, Logs
from library.managers.sql_manager import SQLManager


class LogBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix = "!")
        self.active_voices = {}
        
    def initalize(self):
        self.load_extension("library.cogs.log_commands")

    #def destroy(self):
        #self.is_logging = False
        #self.loop.get_event_loop().wait_until_complete(asyncio.sleep(1))

    ### System events  (Use log_entry_key Logs.SYSTEM) ###
    async def on_ready(self):
        self.file_manager = FileManager()
        self.db_manager = SQLManager()
        self.db_manager.initalize()
        self.file_manager.initalize()

        self.file_manager.add_log(Logs.SYSTEM, f'{self.user} fully initalized and ready to log')
        print("Fully initalized and ready to rumble")

    def sync_voice_duration(self, member):
        user = self.db_manager.find_user(member.id, member.name)
        if not 'voice_time' in user: user['voice_time'] = 0
        duration = {'member': user, 'connected_voices': []}
        if not(member.voice) or not (str(member.id) in self.active_voices):
            return duration
        
        now = datetime.datetime.now()
        member_voice = self.active_voices[str(member.id)]
        member_joined_at = datetime.datetime.strptime(member_voice['joined_at'], "%a %b %d %H:%M:%S %Y")
        participants = [participant for participant in member.voice.channel.members if not(participant.id == member.id)]

        user['voice_time'] = int((now - member_joined_at).total_seconds()) + user['voice_time']
        
        for participant in participants:
            active_voice_join_time = datetime.datetime.strptime(self.active_voices[str(participant.id)]['joined_at'], "%a %b %d %H:%M:%S %Y")
            entry_id = f"{member.id}-{participant.id}"
            connected_time = self.db_manager.select_data(Logs.VOICE, entry_id)
            if not connected_time:
                connected_time = {'id': entry_id, 'duration': 0}
            connected_time['duration'] = connected_time['duration'] + abs((member_joined_at - active_voice_join_time).total_seconds())
            duration['connected_voices'].append(connected_time)
        
        self.db_manager.set_data(Logs.USER, duration['member'])
        for connected_voice in duration['connected_voices']:
            self.db_manager.set_data(Logs.VOICE, connected_voice)
        return duration

    async def on_error(self, *args, **kwargs):
        pass

    async def on_bulk_message_delete(self, messages):
        for message in messages:
            await self.on_message_delete(message)

    ### User events (Use log_entry_key Logs.USER) ###
    async def on_message(self, message):
        await self.process_commands(message)
        if message.author.bot or message.content[0] == self.command_prefix:
            return False
        user = self.db_manager.find_user(message.author.id, message.author.name)
        user_message = {
            'content': message.content, 
            'created_at': message.created_at.ctime(), 
            'channel': message.channel.name,
            'id': message.id,
            'owner': message.author.id
        }
        entry = f'SENT_M: ({message.created_at}) {message.author.name}: {message.content}'
        self.file_manager.add_log(Logs.PERSONAL, entry, owner = message.author.name)
        self.db_manager.set_data(Logs.MESSAGE, user_message)

    async def on_message_delete(self, message):
        now = datetime.datetime.now()
        user_message = self.db_manager.select_data(Logs.MESSAGE, message.id)
        user_message['deleted_at'] = now.ctime()
        entry = f'DELETED_M: ({message.created_at}) {message.author.name}: {message.content}'
        self.file_manager.add_log(Logs.PERSONAL, entry, owner = message.author.name)
        self.db_manager.set_data(Logs.MESSAGE, user_message)

    async def on_message_edit(self, before, after):
        entry = f'EDITED_M: \n\t BEFORE: ({before.created_at}) {before.author.name}: {before.content} \n\t AFTER: ({after.created_at}) {after.author.name}: {after.content}'
        self.file_manager.add_log(Logs.PERSONAL, entry, owner = before.author.name)

    async def on_reaction_add(self, reaction, user):
        entry = f'ADDED_R: {user.name} reacted {reaction.emoji.name} to {reaction.message.content} by {reaction.message.author.name}'
        self.file_manager.add_log(Logs.PERSONAL, entry, owner = user.name)

    async def on_reaction_remove(self, reaction, user):
        entry = f'REMOVED_R: {user.name} removed reaction {reaction.emoji.name} to {reaction.message.content} by {reaction.message.author.name}'
        self.file_manager.add_log(Logs.PERSONAL, entry, owner = user.name)

    async def on_member_join(self, member):
        user = self.db_manager.find_user(member.id, member.name)
        user['joined_at'] = member.joined_at.ctime()
        entry = f'JOINED_M: {member.name} joined'
        self.file_manager.add_log(Logs.PERSONAL, entry, owner = member.name)
        self.db_manager.set_data(Logs.USER, user)

    async def on_member_remove(self, member):
        user = self.db_manager.find_user(member.id, member.name)
        user['removed_at'] = datetime.datetime.now().ctime()
        entry = f'REMOVED_M: {member.name} got removed'
        self.file_manager.add_log(Logs.PERSONAL, entry, owner = member.name)
        self.db_manager.set_data(Logs.USER, user)

    async def on_voice_state_update(self, member, before, after):
        now = datetime.datetime.now()
        entries = []
        if before.channel:
            entries.append(f'VOICE_LEFT: {member.name} left voicechannel {before.channel.name}')
            self.sync_voice_duration(member)
            del self.active_voices[str(member.id)]
        if after.channel:
            entries.append(f'VOICE_JOINED: {member.name} joined voicechannel {after.channel.name}')
            self.active_voices[str(member.id)] = {
                'joined_at': now.ctime(),
                'channel_id': after.channel.id,
                'channel_name': after.channel.name
            }

        if before.afk:
            entries.append(f'VOICE_AFK: {member.name} went afk')
        if after.afk:
            entries.append(f'VOICE_AFK_B: {member.name} came back from afk')

        if before.deaf:
            entries.append(f'VOICE_DEAF_M: {member.name} deafend in {before.channel.name} by moderator')
        if after.deaf:
            entries.append(f'VOICE_UNDEAF_M: {member.name} un-deafend in {after.channel.name} by moderator')

        if before.mute:
            entries.append(f'VOICE_MUTE_M: {member.name} muted in {before.channel.name} by moderator')
        if after.mute:
            entries.append(f'VOICE_UNMUTE_M: {member.name} unmuted in {before.channel.name} by moderator')

        if before.self_deaf:
            entries.append(f'VOICE_DEAF_S: {member.name} self-deafend in {before.channel.name}')
        if after.self_deaf:
            entries.append(f'VOICE_UNDEAF_S: {member.name} self-undeafend in {after.channel.name}')

        if before.self_mute:
            entries.append(f'VOICE_MUTE_S: {member.name} self-muted in {before.channel.name}')
        if after.self_mute:
            entries.append(f'VOICE_UNMUTE_S: {member.name} self-unmuted in {after.channel.name}')

        if before.self_stream:
            entries.append(f'STREAM_START: {member.name} started streaming in {before.channel.name}')
        if after.self_stream:
            entries.append(f'STREAM_END: {member.name} stopped streaming in {after.channel.name}')

        if before.self_video:
            entries.append(f'VIDEO_START: {member.name} started video in {before.channel.name}')
        if after.self_video:
            entries.append(f'VIDEO_END: {member.name} stopped video in {after.channel.name}')

        self.file_manager.add_multiple(Logs.PERSONAL, entries, owner = member.name)

    async def on_member_update(self, before, after):
        entries = []
        if not (before.status == after.status):
            entries.append(f'STATUS: {before.name} changed status from {before.status.name} to {after.status.name}')

        if not (before.activity == after.activity):
            entries.append(f'ACTIVITY: {before.name} changed activity from {before.activity.name} to {after.activity.name}')

        if not (before.nickname == after.nickname):
            entries.append(f'NICKNAME: {before.name} changed nickname from {before.nickname} to {after.nickname}')

        if not (before.roles == after.roles):
            entries.append(f'ROLES: {before.name} changed roles from ({",".join(before.roles)}) to ({",".after.roles})')

        #if not (before.pending == after.pending):
            #entries.append(f'VERIF_P: {before.name} changed status from {before.status.name} to {after.status.name}')

        self.file_manager.add_multiple(Logs.PERSONAL, entries, owner = before.name)

    async def on_user_update(self, before, after):
        entries = []
        if not (before.avatar == after.avatar):
            entries.append(f'AVATAR: {before.name} changed avatar from {before.avatar} to {after.avatar}')

        if not (before.username == after.username):
            entries.append(f'USERNAME: {before.name} changed username from {before.username} to {after.username}')

        if not (before.discriminator == after.discriminator):
            entries.append(f'DISCRIMINATOR: {before.name} conflicts {before.discriminator} with {after.discriminator}')

        self.file_manager.add_multiple(Logs.PERSONAL, entries, owner = before.name)

    ### Moderation events (Use log_entry_key Logs.MOD) ### 
    async def on_reaction_clear(self, message, reactions):
        entry = f'REACTION_CLEAR: message {message.content} by {message.author.name} had reactions {",".join(map(lambda reaction: reaction.emoji.name, reactions))} cleared'
        self.file_manager.add_log(Logs.MOD, entry)

    async def on_reaction_clear_emoji(self, reaction):
        entry = f'EMOJI_CLEAR: message {reaction.message.content} by {reaction.message.author.name} had reaction {reaction.emoji.name} cleared'
        self.file_manager.add_log(Logs.MOD, entry)
    
    """
    async def on_private_channel_update(self, before, after):
        entry = f''
        self.file_manager.add_log(Logs.MOD, entry)

    async def on_private_channel_pins_update(self, channel, last_pin):
        entry = f''
        self.file_manager.add_log(Logs.MOD, entry)

    async def on_guild_channel_update(self, before, after):
        entry = f''
        self.file_manager.add_log(Logs.MOD, entry)

    async def on_guild_channel_pins_update(self, channel, last_pin):
        entry = f''
        self.file_manager.add_log(Logs.MOD, entry)
    """

    async def on_member_ban(self, guild, user):
        user = self.db_manager.find_user(user.id, user.name)
        if not user['banned_times']:
            user['banned_times'] = 0
        user['banned_times'] += 1
        entry = f'USER_BAN: {user.name} got banned'
        self.file_manager.add_log(Logs.PERSONAL, entry, owner = user.name)
        self.file_manager.add_log(Logs.MOD, entry)
        self.db_manager.set_data(Logs.USER, user)

    async def on_member_unban(self, guild, user):
        user = self.db_manager.find_user(user.id, user.name)
        if not user['unbanned_times']:
            user['unbanned_times'] = 0
        user['unbanned_times'] += 1
        entry = f'USER_UNBAN: {user.name} got unbanned'
        self.file_manager.add_log(Logs.PERSONAL, entry, owner = user.name)
        self.file_manager.add_log(Logs.MOD, entry)
        self.db_manager.set_data(Logs.USER, user)

    async def on_invite_create(self, invite):
        entry = f'INVITE_C: invite {invite.url} was created by {invite.inviter}'
        self.file_manager.add_log(Logs.MOD, entry)

    async def on_invite_delete(self, invite):
        entry = f'INVITE_D: invite {invite.url} was deleted by {invite.inviter}'
        self.file_manager.add_log(Logs.MOD, entry)

    ### Administrative events (Use log_entry_key Logs.ADMIN) ###
    """
    async def on_private_channel_create(self, channel):
        pass

    async def on_private_channel_delete(self, channel):
        pass
    
    async def on_guild_channel_create(self, channel):
        pass

    async def on_guild_channel_delete(self, channel):
        pass

    async def on_guild_update(self, before, after):
        pass

    async def on_guild_role_create(self, role):
        pass

    async def on_guild_role_delete(self, role):
        pass

    async def on_guild_role_update(self, before, after):
        pass

    async def on_guild_emojis_update(self, guild, before, after):
        pass
    """