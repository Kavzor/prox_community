class BotManager:
    def __init__(self):
        self.bots = []
        self.is_managing = True

    def add(self, bots):
        self.bots = bots

    def initalize(self):
        for bot in self.bots:
            if("initalize" in dir(bot['entity'])):
                bot['entity'].initalize()

            bot['entity'].run(bot['token'])

    def destroy(self):
        for bot in self.bots:
            bot['entity'].destroy()
