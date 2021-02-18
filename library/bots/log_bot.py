import discord
from discord.ext import commands
import asyncio

from library.managers.file_manager import FileManager, Logs
from library.managers.sql_manager import SQLManager


class LogBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix = "!")
        self.is_logging = True
        self.file_manager = FileManager()
        self.log_batch = self.file_manager.get_entry_keys()
        
    def initalize(self):
        self.load_extension("library.cogs.log_commands")

    def destroy(self):
        self.is_logging = False
        self.loop.get_event_loop().wait_until_complete(asyncio.sleep(1))

    def add_log_entry(self, log_key, entry):
        self.log_batch[log_key].append(entry)

    async def sync_logs(self):
        await self.wait_until_ready()
        while(self.is_logging):
            await asyncio.sleep(3)
            for entry_key in self.log_batch:
                if(len(self.log_batch[entry_key]) > 0):
                    entries = list(self.log_batch[entry_key])
                    await self.file_manager.appendLogs(entry_key, entries)
                    del self.log_batch[entry_key][:len(entries)]

    ### System events  (Use log_entry_key Logs.SYSTEM) ###
    async def on_ready(self):
        user = {'user': "jakob", 'message': "hey"}
        db_manager = SQLManager()
        await db_manager.initalize()
        db_manager.insert_raw_data("user", user)

        print(db_manager.fetch_table_data("user"))

        #self.loop.create_task(self.sync_logs())
        #self.add_log_entry(Logs.SYSTEM, f'{self.user} fully initalized and ready to log')

    async def on_error(self, *args, **kwargs):
        pass

    ### User events (Use log_entry_key Logs.USER) ###
    async def on_message(self, message):
        self.add_log_entry(Logs.USER, f'({message.created_at}) {message.author}: {message.content}')

    async def on_message_delete(self, mesage):
        pass

    async def on_bulk_message_delete(self, messages):
        pass

    async def on_message_edit(self, before, after):
        pass

    async def on_reaction_add(self, reaction, user):
        pass

    async def on_reaction_remove(self, reaction, user):
        pass

    async def on_member_join(self, member):
        pass

    async def on_member_remove(self, member):
        pass

    async def on_member_update(self, before, after):
        pass

    async def on_user_update(self, before, after):
        pass

    ### Moderation events (Use log_entry_key Logs.MOD) ### 
    async def on_reaction_clear(self, message, reactions):
        pass

    async def on_reaction_clear_emoji(self, reaction):
        pass

    async def on_private_channel_update(self, before, after):
        pass

    async def on_private_channel_pins_update(self, channel, last_pin):
        pass

    async def on_guild_channel_update(self, before, after):
        pass

    async def on_guild_channel_pins_update(self, channel, last_pin):
        pass

    async def on_member_ban(self, guild, user):
        pass

    async def on_member_unban(self, guild, user):
        pass

    async def on_invite_create(self, invite):
        pass

    async def on_invite_delete(self, invite):
        pass

    ### Administrative events (Use log_entry_key Logs.ADMIN) ###
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

    async def on_voice_state_update(self, member, before, after):
        pass
