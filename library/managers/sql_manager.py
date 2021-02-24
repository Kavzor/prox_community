import sqlite3
import asyncio
import json
import re
import os

from library.const.logs import Logs
from library.managers.task_manager import TaskManager

class SQLManager(TaskManager):
    def __init__(self):
        super().__init__()
        self.sql_batch = []
        self.db_connection = sqlite3.connect("logs/db_logs")
        self.log_sqls = os.getenv("SHOW_SQL_QUERIES")

    def initalize(self):
        try:
            cursor = self.db_connection.cursor()
            for table in list(Logs):
                cursor.execute(f'CREATE TABLE IF NOT EXISTS {table.value} (id varchar(32), data json)')
            cursor.close()
        except sqlite3.Error as e:
            print(e)
        self.create_task(5, self.sync_database, "db_thread")

    def set_data(self, table, data):
        self.sql_batch.append({"table": table.value, "data": data})

    def __paramatize_json_query(self, params):
        return "".join(map(lambda var: f",'$.{var}'", params))

    def __query_cache(self, table, params, id):
        data = {}
        if id is None:
            return data
        temp_cache = list(self.sql_batch)
        for entry in temp_cache:
            if entry['table'] == table and entry['data']['id'] == id:
                for param in params:
                    if param in entry['data']:
                        data[param] = entry['data'][param]
                    else:
                        return data
        return data

    def find_user(self, id, name):
        user = self.select_data(Logs.USER, id = id)
        if not user:
            user = {'id': id, 'name': name}
        return user

    def select_data(self, table, *params, id = None):
        table = table.value
        data = self.__query_cache(table, params, id)
        if data:
            return data

        sql_query = params and f"SELECT json_extract(data{self.__paramatize_json_query(params)}) from {table}" or f"SELECT data FROM {table}"
        sql_query = id is None and sql_query or sql_query + f" WHERE id = '{id}'"
        if self.log_sqls: print(sql_query)
        try:
            cursor = self.db_connection.cursor()
            data = cursor.execute(sql_query).fetchall()
            data = params and (len(params) == 1 and [dict(zip(params, entry)) for entry in data] or [dict(zip(params, json.loads(entry[0]))) for entry in data]) or [json.loads(entry[0]) for entry in data]
            cursor.close()
        except sqlite3.Error as e:
            print(e)
        return id is not None and data and data[0] or len(data) == 0 and {}

    def destroy(self):
        super().destroy()
        self.db_connection.close()

    async def sync_database(self):
        if(len(self.sql_batch) > 0):
            entries = list(self.sql_batch)
            try: 
                cursor = self.db_connection.cursor()
                for entry in entries:
                    data = json.dumps(entry['data'])
                    matches = re.findall(r'"\w*":', data)
                    for match in matches:
                        data = data.replace(match, f'"$.{match}"').replace('$."', '$.').replace('":"', '",').replace('{', '').replace('}', '')
                    if entry['data']['id']:
                        sql_query = f"UPDATE {entry['table']} SET data = JSON_SET(data, {data}) WHERE id = '{entry['data']['id']}'"
                        rs = cursor.execute(sql_query)
                        if rs.rowcount == 0:
                            data = str(dict(zip(entry['data'].keys(), entry['data'].values()))).replace(':', ',').replace('{', '').replace(':', ',').replace('}', '')
                            sql_query = f"INSERT INTO {entry['table']} VALUES ({entry['data']['id']}, JSON_OBJECT({data}))"
                            rs = cursor.execute(sql_query)
                        if self.log_sqls: print(sql_query)
                    else:
                        data = str(dict(zip(entry['data'].keys(), entry['data'].values()))).replace(':', ',').replace('{', '').replace(':', ',').replace('}', '')
                        sql_query = f"INSERT INTO {entry['table']} (data) VALUES (JSON_OBJECT({data}))"
                        rs = cursor.execute(sql_query)
                        if self.log_sqls: print(sql_query)
                self.db_connection.commit()
                cursor.close()
                del self.sql_batch[:len(entries)]
            except sqlite3.Error as e:
                print(e)
