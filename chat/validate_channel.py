import discord

from chat.History_Service import get_channel_registered


def check_chat(message):
    channel = message.channel
    if message.content.endswith("stop_chat"):
        return False

    if isinstance(channel, discord.DMChannel):
        return True
    if get_channel_registered(channel):
        return True
