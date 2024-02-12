allowed_channels = ["console"]
history = {}

assistant_message = "Pray tell, in what manner may I be of service unto thee on this auspicious day?"

async def add_channel(channel):
    global allowed_channels
    global history
    allowed_channels.append(channel)

    history[channel] = []
    await channel.send(assistant_message)


def get_channel_registered(channel):
    global allowed_channels
    return channel in allowed_channels


def remove_channel(channel):
    global allowed_channels
    global history
    allowed_channels.remove(channel)
    del history[channel]

def append_to_history(channel, content):
    global history
    if len(history[channel]) >= 4:
        history[channel].pop(0)
    history[channel].append(content.strip())

def get_history(channel):
    global history
    return history[channel]
