import sqlite3
import asyncio
import json

class SQLManager:
    def __init__(self):
        self.sql_batch = []
        self.is_running = True
        self.batch_sync_completed = False
        self.db_connection = sqlite3.connect("db_user_logs")

    async def initalize(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS user (id varchar(32), data json)")
            cursor.close()
        except sqlite3.Error as e:
            print(e)

        asyncio.create_task(self.sync_database())

    def insert_data(self, table, data):
        query = f"insert into {table} values ("
        for key in data:
            query += data[key] + ","
        query = query[:-1] + ")"
        self.sql_batch.append(query)

    def insert_raw_data(self, table, data):
        self.sql_batch.append({"table": table, "data": json.dumps(data)})

    def destroy(self):
        self.is_running = False
        while(not self.batch_sync_completed):
            asyncio.sleep(1)
        self.db_connection.close()

    def fetch_table_data(self, table):
        data = []
        try: 
            cursor = self.db_connection.cursor()
            cursor.execute(f"SELECT * FROM '{table}'")
            rows = cursor.fetchall()
            print(rows)
            for row in rows:
                data.append(json.loads(row))

            cursor.close()   
        except sqlite3.Error as e:
            print(e)
        return data

    async def sync_database(self):
        while(self.is_running):
            if(len(self.sql_batch) > 0):
                entries = list(self.sql_batch)
                try: 
                    cursor = self.db_connection.cursor()
                    for entry in entries:
                        cursor.execute(f"insert into {entry['table']} values (?,?)", [1, entry['data']])
                    self.db_connection.commit()
                    cursor.close()
                    del self.sql_batch[:len(entries)]
                except sqlite3.Error as e:
                    print(e)
            await asyncio.sleep(10)
        self.batch_sync_completed = True
