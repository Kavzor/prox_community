import enum
import pathlib
import datetime

class Logs(enum.Enum):
    USER = 'user'
    ADMIN = 'admin'
    MOD = 'mod'
    SYSTEM = 'system'

class FileManager:
    def __init__(self):
        self.log_folder = "logs/"
        pathlib.Path(self.log_folder).mkdir(parents = True, exist_ok = True)

    def get_entry_keys(self):
        return {Logs.USER: [], Logs.ADMIN: [], Logs.SYSTEM: [], Logs.MOD: []}

    async def appendLogs(self, log, entries):
        now = datetime.datetime.now()
        dir_path = f'{self.log_folder}{log.value}/{now.year}-{now.month}/'
        pathlib.Path(dir_path).mkdir(parents = True, exist_ok = True)
        try:
            with open(f'{dir_path}{now.day}.txt', "a") as file:
                log_entry = ''
                for entry in entries:
                    log_entry += entry + "\n"

                file.write(log_entry)
        except Exception as err:
            print(err)