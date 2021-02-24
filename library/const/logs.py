import enum

class Logs(enum.Enum):
    USER = 'user'
    ADMIN = 'admin'
    MOD = 'mod'
    SYSTEM = 'system'
    PERSONAL = 'personal'
    MESSAGE = 'message'
    VOICE = 'voice'