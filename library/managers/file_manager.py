import enum
import pathlib
import datetime

from library.managers.task_manager import TaskManager
from library.const.logs import Logs

class FileManager(TaskManager):
    def __init__(self):
        super().__init__()
        self.log_folder = "logs/"
        pathlib.Path(self.log_folder).mkdir(parents = True, exist_ok = True)
        self.log_batch = {}

    def initalize(self):
        self.create_task(5, self.sync_logs, "log_thread")

    def add_multiple(self, log, entries, owner = "SYSTEM"):
        for entry in entries:
            self.add_log(log, entry, owner)

    def add_log(self, log, entry, owner = "SYSTEM"):
        if owner == Logs.PERSONAL.value:
            self.add_log(Logs.USER, entry)
        if not (log.value in self.log_batch):
            self.log_batch[log.value] = {'owner': owner, 'entries': []}
        self.log_batch[log.value]['entries'].append(entry)

    async def sync_logs(self):
        for log in self.log_batch:
            if log in self.log_batch and len(self.log_batch[log]['entries']) > 0:
                queries = list(self.log_batch[log]['entries'])
                await self.appendLogs(log, queries, self.log_batch[log]['owner'])
                del self.log_batch[log]['entries'][:len(queries)]

    async def appendLogs(self, log, entries, owner):
        now = datetime.datetime.now()
        path = f'{self.log_folder}{log}'
        path += log == Logs.PERSONAL.value and "/" or f'/{now.year}-{now.month}/'
        pathlib.Path(path).mkdir(parents = True, exist_ok = True)
        path += log == Logs.PERSONAL.value and str(owner) or str(now.day)
        try:
            with open(f'{path}.txt', "a") as file:
                log_entry = ''
                for entry in entries:
                    log_entry += entry + "\n"

                file.write(log_entry)
                file.close()
        except Exception as err:
            print(err)
