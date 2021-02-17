class BotManager:
    def __init__(self):
        self.bots = []
        self.is_managing = True

    def add_bots(self, bots):
        self.bots = bots

    def initalize_bots(self):
        for bot in self.bots:
            if("initalize" in dir(bot['entity'])):
                bot['entity'].initalize()

            bot['entity'].run(bot['token'])

    def destroy_bots(self):
        for bot in self.bots:
            bot['entity'].destroy()
    
    def destroy(self):
        self.destroy_bots()
        self.is_managing = False
