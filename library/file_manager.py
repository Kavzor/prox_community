import enum

class Logs(enum.Enum):
    USER = 'user'
    ADMIN = 'admin'
    MOD = 'mod'
    SYSTEM = 'system'

class FileManager:
    def __init__(self):
        self.log_folder = "logs/"

    def get_entry_keys(self):
        return {Logs.USER: [], Logs.ADMIN: [], Logs.SYSTEM: [], Logs.MOD: []}

    def appendLogs(self, log, entries):
        try:
            with open(self.log_folder + log + ".txt", "a") as file:
                log_entry = ''
                for entry in entries:
                    log_entry += entry + "\n"

                file.write(log_entry)
        except Exception as err:
            print(err)