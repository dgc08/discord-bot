class Context:
    def __init__(self, message):
        self.message = message
        self.send = message.channel.send
