from pysondb import db
import asyncio

class PysonManager:
    def __init__(self):
        self.data_batch = []
        self.is_running = True
        self.batch_sync_completed = False
        self.db_connection = db.getDb("user_prox_chat_db.json")

    async def initalize(self):
        asyncio.create_task(self.sync_database())

    def insert_data(self, data):
        self.data_batch.append(data)

    def destroy(self):
        self.is_running = False
        while(not self.batch_sync_completed):
            asyncio.sleep(1)
        self.db_connection.close()

    async def sync_database(self):
        while(self.is_running):
            if(len(self.data_batch) > 0):
                entries = list(self.data_batch)
                print(entries)
                self.db_connection.addMany(entries)
                del self.data_batch[:len(entries)]
            await asyncio.sleep(10)
        self.batch_sync_completed = True
