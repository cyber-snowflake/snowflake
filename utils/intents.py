from discord import Intents


class MyIntents(Intents):
    def __init__(self):
        super(MyIntents, self).__init__()

        self.guilds = True
        self.members = True
        self.emojis = True
        self.invites = True
        self.voice_states = True
        self.presences = True
        self.messages = True
        self.reactions = True
